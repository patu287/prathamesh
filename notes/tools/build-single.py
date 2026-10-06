#!/usr/bin/env python3
"""Fold Notes into one self-contained HTML file.

    python3 tools/build-single.py          # -> release/Notes.html

CSS, JS and all eight woff2 fonts are inlined, so the result has no subresources
at all: it opens from a Downloads folder, a USB stick or an email attachment with
no server and no network. Nothing is minified — the file stays readable, which is
the point of a single-file build you can inspect.

Two honest caveats, both about the browser's storage rules rather than this file:

  * Opened directly as file://, Chrome gives the page an opaque origin, so
    IndexedDB is unavailable and the app falls back to localStorage. That works
    for text, but audio and photos are stored as data URLs there and will hit the
    ~5 MB quota fast. Serve it over http (tools/../serve.py) or run the APK when
    you mean to record.
  * file:// is not a secure origin either, so `navigator.mediaDevices` is absent
    and the mic button cannot work. Text and photos are fine.

The APK embeds the same five source files, so this script and the APK build can
never drift: both read from ../notes.
"""
import base64, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # notes/
OUT = os.path.join(ROOT, "release", "Notes.html")
ASSETS = ["index.html", "styles.css", "app.js", "data.js", "store.js"]


def read(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as fh:
        return fh.read()


def font_data_uri(name):
    with open(os.path.join(ROOT, "fonts", name), "rb") as fh:
        raw = fh.read()
    return "data:font/woff2;base64," + base64.b64encode(raw).decode("ascii"), len(raw)


def main():
    html, css, js = read("index.html"), read("styles.css"), read("app.js")

    # ── fonts: url(fonts/x.woff2) -> data: URI ───────────────────────────────
    inlined, font_bytes = [], 0
    def swap_font(m):
        nonlocal font_bytes
        uri, size = font_data_uri(m.group(1))
        font_bytes += size
        inlined.append(m.group(1))
        return f"url({uri})"
    css = re.sub(r"url\([\"']?fonts/([A-Za-z0-9._-]+\.woff2)[\"']?\)", swap_font, css)

    # every url() must now be a data: URI — a stray url(fonts/…) would 404 offline
    leftovers = [u[:40] for u in re.findall(r"url\([^)]*\)", css)
                 if not u.startswith("url(data:")]
    if leftovers:
        sys.exit(f"stray url() left in CSS: {leftovers[:3]}")

    # ── the page: drop subresource links, inline style and scripts ──────────
    html = re.sub(r"^\s*<link rel=\"preload\".*\n", "", html, flags=re.M)
    html = re.sub(r"^\s*<link rel=\"stylesheet\".*\n", "", html, flags=re.M)
    for name in ["data.js", "store.js", "app.js"]:
        tag = f'<script src="{name}"></script>'
        if tag not in html:
            sys.exit(f"index.html no longer includes {tag} — update this script")
        html = html.replace(tag, f"<script>\n{read(name)}\n</script>")
    html = html.replace("</head>", f"<style>\n{css}\n</style>\n</head>")

    # A subresource is anything in the markup itself. src="${...}" inside a script
    # is a runtime binding to a blob URL, so strip scripts and the stylesheet first
    # and check what is left — that is the only place a 404-offline reference can hide.
    markup = re.sub(r"<script>.*?</script>", "", html, flags=re.S)
    markup = re.sub(r"<style>.*?</style>", "", markup, flags=re.S)
    external = [f[:60] for f in re.findall(r'(?:src|href)="(?!#|data:|\$)[^"]+"', markup)]
    if external:
        sys.exit(f"subresource link survived inlining: {external[:3]} — refusing to "
                 "write a file that cannot work offline")

    # The app promises that nothing leaves the device. Keep it literally true:
    # no URL anywhere in the JavaScript, not even a comment about one.
    for name in ["data.js", "store.js", "app.js"]:
        urls = re.findall(r'''https?://[^\s"'`)]*''', read(name))
        if urls:
            sys.exit(f"{name} mentions {urls[:2]} — the artifact is offline-only, so "
                     "a URL in shipped JavaScript is either dead weight or a bug")

    comment = f"""<!--
  Notes — one self-contained file. Written by tools/build-single.py; edit the
  sources in ../notes, not this file.

  {len(inlined)} fonts, the stylesheet and every script are inlined: this page makes
  zero network requests and needs no server. Open it and write.

  Opened as file:// the browser withholds IndexedDB and the microphone (both need
  a real origin), so the app falls back to localStorage and the mic button stays
  inert. Text and photos work; serve the file over http when you want to record.
-->
"""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(comment + html)

    print(f"wrote {os.path.relpath(OUT, os.path.dirname(ROOT))}  "
          f"{os.path.getsize(OUT) / 1024:.0f} KB  "
          f"({len(inlined)} fonts inlined, {font_bytes / 1024:.0f} KB of woff2, "
          f"{len(ASSETS) - 1} scripts)")


if __name__ == "__main__":
    main()
