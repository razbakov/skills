#!/usr/bin/env python3
"""Pull frames from a video at the moments the transcript points at the screen.

When someone in a recording says "look here", "this button", "вот тут" or "hier",
the words alone mean nothing to the agent doing the triage. This script finds those
moments in a timestamped transcript and saves the video frame shown at each one,
plus (optionally) a frame at every scene change, and writes context.md: one entry per
moment with its timecode, the words said and the frame to look at.

Needs: python3 (stdlib only) and ffmpeg/ffprobe on PATH.

Transcript formats: Whisper / faster-whisper JSON (segments, optional word timestamps),
SRT or VTT. Make one with:
  whisper video.mp4 --output_format json --word_timestamps True --output_dir out/

Usage:
  video_context.py VIDEO TRANSCRIPT [--out DIR] [--scenes 0.3] [--every 0]
                   [--min-gap 3] [--offset 0] [--pattern REGEX ...]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Phrases that point at what is on screen. Kept narrow on purpose: bare "this" or
# "das" appear in nearly every sentence and would flood the output with frames.
POINTERS = [
    # English
    r"\blook(?:ing)? (?:here|at (?:this|that|these|the))\b", r"\b(?:see|you see) (?:here|this|that)\b",
    r"\b(?:right|over|up|down|in) here\b", r"\bhere (?:is|you|we|it)\b", r"\bthis (?:one|button|page|screen|field|part|thing|column|row|menu|tab|icon|box|list|card|view|link)\b",
    r"\bthat (?:one|button|page|screen|field|part|thing)\b", r"\bclick(?:ing|ed)?\b", r"\bscroll(?:ing|ed)?\b", r"\bhover\b",
    # German
    r"\bhier\b", r"\bschau(?:t|en)? (?:mal|hier)\b", r"\bguck(?:t)? mal\b", r"\bda (?:oben|unten|drüben)\b", r"\bdiese[nrms]? (?:knopf|button|seite|feld|spalte|zeile)\b", r"\bklick",
    # Russian / Ukrainian
    r"\bвот\b", r"\bтут\b", r"\bздесь\b", r"\bсмотри(?:те)?\b", r"\bвидишь\b", r"\bвидите\b", r"\bэт(?:от|а|у|и) (?:кнопк|страниц|пол|блок|экран)", r"\bнажим|\bнажм|\bкликн", r"\bось\b", r"\bтут\b",
    # Spanish
    r"\baquí\b", r"\bmira(?:d)?\b", r"\besto de aquí\b", r"\bahí\b", r"\bclic",
]


def ts(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def parse_clock(text: str) -> float:
    text = text.strip().replace(",", ".")
    parts = [float(p) for p in text.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def load_transcript(path: Path):
    """Return a list of segments: {start, end, text, speaker, words: [{start, word}]}."""
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(raw)
        segs = data["segments"] if isinstance(data, dict) else data
        out = []
        for s in segs:
            words = [{"start": float(w["start"]), "word": w.get("word", w.get("text", ""))}
                     for w in s.get("words") or [] if w.get("start") is not None]
            out.append({"start": float(s["start"]), "end": float(s.get("end", s["start"])),
                        "text": s.get("text", "").strip(), "speaker": s.get("speaker", ""), "words": words})
        return out
    # SRT / VTT
    out = []
    for block in re.split(r"\n\s*\n", raw):
        m = re.search(r"([\d:.,]+)\s*-->\s*([\d:.,]+)", block)
        if not m:
            continue
        lines = block[m.end():].strip().splitlines()
        text = " ".join(re.sub(r"<[^>]+>", "", line) for line in lines).strip()
        speaker = ""
        sm = re.match(r"^(?:\[([^\]]+)\]|([A-Z][\w .-]{0,30}):)\s*(.*)$", text)
        if sm:
            speaker, text = (sm.group(1) or sm.group(2)), sm.group(3)
        out.append({"start": parse_clock(m.group(1)), "end": parse_clock(m.group(2)),
                    "text": text, "speaker": speaker, "words": []})
    return out


def duration(video: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(video)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def grab(video: Path, at: float, dest: Path) -> bool:
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{at:.2f}", "-i", str(video),
                        "-frames:v", "1", "-vf", "scale='min(1600,iw)':-2", "-q:v", "3", str(dest)],
                       capture_output=True, text=True)
    return r.returncode == 0 and dest.exists()


def scene_times(video: Path, threshold: float):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(video), "-vf",
                        f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"],
                       capture_output=True, text=True)
    return [float(t) for t in re.findall(r"pts_time:([\d.]+)", r.stderr)]


def word_time(seg, offset):
    """Time of the word at character `offset` in the segment text.

    With word timestamps, walk the words until their joined text reaches the offset.
    Without them, estimate from how far into the segment text the offset falls."""
    if seg["words"]:
        pos = 0
        text = seg["text"]
        for w in seg["words"]:
            word = w["word"].strip()
            found = text.find(word, pos) if word else -1
            end = (found if found >= 0 else pos) + len(word)
            if end > offset:
                return w["start"]
            pos = end
        return seg["words"][-1]["start"]
    frac = offset / max(1, len(seg["text"]))
    return seg["start"] + frac * (seg["end"] - seg["start"])


def segment_at(segments, t):
    for s in segments:
        if s["start"] <= t <= s["end"] + 0.5:
            return s
    before = [s for s in segments if s["start"] <= t]
    return before[-1] if before else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("transcript", type=Path)
    ap.add_argument("--out", type=Path, default=Path("video-context"))
    ap.add_argument("--scenes", type=float, default=0.0,
                    help="also save a frame at each scene change above this score (0.2-0.4 suits screen recordings; 0 = off)")
    ap.add_argument("--every", type=float, default=0.0, help="also save a frame every N seconds (0 = off)")
    ap.add_argument("--min-gap", type=float, default=3.0,
                    help="skip a scene/interval frame closer than this to the previous frame (pointing frames use 0.5s)")
    ap.add_argument("--offset", type=float, default=0.0,
                    help="seconds to add to transcript times when the transcript and video start at different moments")
    ap.add_argument("--lead", type=float, default=0.6,
                    help="seconds after the pointing word to take the frame (the cursor usually lands just after)")
    ap.add_argument("--pattern", action="append", default=[], help="extra regex for pointing phrases")
    a = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if subprocess.run(["which", tool], capture_output=True).returncode:
            sys.exit(f"{tool} not found on PATH")
    if not a.video.exists() or not a.transcript.exists():
        sys.exit("video or transcript not found")

    segments = load_transcript(a.transcript)
    if not segments:
        sys.exit("no timestamped segments in the transcript")
    length = duration(a.video)
    pat = re.compile("|".join(POINTERS + a.pattern), re.IGNORECASE)

    moments = []  # (time, reason, segment)
    for s in segments:
        for m in pat.finditer(s["text"]):
            t = word_time(s, m.start())
            moments.append((t + a.offset + a.lead, "pointing", s))
    if a.scenes:
        for t in scene_times(a.video, a.scenes):
            moments.append((t + 0.3, "scene change", segment_at(segments, t - a.offset)))
    if a.every:
        t = 0.0
        while t < length:
            moments.append((t, "interval", segment_at(segments, t - a.offset)))
            t += a.every

    frames_dir = a.out / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    # Pointing moments first, so a scene or interval frame never crowds one out.
    chosen = []
    for t, reason, seg in sorted(moments, key=lambda m: (m[1] != "pointing", m[0])):
        if length:
            t = min(t, max(0.0, length - 0.5))
        gap = 0.5 if reason == "pointing" else a.min_gap
        if any(abs(t - c[0]) < gap for c in chosen):
            continue
        chosen.append((t, reason, seg))

    kept = []
    for t, reason, seg in sorted(chosen, key=lambda m: m[0]):
        dest = frames_dir / f"{ts(t).replace(':', '-')}_{reason.split()[0]}_{int(t * 10) % 10}.jpg"
        if grab(a.video, t, dest):
            kept.append((t, reason, seg, dest))

    lines = [f"# Video context: {a.video.name}", "",
             f"Transcript: `{a.transcript}` · {len(segments)} segments · video {ts(length)} · "
             f"{len(kept)} frames ({sum(1 for k in kept if k[1] == 'pointing')} where someone points at the screen)", "",
             "Open each frame before reading its quote: the words refer to what is on it.", ""]
    for t, reason, seg, dest in kept:
        who = f"**{seg['speaker']}:** " if seg and seg.get("speaker") else ""
        quote = seg["text"] if seg else ""
        said = f"{who}\"{quote}\" (segment {ts(seg['start'])}–{ts(seg['end'])})" if quote else "_(no speech)_"
        lines += [f"## [{ts(t)}] {reason}", "", said, "",
                  f"![{ts(t)}]({dest.relative_to(a.out)})", ""]
    (a.out / "context.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(kept)} frames -> {frames_dir}\ncontext -> {a.out / 'context.md'}")


if __name__ == "__main__":
    main()
