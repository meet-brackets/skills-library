#!/usr/bin/env python3
"""Render a content-diagrams HTML file to PNG with a headless Edge / Chrome.

    python render_diagram.py diagram.html --out-dir <scratch> --name six-steps --lang en,sk [--theme dark]
    python render_diagram.py diagram.html --out-dir <scratch> --name six-steps --lang en --theme light --variant light
    python render_diagram.py diagram.html ... --colors palette --variant color   # decorative category colors
    python render_diagram.py diagram.html ... --theme brand --bg "#0B3D2E" --accent "#34D399" [--light]
    python render_diagram.py --extract <file.png> [-o diagram.html]

Per language it writes <name>-<lang>[-<variant>].png (1920 px wide, optimized, source HTML embedded as an
iTXt chunk) and previews/<name>-<lang>[-<variant>]-358.png (the size a phone shows it at).
Needs only Python + Pillow and an installed Edge or Chrome. The last stdout line is a JSON report;
exit code 1 means a render failed or the background didn't land on the theme hex.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlencode

from PIL import Image, ImageChops
from PIL.PngImagePlugin import PngInfo

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / 'assets'
CANVAS_CSS_WIDTH = 1200
SENTINEL = (255, 0, 255)
SOURCE_KEY = 'content-diagrams:source'
PARAMS_KEY = 'content-diagrams:params'
THEME_BG = {
    'dark': '#312F3D',
    'dark-subtle': '#494559',
    'light': '#F4F3F6',
    'primary': '#F5A816',
}


def find_browser():
    env = os.environ.get('DIAGRAM_BROWSER')
    candidates = [env] if env else []
    for base in (os.environ.get('PROGRAMFILES(X86)'), os.environ.get('PROGRAMFILES'), os.environ.get('LOCALAPPDATA')):
        if base:
            candidates += [os.path.join(base, 'Microsoft', 'Edge', 'Application', 'msedge.exe'),
                           os.path.join(base, 'Google', 'Chrome', 'Application', 'chrome.exe')]
    candidates += ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                   '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge']
    for name in ('msedge', 'microsoft-edge', 'google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'chrome'):
        found = shutil.which(name)
        if found:
            candidates.append(found)
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return None


def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return '#%02X%02X%02X' % tuple(rgb[:3])


def screenshot(browser, workdir, query, css_height, dsf):
    shot = workdir / 'shot.png'
    if shot.exists():
        shot.unlink()
    url = (workdir / 'diagram.html').as_uri() + '?' + urlencode(query)
    cmd = [browser, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
           '--no-default-browser-check', '--allow-file-access-from-files',
           f'--user-data-dir={workdir / "profile"}', f'--force-device-scale-factor={dsf}',
           f'--window-size={CANVAS_CSS_WIDTH},{css_height}', f'--screenshot={shot}',
           '--virtual-time-budget=5000', url]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    if not shot.exists():
        raise RuntimeError('browser produced no screenshot')
    return Image.open(shot).convert('RGB')


def crop_canvas(im):
    """Crop to the .diagram element: everything that isn't the sentinel color."""
    diff = ImageChops.difference(im, Image.new('RGB', im.size, SENTINEL)).convert('L')
    bbox = diff.point(lambda v: 255 if v > 60 else 0).getbbox()
    if not bbox:
        raise RuntimeError('canvas not found (blank page?)')
    out = im.crop(bbox)
    # Drop a blended edge row/column left by fractional device pixels.
    ref = out.getpixel((2, 2))
    for _ in range(2):
        if out.height > 4 and out.getpixel((2, out.height - 1)) != ref:
            out = out.crop((0, 0, out.width, out.height - 1))
        if out.width > 4 and out.getpixel((out.width - 1, 2)) != ref:
            out = out.crop((0, 0, out.width - 1, out.height))
    return out, bbox


