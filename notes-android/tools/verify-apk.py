#!/usr/bin/env python3
"""Independently verify the Notes APK: v1 + v2 signatures, alignment, dex.

Written from the APK Signature Scheme v2 spec + RFC 2315, not from mkapk.py,
so a bug in the signer cannot hide behind the same bug here.
"""
import base64, hashlib, io, struct, sys, zipfile

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import pkcs7

APK = sys.argv[1] if len(sys.argv) > 1 else "notes/release/Notes-1.0.apk"
CERT_PEM = sys.argv[2] if len(sys.argv) > 2 else "notes-android/keys/notes.cert.pem"

raw = open(APK, "rb").read()
ok_all = True


def check(cond, msg, detail=""):
    global ok_all
    ok_all = ok_all and bool(cond)
    print(("  PASS  " if cond else "  FAIL  ") + msg + (("  " + detail) if detail else ""))


# ------------------------------------------------------------------ tiny DER
def tlv(buf, off):
    """-> (tag, content_off, content_len, next_off)"""
    tag = buf[off]
    ln = buf[off + 1]
    hdr = 2
    if ln & 0x80:
        n = ln & 0x7F
        ln = int.from_bytes(buf[off + 2:off + 2 + n], "big")
        hdr = 2 + n
    return tag, off + hdr, ln, off + hdr + ln


def children(buf, off, end):
    out, p = [], off
    while p < end:
        tag, c_off, c_len, nxt = tlv(buf, p)
        out.append((tag, p, c_off, c_len, nxt))
        p = nxt
    return out


