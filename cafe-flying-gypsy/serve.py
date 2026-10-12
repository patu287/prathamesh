#!/usr/bin/env python3
"""
Dev server for the Cafe Flying Gypsy's site.

Two problems this solves, both of which made the embedded preview fail:

1. STALE CACHING
   Plain `python3 -m http.server` sends no cache headers, so a browser keeps
   serving the previous styles.css / app.js after an edit — you fix the CSS,
   refresh, and nothing appears to change. This sends `no-store` on every
   response and drops `Last-Modified` entirely, so a 304 can never resurrect
   a stale file.

2. CONNECTIONS BEING DROPPED UNDER A NORMAL PAGE LOAD
   The stdlib default is HTTP/1.0 with a listen backlog of 5. A browser
   loading this page requests ~24 files at once; with HTTP/1.0 every one of
   them needs its own connection, the accept queue overflows, the kernel
   drops the SYNs and the client stalls for ~1s on retransmit before
   retrying. Through a proxy that reads as a broken preview.
   Fixed by speaking HTTP/1.1 (so connections are reused) and raising the
   backlog to 512.

    python3 serve.py [port]        # default 8080
    # → http://localhost:8080
"""

import os
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))


class Handler(SimpleHTTPRequestHandler):
    # reuse connections instead of opening one per file
    protocol_version = "HTTP/1.1"
    # clean up idle keep-alive sockets rather than leaking a thread each
    timeout = 20

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def send_header(self, keyword, value):
        # never let a cached 304 sneak back in
        if keyword.lower() == "last-modified":
            return
        super().send_header(keyword, value)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))
        sys.stderr.flush()

    def handle_one_request(self):
        # a browser or proxy hanging up mid-response is normal, not an error
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            self.close_connection = True


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    # was 5 — a single page load asks for ~24 files at once
    request_queue_size = 512


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    handler = partial(Handler, directory=HERE)
    httpd = Server(("0.0.0.0", port), handler)
    print(
        "Cafe Flying Gypsy's dev server on http://0.0.0.0:%d  (root: %s)"
        % (port, HERE),
        flush=True,
    )
    try:
        httpd.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print("\nstopped", flush=True)


if __name__ == "__main__":
    main()
