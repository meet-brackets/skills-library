#!/usr/bin/env python3
"""Post-process a Higgsfield diagram so its background lands exactly on the theme token.

    python postprocess_diagram.py <src.png> <dst.png> --bg "#312F3D" [--crop] [--shift | --no-shift]

The model lands near, not on, the target background (#2C2A39…#2E2B3A for #312F3D), which shows as a
visible box on the page. Steps:
1. measure the background (median of the top-left 20×20 px);
2. --shift (default on dark themes): move every channel by target − measured;
   --no-shift (default on light backgrounds): leave content pixels alone;
3. snap pixels whose difference from the measured background is < 7 to the exact target;
4. --crop: crop to the content bounding box + 140 px vertical padding (wide timelines);
5. resize to --width (default 1920, LANCZOS) and save an optimized PNG.

Pillow only. On Windows pass C:/… paths, not Git-Bash /c/… paths. Last stdout line = JSON report.
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return '#%02X%02X%02X' % tuple(rgb[:3])


def luminance(rgb):
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


def process(src, dst, target_hex, crop_to_content=False, shift=None, width=1920):
    target = hex_to_rgb(target_hex)
    im = Image.open(src).convert('RGB')
    bg = tuple(round(v) for v in ImageStat.Stat(im.crop((0, 0, 20, 20))).median)
    if shift is None:
        # The global shift was only verified on dark backgrounds; on light ones it can drift dark text.
        shift = luminance(target) < 128

    if shift:
        off = [target[i] - bg[i] for i in range(3)]
        base = Image.merge('RGB', [b.point(lambda v, o=o: max(0, min(255, v + o)))
                                   for b, o in zip(im.split(), off)])
    else:
        base = im

    diff = ImageChops.difference(im, Image.new('RGB', im.size, bg)).convert('L')
    near = diff.point(lambda v: 255 if v < 7 else 0)
    out = Image.composite(Image.new('RGB', im.size, target), base, near)

    if crop_to_content:
        box = diff.point(lambda v: 255 if v > 30 else 0).getbbox()
        if box:
            out = out.crop((0, max(0, box[1] - 140), out.width, min(out.height, box[3] + 140)))

    if out.width != width:
        out = out.resize((width, round(width * out.height / out.width)), Image.LANCZOS)
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    out.save(dst, optimize=True)

    corners = [out.getpixel(p) for p in ((2, 2), (out.width - 3, 2), (2, out.height - 3), (out.width - 3, out.height - 3))]
    return {
        'file': str(dst), 'size': [out.width, out.height], 'kb': round(Path(dst).stat().st_size / 1024),
        'bg_measured_before': rgb_to_hex(bg), 'bg_target': target_hex.upper(), 'shift': shift,
        'corners': [rgb_to_hex(c) for c in corners], 'bg_ok': all(c == target for c in corners),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('src')
    p.add_argument('dst')
    p.add_argument('--bg', required=True, help='theme background hex, e.g. #312F3D')
    p.add_argument('--crop', action='store_true', help='crop to content + 140 px vertical padding')
    g = p.add_mutually_exclusive_group()
    g.add_argument('--shift', dest='shift', action='store_true', default=None, help='force the global channel shift')
    g.add_argument('--no-shift', dest='shift', action='store_false', help='snap the background only')
    p.add_argument('--width', type=int, default=1920)
    args = p.parse_args()

    report = process(args.src, args.dst, args.bg, args.crop, args.shift, args.width)
    print(json.dumps(report))
    return 0 if report['bg_ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
