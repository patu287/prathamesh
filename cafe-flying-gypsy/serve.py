#!/usr/bin/env python3
"""
Cache-disabled dev server for the Cafe Flying Gypsy's site.

Plain `python3 -m http.server` sends no cache headers, so browsers happily
serve a stale styles.css / app.js after an edit — you fix the CSS, refresh,
and nothing appears to change.

This sends `Cache-Control: no-store` on every response so a hard refresh is
never needed.

    python3 serve.py 8080
    # → http://localhost:8080
"""

import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def send_header(self, keyword, value):
        # never let a cached 304 sneak back in
        if keyword.lower() == "last-modified":
            return
        super().send_header(keyword, value)

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s\n" % (fmt % args))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    handler = partial(NoCacheHandler, directory=".")
    with ThreadingHTTPServer(("0.0.0.0", port), handler) as httpd:
        print(f"Cafe Flying Gypsy's — serving on http://0.0.0.0:{port}")
        print("Cache-Control: no-store on every response. Ctrl-C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")


if __name__ == "__main__":
    main()
