#!/usr/bin/env python3
"""
Rasterise the Notes launcher icon into the five legacy mipmap densities.

API 26+ uses the adaptive icon (mipmap-anydpi-v26 + the vector foreground), but
API 24-25 still need real PNGs. There is no image tooling in this environment, so
the glyph is drawn here directly: a page with two ordinary lines and one amber
line — the sentence that got promoted to a key point — rendered as shape
coverage, supersampled 3x3 per pixel and box-filtered down for anti-aliasing.

    python3 tools/make_icons.py

Writes into app/src/main/res/mipmap-*/ic_launcher.png and ic_launcher_round.png.
The round variant is the same art with the corners made transparent, which is what
launchers on those API levels expect. The colours are the app's own tokens, so the
Python and the vector drawable cannot drift apart silently — if you change one,
change both.
"""
import math
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, '..', 'app', 'src', 'main', 'res'))

BG = (0x2F, 0x3E, 0x6B)        # indigo
PAPER = (0xF6, 0xF2, 0xE9)     # paper
ACCENT = (0xB0, 0x7F, 0x2F)    # amber — the promoted line

CONTENT_SCALE = 1.34           # legacy icons fill more of the canvas than adaptive
DENSITIES = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}
SS = 3                         # supersampling factor per axis

# ── geometry, authored in the same 108x108 space as the vector drawable ──────
PAGE = (35.0, 26.0, 79.0, 82.0, 6.0)     # x0, y0, x1, y1, corner radius
STROKE = 4.0
LINES = [((42.0, 45.0), (66.0, 55.0 - 10.0), False),
         ((42.0, 55.0), (66.0, 55.0), False),
         ((42.0, 65.0), (58.0, 65.0), True)]     # True = the amber one


def dist_seg(px, py, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def inside_page(px, py):
    """Rounded-rectangle test: shrink the box by the radius, then measure the
    distance to the remaining core rectangle."""
    x0, y0, x1, y1, r = PAGE
    cx = max(x0 + r, min(px, x1 - r))
    cy = max(y0 + r, min(py, y1 - r))
    if x0 + r <= px <= x1 - r and y0 <= py <= y1:
        return True
    if y0 + r <= py <= y1 - r and x0 <= px <= x1:
        return True
    return math.hypot(px - cx, py - cy) <= r


def sample(px, py):
    """The colour under one sample point, in 108-unit design space."""
    half = STROKE / 2.0
    for a, b, amber in LINES:
        if dist_seg(px, py, a, b) <= half:
            return ACCENT if amber else BG
    if inside_page(px, py):
        return PAPER
    return BG


def render(size, round_mask):
    k = (size / 108.0) * CONTENT_SCALE
    c = size / 2.0
    r = size / 2.0
    rows = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            acc = [0.0, 0.0, 0.0]
            a_acc = 0.0
            for sy in range(SS):
                for sx in range(SS):
                    px = x + (sx + 0.5) / SS
                    py = y + (sy + 0.5) / SS
                    gx = (px - c) / k + 54.0
                    gy = (py - c) / k + 54.0
                    col = sample(gx, gy)
                    a = 255
                    if round_mask:
                        dd = math.hypot(px - r, py - r)
                        a = int(round(max(0.0, min(1.0, (r - dd) + 0.5)) * 255))
                    for i in range(3):
                        acc[i] += col[i] * (a / 255.0)
                    a_acc += a
            n = SS * SS
            row += bytes(int(round(v / n)) for v in acc)
            row.append(int(round(a_acc / n)))
        rows.append(bytes(row))
    return rows


# ── png writer ───────────────────────────────────────────────────────────────
def write_png(path, size, rows):
    raw = b''.join(b'\x00' + r for r in rows)                   # filter 0 per scanline
    ihdr = struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)   # 8-bit RGBA

    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data
                + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF))

    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', zlib.compress(raw, 9))
           + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


def main():
    total = 0
    for name, size in DENSITIES.items():
        d = os.path.join(RES, 'mipmap-' + name)
        os.makedirs(d, exist_ok=True)
        for fname, round_mask in (('ic_launcher.png', False), ('ic_launcher_round.png', True)):
            n = write_png(os.path.join(d, fname), size, render(size, round_mask))
            total += n
            print('  %-40s %3dpx  %6d bytes' % ('mipmap-%s/%s' % (name, fname), size, n))
    print('wrote %d icons, %d bytes total' % (len(DENSITIES) * 2, total))


if __name__ == '__main__':
    main()
