#!/usr/bin/env python3
"""
Tiny receiver for the Android build's self-reports.

GitHub Actions step logs live on a CDN this sandbox cannot reach, so the build
(settings.gradle, gradle.buildFinished) PUTs its outcome here instead:
failure.log on failure, the finished APK on success. GET serves whatever has
landed in wardrobe-android/release/, which is also how the APK reaches the
phone: https://8081-<sandbox>.e2b.app/MyWardrobe-1.0.apk

    python3 wardrobe-android/tools/report_server.py [port]
"""
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'release'))
os.makedirs(DIR, exist_ok=True)
SAFE = re.compile(r'^[\w.\-]+$')
CTYPE = {
    'apk': 'application/vnd.android.package-archive',
    'log': 'text/plain; charset=utf-8',
    'txt': 'text/plain; charset=utf-8',
}


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def _reply(self, code, body, ctype='text/plain; charset=utf-8', attachment=None):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        if attachment:
            self.send_header('Content-Disposition', 'attachment; filename="%s"' % attachment)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        name = os.path.basename(self.path.rstrip('/'))
        if not name:
            files = sorted(os.listdir(DIR))
            listing = '\n'.join('%s  %d bytes' % (f, os.path.getsize(os.path.join(DIR, f)))
                                for f in files) or '(nothing received yet)'
            self._reply(200, listing.encode())
            return
        path = os.path.join(DIR, name)
        if SAFE.match(name) and os.path.isfile(path):
            body = open(path, 'rb').read()
            ext = name.rsplit('.', 1)[-1].lower()
            self._reply(200, body, CTYPE.get(ext, 'application/octet-stream'),
                        attachment=name if ext == 'apk' else None)
        else:
            self._reply(404, b'not found')

    def do_PUT(self):
        name = os.path.basename(self.path.split('/upload/')[-1])
        size = int(self.headers.get('Content-Length') or 0)
        body = self.rfile.read(size)
        if not SAFE.match(name) or size == 0 or size > 60_000_000:
            self._reply(400, b'bad name or size')
            return
        with open(os.path.join(DIR, name), 'wb') as f:
            f.write(body)
        print('SAVED %s (%d bytes)' % (name, size), flush=True)
        self._reply(200, ('saved %s' % name).encode())

    def log_message(self, fmt, *args):
        print('[%s] %s' % (self.command, fmt % args), flush=True)


if __name__ == '__main__':
    print('report receiver on 0.0.0.0:%d -> %s' % (PORT, DIR), flush=True)
    ThreadingHTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
