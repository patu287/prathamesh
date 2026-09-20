#!/usr/bin/env python3
"""
Build PythonCourse-1.0.apk by packaging the offline Pyodide playground and curriculum
into a native Android WebView shell.
"""

import os
import sys
import zipfile
import pathlib

# Course and repo root
HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parent
REPO = COURSE.parent
PLAYGROUND = COURSE / "playground"

# Keys and template
TEMPLATE_APK = REPO / "reset" / "Reset-1.0.apk"
KEY_DIR = REPO / "android" / "keys"
OUT_APK = COURSE / "PythonCourse-1.0.apk"

# Import mkapk machinery
sys.path.insert(0, str(REPO / "android" / "tools"))
import mkapk

def collect_assets():
    """Collect all files needed for the offline Python course app."""
    assets = {}

    # 1. Entry point index.html
    entry_html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Python Course</title>
  <meta http-equiv="refresh" content="0; url=playground/index.html" />
  <style>
    body {
      background: #0b0f17;
      color: #e8edf7;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      margin: 0;
      text-align: center;
    }
    .spinner {
      width: 32px;
      height: 32px;
      border: 3px solid rgba(255,255,255,0.15);
      border-top-color: #38bdf8;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      margin-bottom: 16px;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>
  <div class="spinner"></div>
  <p>Loading Python Playground…</p>
  <script>location.replace("playground/index.html");</script>
</body>
</html>"""
    assets["assets/index.html"] = entry_html.encode("utf-8")

    # 2. Playground web files
    for fname in ["index.html", "style.css", "app.js", "worker.js"]:
        fpath = PLAYGROUND / fname
        if fpath.exists():
            assets[f"assets/playground/{fname}"] = fpath.read_bytes()

    # 3. Vendored Pyodide
    vendor_dir = PLAYGROUND / "vendor" / "pyodide"
    for item in vendor_dir.glob("*"):
        if item.is_file():
            assets[f"assets/playground/vendor/pyodide/{item.name}"] = item.read_bytes()

    # 4. Documentation (README and CHEATSHEET)
    for doc in ["README.md", "CHEATSHEET.md"]:
        fpath = COURSE / doc
        if fpath.exists():
            assets[f"assets/{doc}"] = fpath.read_bytes()

    # 5. Lessons, exercises, dsa, problems, tools
    for section_dir in ["lessons", "exercises", "dsa", "problems", "tools"]:
        sdir = COURSE / section_dir
        if not sdir.exists():
            continue
        for root, _, files in os.walk(sdir):
            if "__pycache__" in root:
                continue
            for f in files:
                if f.endswith(".py"):
                    full = pathlib.Path(root) / f
                    rel = full.relative_to(COURSE).as_posix()
                    assets[f"assets/{rel}"] = full.read_bytes()

    return assets

def build():
    print("Collecting Python course assets...")
    assets = collect_assets()
    print(f"Collected {len(assets)} assets (~{sum(len(v) for v in assets.values()) / (1024*1024):.1f} MB)")

    print(f"Reading template APK from {TEMPLATE_APK}...")
    files = []
    classes_dex = None

    with zipfile.ZipFile(TEMPLATE_APK, "r") as z:
        for info in z.infolist():
            name = info.filename
            # Skip old assets, old signature, and classes.dex (handled separately)
            if name.startswith("assets/") or name.startswith("META-INF/"):
                continue
            if name == "classes.dex":
                classes_dex = z.read(name)
                continue
            files.append((name, z.read(name)))

    if not classes_dex:
        raise RuntimeError("No classes.dex found in template APK")

    # Add all new assets
    for aname, adata in assets.items():
        files.append((aname, adata))

    # Add classes.dex
    files.append(("classes.dex", classes_dex))

    # Android requires AndroidManifest.xml first
    files.sort(key=lambda f: (f[0] != "AndroidManifest.xml", f[0]))

    # Sign APK (v1 + v2)
    kp = KEY_DIR / "reset.key.pem"
    cp = KEY_DIR / "reset.cert.pem"
    key, cert = mkapk.load_key(str(kp), str(cp))

    print("Generating v1 JAR signature...")
    manifest, sf, p7 = mkapk.v1_sign(files, key, cert)

    print("Assembling ZIP structure with 4-byte alignment...")
    zw = mkapk.ZipWriter()
    for name, data in files:
        zw.add(name, data, store=name.endswith(mkapk.STORE_EXT))
    zw.add("META-INF/MANIFEST.MF", manifest)
    zw.add("META-INF/CERT.SF", sf)
    zw.add("META-INF/CERT.RSA", p7, store=True)
    unsigned = zw.finish()

    print("Signing with APK Signature Scheme v2...")
    signed = mkapk.v2_sign(unsigned, key, cert)

    OUT_APK.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_APK, "wb") as f:
        f.write(signed)

    print(f"Successfully built {OUT_APK} ({len(signed):,} bytes, ~{len(signed)/(1024*1024):.1f} MB)")

if __name__ == "__main__":
    build()
