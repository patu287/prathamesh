#!/usr/bin/env python3
"""
Assemble + sign an APK without the Android SDK's apkbuilder/apksigner.

- rebuilds the zip so resources.arsc is STORED and 4-byte aligned (required for
  apps targeting API 30+)
- v1 (JAR) signature: META-INF/MANIFEST.MF + CERT.SF + CERT.RSA
- v2 signature: APK Signature Scheme v2 block (required by Android 11+ for
  apps targeting API 30+)
"""
import hashlib, io, os, struct, sys, zipfile, base64, datetime

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

ALIGN = 4
STORE_EXT = (".arsc", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".so", ".ogg", ".mp3", ".wav")


# ---------------------------------------------------------------- zip writing
class ZipWriter:
    def __init__(self):
        self.buf = io.BytesIO()
        self.entries = []

    def add(self, name, data, store=False, align=ALIGN):
        nb = name.encode("utf-8")
        crc = zipfile.crc32(data) & 0xFFFFFFFF
        if store:
            comp = data
            method = 0
        else:
            import zlib
            co = zlib.compressobj(9, zlib.DEFLATED, -15)
            comp = co.compress(data) + co.flush()
            method = 8

        extra = b""
        if store and align:
            base = self.buf.tell() + 30 + len(nb)
            need = (align - (base % align)) % align
            if need:
                need += align  # room for the 4-byte extra-field header
                extra = struct.pack("<HH", 0xD935, need - 4) + b"\x00" * (need - 4)

        offset = self.buf.tell()
        self.buf.write(struct.pack("<IHHHHHIIIHH", 0x04034B50, 20, 0, method, 0, 0x21,
                                   crc, len(comp), len(data), len(nb), len(extra)))
        self.buf.write(nb)
        self.buf.write(extra)
        self.buf.write(comp)
        self.entries.append((nb, method, crc, len(comp), len(data), offset))

    def finish(self):
        cd_offset = self.buf.tell()
        cd = io.BytesIO()
        for nb, method, crc, csize, usize, offset in self.entries:
            cd.write(struct.pack("<IHHHHHHIIIHHHHHII", 0x02014B50, 20, 20, 0, method, 0, 0x21,
                                 crc, csize, usize, len(nb), 0, 0, 0, 0, 0, offset))
            cd.write(nb)
        cdb = cd.getvalue()
        self.buf.write(cdb)
        self.buf.write(struct.pack("<IHHHHIIH", 0x06054B50, 0, 0,
                                   len(self.entries), len(self.entries), len(cdb), cd_offset, 0))
        return self.buf.getvalue()


# ------------------------------------------------------------- v1 JAR signing
def wrap(line: bytes) -> bytes:
    """Manifest lines must be <= 72 bytes; continuations start with a space."""
    out = line[:72]
    rest = line[72:]
    while rest:
        out += b"\r\n " + rest[:71]
        rest = rest[71:]
    return out + b"\r\n"


def b64(d):
    return base64.b64encode(d)


def v1_sign(files, key, cert):
    """files: list of (name, data). Returns MANIFEST.MF, CERT.SF, CERT.RSA bytes."""
    main = wrap(b"Manifest-Version: 1.0") + wrap(b"Created-By: 1.0 (Reset APK builder)") + b"\r\n"
    sections = []
    for name, data in files:
        sec = wrap(b"Name: " + name.encode()) + \
              wrap(b"SHA-256-Digest: " + b64(hashlib.sha256(data).digest())) + b"\r\n"
        sections.append((name, sec))
    manifest = main + b"".join(s for _, s in sections)

    sf_main = wrap(b"Signature-Version: 1.0") + \
        wrap(b"Created-By: 1.0 (Reset APK builder)") + \
        wrap(b"SHA-256-Digest-Manifest-Main-Attributes: " + b64(hashlib.sha256(main).digest())) + \
        wrap(b"SHA-256-Digest-Manifest: " + b64(hashlib.sha256(manifest).digest())) + b"\r\n"
    sf = sf_main + b"".join(
        wrap(b"Name: " + name.encode()) +
        wrap(b"SHA-256-Digest: " + b64(hashlib.sha256(sec).digest())) + b"\r\n"
        for name, sec in sections)

    from cryptography.hazmat.primitives.serialization import pkcs7
    p7 = (pkcs7.PKCS7SignatureBuilder()
          .set_data(sf)
          .add_signer(cert, key, hashes.SHA256())
          .sign(serialization.Encoding.DER,
                [pkcs7.PKCS7Options.DetachedSignature,
                 pkcs7.PKCS7Options.Binary,
                 pkcs7.PKCS7Options.NoAttributes]))
    return manifest, sf, p7


# ------------------------------------------------- v2 APK Signature Scheme v2
MAGIC = b"APK Sig Block 42"
V2_ID = 0x7109871A
SIG_ALGO_RSA_SHA256 = 0x0103
CHUNK = 1024 * 1024


