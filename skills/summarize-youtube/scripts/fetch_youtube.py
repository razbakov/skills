#!/usr/bin/env python3
"""Fetch metadata + a clean transcript for one or more YouTube videos.

Why this exists: YouTube pages don't expose the transcript to a plain fetch,
and auto-generated captions arrive as rolling, heavily-duplicated VTT/SRT.
This script wraps the reliable path (yt-dlp captions) and collapses the
rolling duplicates into readable prose so the model can summarize directly.

Usage:
    python3 fetch_youtube.py <url-or-id> [<url-or-id> ...] [--outdir DIR] [--lang en]

For each video it writes  <outdir>/clean_<id>.txt  (plain transcript text)
and prints one metadata line per video:
    <id>\tTITLE\tCHANNEL\tDURATION\tUPLOAD_DATE\t<clean_path>
Videos with no captions still get a metadata line with an empty path.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def video_id(url: str) -> str:
    m = re.search(r"(?:v=|youtu\.be/|/shorts/|/embed/)([\w-]{11})", url)
    if m:
        return m.group(1)
    return url  # assume a bare id was passed


def watch_url(token: str) -> str:
    if token.startswith("http"):
        return token
    return f"https://www.youtube.com/watch?v={token}"


def metadata(url: str) -> str:
    try:
        out = subprocess.run(
            ["yt-dlp", "--skip-download", "--print",
             "%(title)s\t%(uploader)s\t%(duration_string)s\t%(upload_date)s", url],
            capture_output=True, text=True, timeout=120,
        )
        return out.stdout.strip() or "\t\t\t"
    except Exception:
        return "\t\t\t"


def fetch_subs(url: str, vid: str, lang: str, workdir: Path) -> Path | None:
    """Download auto + manual subs, convert to srt, return the srt path or None."""
    tmpl = str(workdir / f"{vid}.%(ext)s")
    subprocess.run(
        ["yt-dlp", "--skip-download", "--write-auto-sub", "--write-sub",
         "--sub-lang", lang, "--sub-format", "vtt", "--convert-subs", "srt",
         "-o", tmpl, url],
        capture_output=True, text=True, timeout=300,
    )
    # yt-dlp names it <vid>.<lang>.srt (lang may carry a region suffix)
    candidates = sorted(workdir.glob(f"{vid}*.srt"))
    return candidates[0] if candidates else None


def clean_srt(path: Path) -> str:
    """Strip indices/timestamps/tags and collapse rolling-caption duplicates."""
    lines = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = raw.strip()
        if not s or s.isdigit() or "-->" in s:
            continue
        s = re.sub(r"<[^>]+>", "", s)          # inline timing tags
        if lines and lines[-1] == s:
            continue
        lines.append(s)
    out = []
    for s in lines:
        if out and (s in out[-1] or out[-1] in s):
            if len(s) > len(out[-1]):
                out[-1] = s                     # keep the longer rolling line
            continue
        out.append(s)
    return " ".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--lang", default="en")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        for token in args.urls:
            vid = video_id(token)
            url = watch_url(token)
            meta = metadata(url)
            srt = fetch_subs(url, vid, args.lang, workdir)
            clean_path = ""
            if srt:
                text = clean_srt(srt)
                if text:
                    dest = outdir / f"clean_{vid}.txt"
                    dest.write_text(text, encoding="utf-8")
                    clean_path = str(dest)
            print(f"{vid}\t{meta}\t{clean_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
