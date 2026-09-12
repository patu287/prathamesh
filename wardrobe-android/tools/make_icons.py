#!/usr/bin/env python3
"""
Rasterise the My Wardrobe launcher icon into the five legacy mipmap densities.

API 26+ uses the adaptive icon (mipmap-anydpi-v26 + the vector foreground), but
API 24-25 still need real PNGs. There is no image tooling in this environment,
so the glyph is drawn here directly: a hanger rendered as distance-to-segment
coverage, supersampled 3x3 per pixel and box-filtered down for anti-aliasing.

    python3 tools/make_icons.py

Writes into app/src/main/res/mipmap-*/ic_launcher.png and ic_launcher_round.png.
The round variant is the same art with the corners made transparent, which is
what launchers on those API levels expect.
"""
import math
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, '..', 'app', 'src', 'main', 'res'))

BG = (0x13, 0x11, 0x10)        # Dusk --bg
FG = (0xC9, 0xA4, 0x4C)        # antique gold
STROKE = 4.6                   # in 108-unit design space, matching the vector
CONTENT_SCALE = 1.34           # legacy icons fill more of the canvas than adaptive
DENSITIES = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}
SS = 3                         # supersampling factor per axis


# ------------------------------------------------------------------ geometry
# Everything is authored in the same 108x108 space as the vector drawable.
HOOK_C, HOOK_R = (54.0, 36.6), 5.9
STEM = ((54.0, 42.5), (54.0, 50.4))
SHOULDERS = ((54.0, 50.4), (31.6, 65.8)), ((54.0, 50.4), (76.4, 65.8))
BAR = ((31.6, 67.0), (76.4, 67.0))
SEGMENTS = [STEM, SHOULDERS[0], SHOULDERS[1], BAR]


def dist_seg(px, py, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def coverage(x, y, size):
    """1.0 inside the gold glyph, 0.0 outside, fractional on the edge."""
    # map pixel space -> 108 design space
    k = (size / 108.0) * CONTENT_SCALE
    cx = cy = size / 2.0
    gx = (x - cx) / k + 54.0
    gy = (y - cy) / k + 54.0
    half = STROKE / 2.0

    d_hook = abs(math.hypot(gx - HOOK_C[0], gy - HOOK_C[1]) - HOOK_R)
    d = d_hook
    for a, b in SEGMENTS:
        d = min(d, dist_seg(gx, gy, a, b))
    return max(0.0, min(1.0, (half - d) / half + 0.5)) if d < half else 0.0


def render(size, round_mask):
    rows = []
    r = size / 2.0
    for y in range(size):
        row = bytearray()
        for x in range(size):
            acc = [0.0, 0.0, 0.0]
            a_acc = 0.0
            for sy in range(SS):
                for sx in range(SS):
                    px = x + (sx + 0.5) / SS
                    py = y + (sy + 0.5) / SS
                    c = coverage(px, py, size)
                    a = 255
                    if round_mask:
                        dd = math.hypot(px - r, py - r)
                        a = max(0.0, min(1.0, (r - dd) + 0.5))
                        a = int(round(a * 255))
                    for i in range(3):
                        src = FG[i] if c > 0 else BG[i]
                        acc[i] += (src * c + BG[i] * (1 - c)) * (a / 255.0)
                    a_acc += a
            n = SS * SS
            row += bytes(int(round(v / n)) for v in acc)
            row.append(int(round(a_acc / n)))
        rows.append(bytes(row))
    return rows


# ----------------------------------------------------------------- png writer
def write_png(path, size, rows):
    raw = b''.join(b'\x00' + r for r in rows)          # filter type 0 per scanline
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
            print('  %-34s %3dpx  %6d bytes' % ('mipmap-%s/%s' % (name, fname), size, n))
    print('wrote %d icons, %d bytes total' % (len(DENSITIES) * 2, total))


if __name__ == '__main__':
    main()