def lp(data: bytes) -> bytes:
    """uint32-length-prefixed blob"""
    return struct.pack("<I", len(data)) + data


def chunked_digest(sections):
    chunks = []
    for sec in sections:
        for i in range(0, len(sec), CHUNK):
            chunks.append(sec[i:i + CHUNK])
    out = hashlib.sha256()
    out.update(b"\x5a" + struct.pack("<I", len(chunks)))
    for c in chunks:
        h = hashlib.sha256()
        h.update(b"\xa5" + struct.pack("<I", len(c)) + c)
        out.update(h.digest())
    return out.digest()


def v2_sign(apk: bytes, key, cert) -> bytes:
    # locate End Of Central Directory
    eocd_off = apk.rfind(b"PK\x05\x06")
    if eocd_off < 0:
        raise SystemExit("no EOCD")
    eocd = bytearray(apk[eocd_off:])
    cd_size = struct.unpack_from("<I", eocd, 12)[0]
    cd_off = struct.unpack_from("<I", eocd, 16)[0]

    contents = apk[:cd_off]
    cd = apk[cd_off:cd_off + cd_size]

    digest = chunked_digest([contents, cd, bytes(eocd)])

    cert_der = cert.public_bytes(serialization.Encoding.DER)
    digests = lp(struct.pack("<I", SIG_ALGO_RSA_SHA256) + lp(digest))
    certs = lp(cert_der)
    signed_data = lp(digests) + lp(certs) + lp(b"")          # no additional attributes

    signature = key.sign(signed_data, padding.PKCS1v15(), hashes.SHA256())
    signatures = lp(struct.pack("<I", SIG_ALGO_RSA_SHA256) + lp(signature))
    pubkey = cert.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)

    signer = lp(signed_data) + lp(signatures) + lp(pubkey)
    # the signers sequence is itself length-prefixed, and so is each signer in it
    v2_value = lp(lp(signer))

    pair = struct.pack("<Q", 4 + len(v2_value)) + struct.pack("<I", V2_ID) + v2_value
    # pad so the whole signing block is a multiple of 4096 (matches zipalign -p style)
    body = pair
    size = len(body) + 8 + 16                                # + trailing size + magic
    pad = (4096 - ((size + 8) % 4096)) % 4096                # + leading size field
    if pad:
        if pad < 12:
            pad += 4096
        body += struct.pack("<Q", pad - 8) + struct.pack("<I", 0x42726577) + b"\x00" * (pad - 12)
    block_size = len(body) + 8 + 16                          # trailing size + magic
    block = struct.pack("<Q", block_size) + body + struct.pack("<Q", block_size) + MAGIC

    struct.pack_into("<I", eocd, 16, cd_off + len(block))    # CD moved by block length
    return contents + block + cd + bytes(eocd)


# ------------------------------------------------------------------- key/cert
def make_key(path_key, path_cert):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"Reset"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Reset"),
    ])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (x509.CertificateBuilder()
            .subject_name(name).issuer_name(name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(days=1))
            .not_valid_after(now + datetime.timedelta(days=365 * 30))
            .sign(key, hashes.SHA256()))
    with open(path_key, "wb") as f:
        f.write(key.private_bytes(serialization.Encoding.PEM,
                                  serialization.PrivateFormat.PKCS8,
                                  serialization.NoEncryption()))
    with open(path_cert, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    return key, cert


def load_key(path_key, path_cert):
    key = serialization.load_pem_private_key(open(path_key, "rb").read(), password=None)
    cert = x509.load_pem_x509_certificate(open(path_cert, "rb").read())
    return key, cert


# ------------------------------------------------------------------- assemble
def main():
    base_apk, dex, out, keydir = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    os.makedirs(keydir, exist_ok=True)
    kp, cp = os.path.join(keydir, "reset.key.pem"), os.path.join(keydir, "reset.cert.pem")
    key, cert = load_key(kp, cp) if os.path.exists(kp) else make_key(kp, cp)

    files = []
    with zipfile.ZipFile(base_apk) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            files.append((info.filename, z.read(info.filename)))
    files.append(("classes.dex", open(dex, "rb").read()))
    files.sort(key=lambda f: (f[0] != "AndroidManifest.xml", f[0]))

    manifest, sf, p7 = v1_sign(files, key, cert)

    zw = ZipWriter()
    for name, data in files:
        zw.add(name, data, store=name.endswith(STORE_EXT))
    zw.add("META-INF/MANIFEST.MF", manifest)
    zw.add("META-INF/CERT.SF", sf)
    zw.add("META-INF/CERT.RSA", p7, store=True)
    unsigned = zw.finish()

    signed = v2_sign(unsigned, key, cert)
    with open(out, "wb") as f:
        f.write(signed)
    print("wrote", out, len(signed), "bytes")


if __name__ == "__main__":
    main()
