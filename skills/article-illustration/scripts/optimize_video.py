#!/usr/bin/env python3
"""
Turn a raw generated video into a silent, web-ready MP4 under 1 MB (target ~500 KB) and verify it.

Nothing to install by hand. ffmpeg is taken from PATH if present; otherwise the script installs the
`imageio-ffmpeg` wheel (a static ffmpeg build for Windows / macOS / Linux, ~80 MB) into a user cache
folder once, with `pip --target`, and reuses it on every later run. No admin rights, no system change.

What it does
  1. Strip audio, scale to max 1280 px wide, two-pass H.264 (yuv420p, +faststart) at a bitrate
     computed from the target size and the duration.
  2. If the file is over the limit (or well over the target), lower the bitrate ~20 % and redo,
     at most 2 retries.
  3. Verify: no audio stream, size, duration, first-vs-last frame difference (loop seam, compared
     at 320 px wide), and save
     frames at 0 / 25 / 50 / 75 % / last for a visual check.
  Prints a JSON report as the last line.

Examples
  python optimize_video.py raw.mp4 -o file.mp4
  python optimize_video.py raw.mp4 -o file.mp4 --target-kb 450 --max-kb 900 --frames-dir frames
"""
import argparse
import importlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

CACHE = Path(os.environ.get("ARTICLE_ILLUSTRATION_CACHE", Path.home() / ".cache" / "article-illustration"))
VENDOR = CACHE / "vendor"
SEAM_WIDTH = 320  # frames are compared downscaled, so halftone compression noise doesn't count as motion
LOOP_OK = 4.0  # mean per-channel difference (0-255) at SEAM_WIDTH under which the seam is invisible


def log(msg):
    print(msg, file=sys.stderr)


def find_ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    sys.path.insert(0, str(VENDOR))
    try:
        import imageio_ffmpeg  # noqa: F401
    except ImportError:
        log(f"ffmpeg not found, installing imageio-ffmpeg into {VENDOR} (one-time)...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
                        "--target", str(VENDOR), "imageio-ffmpeg"], check=True)
        importlib.invalidate_caches()  # VENDOR didn't exist when it went on sys.path
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def run(ffmpeg, args, cwd=None):
    return subprocess.run([ffmpeg, "-hide_banner", *args], cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def probe(ffmpeg, path):
    """Duration (s), has_audio, width, height, parsed from `ffmpeg -i` (no ffprobe needed)."""
    err = run(ffmpeg, ["-i", str(path)]).stderr
    d = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", err)
    if not d:
        raise RuntimeError(f"Could not read {path}:\n{err[-800:]}")
    size = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", err)
    return {
        "duration": round(int(d[1]) * 3600 + int(d[2]) * 60 + float(d[3]), 2),
        "has_audio": bool(re.search(r"Stream #.*Audio:", err)),
        "width": int(size[1]) if size else None,
        "height": int(size[2]) if size else None,
    }


def encode(ffmpeg, src, dst, kbps, max_width, workdir):
    vf = f"scale='min({max_width},iw)':-2,format=yuv420p"
    common = ["-y", "-i", str(src), "-an", "-c:v", "libx264", "-preset", "slow", "-b:v", f"{kbps}k",
              "-vf", vf, "-passlogfile", "x264"]
    p1 = run(ffmpeg, [*common, "-pass", "1", "-f", "null", "-"], cwd=workdir)
    if p1.returncode:
        raise RuntimeError(f"pass 1 failed:\n{p1.stderr[-800:]}")
    p2 = run(ffmpeg, [*common, "-maxrate", f"{int(kbps * 1.45)}k", "-bufsize", f"{kbps * 2}k",
                      "-profile:v", "high", "-pass", "2", "-movflags", "+faststart", str(dst)], cwd=workdir)
    if p2.returncode:
        raise RuntimeError(f"pass 2 failed:\n{p2.stderr[-800:]}")
    return dst.stat().st_size / 1000


def grab(ffmpeg, video, t, out, last=False):
    if last:  # keep overwriting one file while decoding the final second -> the last frame remains
        args = ["-y", "-v", "error", "-sseof", "-1", "-i", str(video), "-update", "1", str(out)]
    else:
        args = ["-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", str(out)]
    r = run(ffmpeg, args)
    if r.returncode or not out.exists():
        raise RuntimeError(f"frame grab failed at {t}s:\n{r.stderr[-500:]}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="raw video from the generator")
    ap.add_argument("-o", "--out", required=True, help="output .mp4 path")
    ap.add_argument("--target-kb", type=int, default=500)
    ap.add_argument("--max-kb", type=int, default=1000)
    ap.add_argument("--max-width", type=int, default=1280)
    ap.add_argument("--frames-dir", help="where to save check frames (default: next to --out)")
    args = ap.parse_args()

    src, out = Path(args.src).resolve(), Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = find_ffmpeg()
    info = probe(ffmpeg, src)
    # leave ~5 % for the MP4 container
    kbps = math.floor(args.target_kb * 8 / info["duration"] * 0.95)

    attempts = []
    with tempfile.TemporaryDirectory() as work:
        for _ in range(3):
            kb = encode(ffmpeg, src, out, kbps, args.max_width, work)
            attempts.append({"kbps": kbps, "kb": round(kb)})
            if kb <= args.max_kb and kb <= args.target_kb * 1.2:
                break
            kbps = math.floor(kbps * 0.8)

    result = probe(ffmpeg, out)
    frames_dir = Path(args.frames_dir).resolve() if args.frames_dir else out.parent / f"{out.stem}-frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    frames = {"first": grab(ffmpeg, out, 0, frames_dir / "first.png")}
    for pct in (25, 50, 75):
        frames[f"{pct}%"] = grab(ffmpeg, out, result["duration"] * pct / 100, frames_dir / f"p{pct}.png")
    frames["last"] = grab(ffmpeg, out, 0, frames_dir / "last.png", last=True)
    a, b = (Image.open(frames[k]).convert("RGB") for k in ("first", "last"))
    small = (SEAM_WIDTH, max(1, SEAM_WIDTH * a.height // a.width))
    a, b = a.resize(small, Image.LANCZOS), b.resize(small, Image.LANCZOS)
    seam = round(sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3, 2)

    size_kb = round(out.stat().st_size / 1000)
    report = {
        "output": str(out),
        "size_kb": size_kb,
        "under_limit": size_kb <= args.max_kb,
        "duration": result["duration"],
        "resolution": f"{result['width']}x{result['height']}",
        "has_audio": result["has_audio"],
        "loop_seam": seam,
        "loop_ok": seam < LOOP_OK,
        "attempts": attempts,
        "frames": {k: str(v) for k, v in frames.items()},
        "source": {"kb": round(src.stat().st_size / 1000), **info},
    }
    print(json.dumps(report))
    if not report["under_limit"] or report["has_audio"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
