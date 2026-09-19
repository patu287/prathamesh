#!/usr/bin/env python3
"""Dev server for Rojni — threaded, cache-disabled, binds 0.0.0.0.

    python3 serve.py [port]        # default 8090

Serve over http, not file://. Two reasons, both real:

  * With no IndexedDB on a `file://` page the app falls back to localStorage,
    where audio and photos as data URLs run out of room almost immediately.
  * `navigator.mediaDevices` is absent on an insecure origin, so the mic button
    does nothing at all — and it does so silently.

`python3 -m http.server` also works, but it sends Last-Modified and lets the
browser cache CSS/JS, so a preview can show a stale build after an edit. This
turns caching off.
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
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    handler = partial(Handler, directory=HERE)
    httpd = ThreadingHTTPServer(('0.0.0.0', port), handler)
    httpd.daemon_threads = True
    print('Rojni dev server on http://0.0.0.0:%d  (root: %s)' % (port, HERE), flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nstopped', flush=True)


if __name__ == '__main__':
    main()
