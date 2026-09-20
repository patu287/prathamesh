#!/usr/bin/env python3
"""
Tiny static file server for the course playground.

Why not `python3 -m http.server`? Two reasons:
  1. it does not know the MIME type of `.wasm` on older Pythons, and Pyodide
     refuses to start if the WebAssembly file is not served as application/wasm;
  2. we want no-cache headers so editing a lesson file shows up on refresh.

Usage:
    python3 serve.py              # serves the repo root on port 8080
    python3 serve.py 9000         # custom port

Then open:  http://localhost:8080/python-course/playground/
"""

import functools
import http.server
import mimetypes
import pathlib
import socketserver
import sys

mimetypes.add_type("application/wasm", ".wasm")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/javascript", ".mjs")
mimetypes.add_type("application/json", ".json")
mimetypes.add_type("text/plain", ".py")
mimetypes.add_type("image/svg+xml", ".svg")

ROOT = pathlib.Path(__file__).resolve().parent.parent  # repo root
PLAYGROUND = "/python-course/playground/"


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 - required name
        # make the root URL land straight on the playground
        if self.path in ("/", ""):
            self.send_response(302)
            self.send_header("Location", PLAYGROUND)
            self.end_headers()
            return
        super().do_GET()

    def end_headers(self):
        # never cache: the playground fetches .py sources that you may be editing
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def log_message(self, fmt, *args):  # quieter logs
        if "404" in (fmt % args) or "500" in (fmt % args):
            sys.stderr.write("  " + fmt % args + "\n")


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    handler = functools.partial(Handler, directory=str(ROOT))
    with Server(("0.0.0.0", port), handler) as httpd:
        print(f"🐍 Python course playground → http://localhost:{port}{PLAYGROUND}")
        print(f"   serving {ROOT}  (Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nbye 👋")


if __name__ == "__main__":
    main()