def oid_str(buf, c_off, c_len):
    b = buf[c_off:c_off + c_len]
    parts = [b[0] // 40, b[0] % 40]
    val = 0
    for x in b[1:]:
        val = (val << 7) | (x & 0x7F)
        if not x & 0x80:
            parts.append(val)
            val = 0
    return ".".join(str(p) for p in parts)


print(f"--- {APK}  ({len(raw)} bytes) ---")

# ---------------------------------------------------------------- v1 (JAR)
print("v1 (JAR) signature:")
try:
    z = zipfile.ZipFile(io.BytesIO(raw))
    names = z.namelist()
    manifest = z.read("META-INF/MANIFEST.MF")
    cert_sf = z.read("META-INF/CERT.SF")
    cert_rsa = z.read("META-INF/CERT.RSA")
    check(True, "MANIFEST.MF + CERT.SF + CERT.RSA present")

    sections, cur = {}, None
    for line in manifest.split(b"\r\n"):
        if line.startswith(b"Name: "):
            cur = line[6:].decode()
            sections[cur] = {}
        elif b": " in line and cur:
            k, v = line.split(b": ", 1)
            sections[cur][k.decode()] = v.decode()
    missing = [n for n in names if not n.startswith("META-INF/") and n not in sections]
    bad = [n for n in sections if hashlib.sha256(z.read(n)).digest() !=
           base64.b64decode(sections[n].get("SHA-256-Digest", ""))]
    check(not missing, f"MANIFEST.MF covers all {len(names) - 3} payload entries",
          f"missing={missing[:3]}")
    check(not bad, "every payload entry matches its MANIFEST.MF SHA-256 digest",
          f"bad={bad[:3]}")

    sf = {}
    for line in cert_sf.split(b"\r\n"):
        if b": " in line:
            k, v = line.split(b": ", 1)
            sf[k.decode()] = v.decode()
    check(base64.b64decode(sf.get("SHA-256-Digest-Manifest", "")) ==
          hashlib.sha256(manifest).digest(), "CERT.SF digests MANIFEST.MF")

    # walk PKCS#7 SignedData down to the raw signature + signed attributes
    tag, c_off, c_len, _ = tlv(cert_rsa, 0)
    ci = children(cert_rsa, c_off, c_off + c_len)
    check(oid_str(cert_rsa, ci[0][2], ci[0][3]) == "1.2.840.113549.1.7.2",
          "CERT.RSA content type is signedData")
    sd_tag, sd_off, sd_len, _ = tlv(cert_rsa, ci[1][2])
    sd = children(cert_rsa, sd_off, sd_off + sd_len)
    sig_infos = [c for c in sd if c[0] == 0x31][-1]
    signer = children(cert_rsa, sig_infos[2], sig_infos[2] + sig_infos[3])[0]
    parts = children(cert_rsa, signer[2], signer[2] + signer[3])
    signed_attrs = [p for p in parts if p[0] == 0xA0]
    sig_tlv = [p for p in parts if p[0] == 0x04][-1]
    sig = cert_rsa[sig_tlv[2]:sig_tlv[2] + sig_tlv[3]]

    if signed_attrs:
        # attributes are signed as an explicit SET (their implicit [0] tag re-encoded)
        sa = signed_attrs[0]
        hdr = cert_rsa[sa[1]:sa[2]]
        to_sign = b"\x31" + hdr[1:] + cert_rsa[sa[2]:sa[2] + sa[3]]
        what = "the signed attributes"
    else:
        # detached CMS with no attributes: the signature covers the content itself
        to_sign = cert_sf
        what = "CERT.SF directly (no signed attributes)"

    certs = pkcs7.load_der_pkcs7_certificates(cert_rsa)
    check(len(certs) == 1, "CERT.RSA carries exactly one certificate")
    if certs:
        try:
            certs[0].public_key().verify(sig, to_sign, padding.PKCS1v15(), hashes.SHA256())
            verified = True
            err = ""
        except Exception as e:                       # noqa: BLE001
            verified, err = False, f"{type(e).__name__}: {e}"
        check(verified, f"CERT.RSA signature verifies over {what}", err)
        check(certs[0].public_bytes(serialization.Encoding.DER) ==
              x509.load_pem_x509_certificate(open(CERT_PEM, "rb").read())
              .public_bytes(serialization.Encoding.DER),
              "CERT.RSA certificate == keys/notes.cert.pem")

    md = None
    for sa in signed_attrs:
        for a in children(cert_rsa, sa[2], sa[2] + sa[3]):
            akid = children(cert_rsa, a[2], a[2] + a[3])
            if oid_str(cert_rsa, akid[0][2], akid[0][3]) == "1.2.840.113549.1.9.4":
                s = children(cert_rsa, akid[1][2], akid[1][2] + akid[1][3])[0]
                md = cert_rsa[s[2]:s[2] + s[3]]
    if md is not None:
        check(md == hashlib.sha256(cert_sf).digest(),
              "signed messageDigest attribute == SHA-256(CERT.SF)")
except Exception as e:  # noqa: BLE001
    check(False, f"v1 verification crashed: {type(e).__name__}: {e}")

# ---------------------------------------------------------------- v2 block
print("v2 (APK Signature Scheme) block:")
try:
    eocd_off = raw.rfind(b"PK\x05\x06")
    cd_size = struct.unpack_from("<I", raw, eocd_off + 12)[0]
    cd_off = struct.unpack_from("<I", raw, eocd_off + 16)[0]
    check(cd_off + cd_size == eocd_off, "EOCD central-directory offset is consistent")

    MAGIC = b"APK Sig Block 42"
    check(raw[cd_off - 16:cd_off] == MAGIC, "signing block magic sits right before the CD")
    blk_size = struct.unpack_from("<Q", raw, cd_off - 24)[0]
    blk_start = cd_off - blk_size - 8
    check(struct.unpack_from("<Q", raw, blk_start)[0] == blk_size,
          "leading and trailing block-size fields agree", f"size={blk_size}")

    pairs, p = {}, blk_start + 8
    while p < cd_off - 24:
        ln = struct.unpack_from("<Q", raw, p)[0]
        pairs[struct.unpack_from("<I", raw, p + 8)[0]] = raw[p + 12:p + 8 + ln]
        p += 8 + ln
    check(0x7109871A in pairs, "v2 signer block (id 0x7109871a) present",
          f"ids={[hex(i) for i in pairs]}")

    def lp(buf, off=0):
        n = struct.unpack_from("<I", buf, off)[0]
        return buf[off + 4:off + 4 + n], off + 4 + n

    signers, _ = lp(pairs[0x7109871A])
    signer, _ = lp(signers)
    signed_data, o = lp(signer)
    signatures, o = lp(signer, o)
    pubkey, o = lp(signer, o)
    check(o == len(signer), "signer blob fully consumed")

    digests, o2 = lp(signed_data)
    certs_blob, o2 = lp(signed_data, o2)
    addl, o2 = lp(signed_data, o2)
    check(o2 == len(signed_data), "signed-data blob fully consumed")
    check(addl == b"", "no additional attributes (as expected)")
    entry, _ = lp(digests)                                # digests: seq of lp(digest)
    algo = struct.unpack_from("<I", entry, 0)[0]
    our_digest, _ = lp(entry, 4)
    check(algo == 0x0103, "digest algorithm id 0x0103 (RSA PKCS#1 v1.5 SHA-256)",
          f"id=0x{algo:04x}")

    # recompute the content digest from the spec
    eocd = bytearray(raw[eocd_off:])
    struct.pack_into("<I", eocd, 16, blk_start)          # CD offset := block start
    CH = 1 << 20
    chunk_digests, total = [], 0
    for sec in (raw[:blk_start], raw[cd_off:cd_off + cd_size], bytes(eocd)):
        for i in range(0, len(sec), CH):
            c = sec[i:i + CH]
            total += 1
            chunk_digests.append(hashlib.sha256(b"\xa5" + struct.pack("<I", len(c)) + c).digest())
            if len(c) < CH:
                break
    h = hashlib.sha256(b"\x5a" + struct.pack("<I", total))
    for cd in chunk_digests:
        h.update(cd)
    check(h.digest() == our_digest, "v2 content digest reproduces from the spec",
          f"chunks={total} (1 MiB each)")

    sig_entry, _ = lp(signatures)                         # signatures: seq of lp(sig)
    sig_algo = struct.unpack_from("<I", sig_entry, 0)[0]
    sig, _ = lp(sig_entry, 4)
    cert_der, _ = lp(certs_blob)
    cert = x509.load_der_x509_certificate(cert_der)
    disk = x509.load_pem_x509_certificate(open(CERT_PEM, "rb").read())
    check(cert_der == disk.public_bytes(serialization.Encoding.DER),
          "v2 certificate == the committed keys/notes.cert.pem")
    check(pubkey == cert.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo),
        "embedded public key matches the certificate")
    check(cert.public_key().verify(sig, signed_data, padding.PKCS1v15(), hashes.SHA256()) is None,
          "v2 signature verifies over signed-data", f"sigalgo=0x{sig_algo:04x}, {len(sig)} B")
    print(f"        subject : {cert.subject.rfc4514_string()}")
    print(f"        serial  : {cert.serial_number:x}")
    print(f"        expires : {cert.not_valid_after_utc:%Y-%m-%d}")
