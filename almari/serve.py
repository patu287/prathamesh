#!/usr/bin/env python3
"""Dev server for Almari — threaded, cache-disabled, binds 0.0.0.0.

    python3 serve.py [port]        # default 8080

`python3 -m http.server` also works, but it sends Last-Modified and lets the
browser cache CSS/JS — an embedded preview can then show a stale build after
an edit. This turns caching off so the preview is always the current code.
"""
import os
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, max-age=0, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write('%s - %s\n' % (self.address_string(), fmt % args))
        sys.stderr.flush()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    handler = partial(Handler, directory=HERE)
    httpd = ThreadingHTTPServer(('0.0.0.0', port), handler)
    httpd.daemon_threads = True
    print('Almari dev server on http://0.0.0.0:%d  (root: %s)' % (port, HERE), flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nstopped', flush=True)


if __name__ == '__main__':
    main()