def render_one(browser, src_html, args, lang, out_path, preview_path):
    workdir = Path(tempfile.mkdtemp(prefix='content-diagrams-'))
    try:
        shutil.copy(ASSETS / 'base.css', workdir / 'base.css')
        shutil.copy(ASSETS / 'diagram.js', workdir / 'diagram.js')
        shutil.copytree(ASSETS / 'fonts', workdir / 'fonts')
        (workdir / 'diagram.html').write_text(src_html, encoding='utf-8')

        query = {'theme': args.theme, 'colors': args.colors}
        if lang:
            query['lang'] = lang
        if args.bg:
            query['bg'] = args.bg
        if args.accent:
            query['accent'] = args.accent
        if args.on_accent:
            query['onaccent'] = args.on_accent
        if args.light:
            query['light'] = '1'

        dsf = args.width / CANVAS_CSS_WIDTH
        css_height = 2400
        for _ in range(3):
            shot = screenshot(browser, workdir, query, css_height, dsf)
            canvas, bbox = crop_canvas(shot)
            if bbox[3] < shot.height - 2:
                break
            css_height *= 2  # canvas touches the bottom edge: it may be cut off
        else:
            raise RuntimeError('canvas taller than the render window')

        if canvas.width != args.width:
            canvas = canvas.resize((args.width, round(args.width * canvas.height / canvas.width)), Image.LANCZOS)

        expected = (args.bg or THEME_BG.get(args.theme, '')).upper()
        measured = rgb_to_hex(canvas.getpixel((2, 2)))
        corners = {rgb_to_hex(canvas.getpixel(p)) for p in
                   ((2, 2), (canvas.width - 3, 2), (2, canvas.height - 3), (canvas.width - 3, canvas.height - 3))}

        info = PngInfo()
        info.add_itxt(SOURCE_KEY, src_html, zip=True)
        info.add_itxt(PARAMS_KEY, json.dumps({**query, 'width': args.width}), zip=False)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out_path, optimize=True, pnginfo=info)

        preview_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.resize((358, round(358 * canvas.height / canvas.width)), Image.LANCZOS).save(preview_path)

        return {
            'file': str(out_path), 'preview_358': str(preview_path), 'lang': lang, 'theme': args.theme,
            'size': [canvas.width, canvas.height], 'ratio': round(canvas.width / canvas.height, 3),
            'kb': round(out_path.stat().st_size / 1024), 'bg_measured': measured, 'bg_expected': expected or None,
            'bg_ok': (measured == expected and len(corners) == 1) if expected else None,
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def extract(png, out):
    im = Image.open(png)
    src = im.text.get(SOURCE_KEY) if hasattr(im, 'text') else None
    if not src:
        print(json.dumps({'ok': False, 'error': f'no {SOURCE_KEY} chunk in {png}'}))
        return 1
    target = Path(out) if out else Path(png).with_suffix('.html')
    with open(target, 'w', encoding='utf-8', newline='') as f:
        f.write(src)
    print(json.dumps({'ok': True, 'html': str(target), 'params': json.loads(im.text.get(PARAMS_KEY, '{}'))}))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('src', nargs='?', help='diagram HTML file')
    p.add_argument('--out-dir', help='where PNGs go (render into the scratchpad, copy to the repo after review)')
    p.add_argument('--name', help='base file name, e.g. six-steps')
    p.add_argument('--lang', default='', help='comma-separated languages, e.g. en,sk (empty = no language switch)')
    p.add_argument('--theme', default='dark', choices=['dark', 'dark-subtle', 'light', 'primary', 'brand'])
    p.add_argument('--colors', default='mono', choices=['mono', 'palette'],
                   help='palette = activate the decorative category colors (data-cat) in the source')
    p.add_argument('--variant', default='', help='file suffix after the language, e.g. light, dark, primary, brand, mobile')
    p.add_argument('--bg', help='brand / custom background hex (theme=brand)')
    p.add_argument('--accent', help='brand accent hex (theme=brand)')
    p.add_argument('--on-accent', help='text color on the brand accent fill')
    p.add_argument('--light', action='store_true', help='brand surface is light: use gray-900 text')
    p.add_argument('--width', type=int, default=1920, help='output width in px (default 1920)')
    p.add_argument('--extract', metavar='PNG', help='write the embedded source HTML of a rendered PNG')
    p.add_argument('-o', '--output', help='output path for --extract')
    args = p.parse_args()

    if args.extract:
        return extract(args.extract, args.output)
    if not (args.src and args.out_dir and args.name):
        p.error('src, --out-dir and --name are required')
    if args.theme == 'brand' and not args.bg:
        p.error('--theme brand needs --bg')

    browser = find_browser()
    if not browser:
        print(json.dumps({'ok': False, 'error': 'no Edge / Chrome found; set DIAGRAM_BROWSER to its path'}))
        return 1

    src_html = Path(args.src).read_bytes().decode('utf-8')  # keep line endings byte-exact for --extract
    out_dir = Path(args.out_dir)
    results, ok = [], True
    for lang in [l.strip() for l in args.lang.split(',') if l.strip()] or ['']:
        suffix = f'-{args.variant}' if args.variant else ''
        stem = f'{args.name}-{lang}{suffix}' if lang else f'{args.name}{suffix}'
        try:
            r = render_one(browser, src_html, args, lang, out_dir / f'{stem}.png', out_dir / 'previews' / f'{stem}-358.png')
            ok = ok and r['bg_ok'] is not False
        except Exception as e:  # report and continue with the other languages
            r, ok = {'lang': lang, 'error': str(e)}, False
        results.append(r)

    print(json.dumps({'ok': ok, 'browser': browser, 'results': results}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
