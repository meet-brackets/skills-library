#!/usr/bin/env python3
"""
Find which palette colors the latest meetbrackets.com/thinking articles use, and suggest the next one.

Only needs Pillow. Reads the live listing (newest first), opens each article's og:image, samples a
ring of border pixels (the background; the ring also outvotes an AI-disclosure icon in one corner)
and maps them to the nearest BRACKETS palette color. A background far from every palette color is
reported as off-palette and blocks nothing.

Examples
  python recent_colors.py                                  # last 8 live articles + suggestion
  python recent_colors.py --count 5 --json                 # machine-readable
  python recent_colors.py --local-repo C:/_WWW/BRACKETS/brackets-web
                                                           # also count local entries not live yet

Suggestion order: the most recent article's color is excluded (no back-to-back repeat), then colors
not used in the window, then the least recently used ones.
"""
import argparse
import io
import json
import re
import sys
import urllib.request
from pathlib import Path

from PIL import Image

# Keep in sync with references/palette.md (source: brackets-web/src/styles/tokens/colors.css)
PALETTE = {
    "Carribean Green": "#34D399",
    "Supernova": "#F5A816",
    "Biloba Flower": "#9333EA",
    "Princess Perfume": "#DB2777",
    "Deep Sky": "#22D3EE",
    "Crusta": "#F97316",
    "Cornflower Blue": "#2563EB",
    "Blue Violet": "#4F46E5",
    "Radical Red": "#F43F5E",
    "Keppel": "#14B8A6",
}
SITE = "https://meetbrackets.com"
OFF_PALETTE = 60  # RGB distance above which a background counts as off-palette
UA = {"User-Agent": "Mozilla/5.0 (article-illustration skill)"}


def rgb(hex_):
    hex_ = hex_.lstrip("#")
    return tuple(int(hex_[i:i + 2], 16) for i in (0, 2, 4))


def to_hex(c):
    return "#%02X%02X%02X" % c


PALETTE_RGB = {name: rgb(h) for name, h in PALETTE.items()}


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def nearest(c):
    name = min(PALETTE_RGB, key=lambda n: dist(PALETTE_RGB[n], c))
    return name, dist(PALETTE_RGB[name], c)


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read()


def median(colors):
    return tuple(sorted(c[i] for c in colors)[len(colors) // 2] for i in range(3))


def background(img):
    """Return (measured hex, palette name or None, distance) for an image's background."""
    img = img.convert("RGB")
    w, h = img.size
    inset, steps = 3, 24
    ring = []
    for i in range(steps + 1):
        x = inset + (w - 2 * inset - 1) * i // steps
        y = inset + (h - 2 * inset - 1) * i // steps
        ring += [img.getpixel((x, inset)), img.getpixel((x, h - 1 - inset)),
                 img.getpixel((inset, y)), img.getpixel((w - 1 - inset, y))]
    votes = {}
    for c in ring:
        name, d = nearest(c)
        if d <= OFF_PALETTE:
            votes.setdefault(name, []).append(c)
    if votes:
        name, group = max(votes.items(), key=lambda kv: len(kv[1]))
        if len(group) * 2 >= len(ring):  # majority of the border is this palette color
            m = median(group)
            return to_hex(m), name, round(dist(PALETTE_RGB[name], m))
    m = median(ring)
    return to_hex(m), None, round(nearest(m)[1])


def live_articles(count):
    html = fetch(f"{SITE}/thinking").decode("utf-8", "replace")
    slugs = []
    for s in re.findall(r'href="/thinking/([a-z0-9-]+)/?"', html):
        if s not in slugs:
            slugs.append(s)
    out = []
    for slug in slugs[:count]:
        entry = {"slug": slug, "source": "live"}
        try:
            page = fetch(f"{SITE}/thinking/{slug}").decode("utf-8", "replace")
            og = re.search(r'property="og:image"\s+content="([^"]+)"', page)
            if not og:
                raise ValueError("no og:image")
            entry["image"] = og.group(1)
            entry["hex"], entry["color"], entry["distance"] = background(
                Image.open(io.BytesIO(fetch(og.group(1)))))
        except Exception as e:  # one broken article shouldn't kill the run
            entry["error"] = str(e)
        out.append(entry)
    return out, set(slugs)


def local_articles(repo, live_slugs):
    """Entries in a local brackets-web checkout that aren't on the live listing (newest first)."""
    repo = Path(repo)
    out = []
    for f in (repo / "src/content/thinking").glob("*.mdoc"):
        slug = f.stem
        if slug in live_slugs:
            continue
        text = f.read_text(encoding="utf-8")
        fm = text.split("---")[1] if text.startswith("---") else ""
        date = re.search(r"^publishDate:\s*['\"]?([0-9-]+)", fm, re.M)
        img = re.search(r"^\s+image:\s*(?:>-\s*\n\s*)?['\"]?(@assets/[^'\"\n]+)", fm, re.M)
        if not img:
            continue  # no featured image yet: nothing to compare against
        path = repo / "src" / img.group(1).replace("@assets/", "assets/", 1)
        entry = {"slug": slug, "source": "local", "date": date.group(1) if date else "", "image": str(path)}
        try:
            entry["hex"], entry["color"], entry["distance"] = background(Image.open(path))
        except Exception as e:
            entry["error"] = str(e)
        out.append(entry)
    return sorted(out, key=lambda e: e["date"], reverse=True)


def suggest(articles):
    used = [a.get("color") for a in articles]  # newest first, None = off-palette / error
    latest = used[0] if used else None
    last_seen = {}
    for i, c in enumerate(used):
        if c and c not in last_seen:
            last_seen[c] = i
    candidates = [n for n in PALETTE if n != latest]
    # never used in the window first (palette order), then the oldest last use first
    candidates.sort(key=lambda n: (n in last_seen, -last_seen.get(n, 0)))
    return latest, [{"color": n, "hex": PALETTE[n], "last_used": last_seen.get(n)} for n in candidates]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--count", type=int, default=8, help="how many latest live articles to check")
    ap.add_argument("--local-repo", help="brackets-web checkout; adds entries not live yet")
    ap.add_argument("--json", action="store_true", help="print JSON instead of a table")
    args = ap.parse_args()

    try:
        articles, live_slugs = live_articles(args.count)
    except Exception as e:
        sys.exit(f"Could not read {SITE}/thinking: {e}")
    if args.local_repo:
        articles = local_articles(args.local_repo, live_slugs) + articles
    latest, ranking = suggest(articles)

    if args.json:
        print(json.dumps({"articles": articles, "excluded": latest, "suggestions": ranking}, indent=2))
        return
    print("Latest articles (newest first):")
    for i, a in enumerate(articles):
        if "error" in a:
            label = f"error: {a['error']}"
        elif a["color"]:
            label = f"{a['color']} {PALETTE[a['color']]} (measured {a['hex']}, d={a['distance']})"
        else:
            label = f"OFF-PALETTE (measured {a['hex']}, nearest d={a['distance']})"
        print(f"  {i + 1:>2}. [{a['source']}] {a['slug']}: {label}")
    print(f"\nExcluded (latest article): {latest or 'none (latest is off-palette or unreadable)'}")
    print("Suggestions (best first):")
    for s in ranking:
        when = "not used in window" if s["last_used"] is None else f"last used by article #{s['last_used'] + 1}"
        print(f"  - {s['color']} {s['hex']}: {when}")


if __name__ == "__main__":
    main()