except Exception as e:  # noqa: BLE001
    check(False, f"v2 verification crashed: {type(e).__name__}: {e}")

# ---------------------------------------------------------------- structure
print("package structure:")
try:
    z = zipfile.ZipFile(io.BytesIO(raw))
    check(z.testzip() is None, "zip integrity (every CRC32)")
    meta = {i.filename: i for i in z.infolist()}
    check("classes.dex" in meta, "classes.dex present")
    arsc = meta["resources.arsc"]
    check(arsc.compress_type == zipfile.ZIP_STORED, "resources.arsc is STORED (uncompressed)")
    # zipalign / Android's rule is about where the DATA of a stored entry starts
    def data_off(i):
        h = i.header_offset
        el = struct.unpack_from("<H", raw, h + 28)[0]      # local extra length
        return h + 30 + len(i.filename.encode()) + el
    check(data_off(arsc) % 4 == 0, "resources.arsc DATA is 4-byte aligned",
          f"data@{data_off(arsc)} header@{arsc.header_offset} extra={len(arsc.extra)}B")
    unaligned = [n for n in meta if meta[n].compress_type == zipfile.ZIP_STORED
                 and data_off(meta[n]) % 4]
    check(not unaligned, f"all {sum(1 for n in meta if meta[n].compress_type == 0)} "
          "stored entries are 4-byte aligned", f"misaligned={unaligned[:3]}")
    for need in ["AndroidManifest.xml", "assets/index.html", "assets/app.js",
                 "assets/styles.css", "assets/data.js", "assets/store.js"]:
        check(need in meta, f"{need} present")
    fonts = sorted(n for n in z.namelist() if n.startswith("assets/fonts/"))
    check(len(fonts) == 8, "all 8 bundled fonts in assets", f"{len(fonts)} found")

    dex = z.read("classes.dex")
    check(b"app/notes/MainActivity" in dex, "app/notes/MainActivity is in the dex")
    check(b"app/notes/CaptureProvider" in dex, "app/notes/CaptureProvider is in the dex")
    check(b"com/android/dx" not in dex, "no dx classes leaked into the app dex")
    check(b"https://appassets.androidplatform.net/assets/index.html" in dex,
          "dex carries the https://appassets.androidplatform.net start URL")
    check(dex[:8] in (b"dex\n035\x00", b"dex\n037\x00"),
          "dex format version is 035/037 (minSdk 24 -> dx emits 037)", dex[:8].decode("latin1"))

    axml = z.read("AndroidManifest.xml")
    for prop in ["RECORD_AUDIO", "app.notes.capture", "app.notes.MainActivity"]:
        check(prop.encode() in axml or prop.encode("utf-16-le") in axml,
              f"manifest references {prop}")
    for forbidden in ["android.permission.CAMERA", "android.permission.INTERNET",
                      "WRITE_EXTERNAL_STORAGE", "READ_EXTERNAL_STORAGE"]:
        check(forbidden.encode() not in axml and forbidden.encode("utf-16-le") not in axml,
              f"manifest does NOT use {forbidden}")
except Exception as e:  # noqa: BLE001
    check(False, f"structure check crashed: {type(e).__name__}: {e}")

print("---", "ALL CHECKS PASSED" if ok_all else "SOMETHING FAILED", "---")
sys.exit(0 if ok_all else 1)
