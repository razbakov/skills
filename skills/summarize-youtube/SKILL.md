---
name: summarize-youtube
description: >-
  Summarize one or more YouTube videos from their links. Use this whenever the
  user pastes a youtube.com or youtu.be URL (or several) and wants to know what
  it's about — phrasings like "summarize to telegram", "tldr these videos",
  "what do these say", "summary of this talk", or just dropping links with no
  instruction at all. Fetches each video's real transcript via yt-dlp (not the
  page text, which never contains the transcript), cleans the captions, and
  writes a per-video summary. Default delivery is Telegram; honor any other
  surface the user names ("to my notes", "just here in chat", "email it").
  Trigger even when the user only pastes bare links — bare YouTube links almost
  always mean "tell me what's in these".
---

# Summarize YouTube

Turn YouTube links into faithful, skimmable summaries.

## Why a skill (and not just "fetch the page")

A plain web fetch of a YouTube watch page returns nav chrome and, at best, the
title — **never the transcript**. The reliable source of truth is the video's
captions, pulled with `yt-dlp`. Auto-generated captions arrive as *rolling*
lines (each cue repeats the tail of the previous one), so raw SRT is ~3x
duplicated noise. The bundled script handles both problems, so you summarize
from clean prose instead of fighting caption formatting every time.

## Workflow

### 1. Collect the links and the intent

Pull every YouTube URL from the user's message. Note any delivery instruction
("to telegram", "in chat", "email me") and any focus ("just the action items",
"compare them"). No instruction → default to a Telegram summary (see Delivery).

### 2. Fetch metadata + transcripts

Run the bundled script with all the links at once (it dedupes captions for you):

```bash
python3 <skill>/scripts/fetch_youtube.py <url1> <url2> ... --outdir /tmp
```

It prints one tab-separated line per video —
`id  TITLE  CHANNEL  DURATION  UPLOAD_DATE  /tmp/clean_<id>.txt` — and writes the
cleaned transcript to each `clean_<id>.txt`. A video with no captions gets an
empty path; for those, fall back to transcribing the audio (see
`/transcribe-via-faster-whisper`) or tell the user it has no captions.

Read each `clean_<id>.txt`. These are full transcripts — read the whole thing,
don't skim, so the summary is grounded in what was actually said.

### 3. Summarize each video

Write the summary from the transcript, not from the title or your priors. Lead
with the concrete claims, structure, and any conclusions the video reaches.

Per video, use this shape (scale length to the video — a 5-min clip gets a few
lines, a 40-min talk gets the bullets):

```
<Title> — <Channel> (<duration> · <date>)
<1-2 sentence thesis: what the video is actually about / its main claim>
• <key point / argument / step>
• <key point>
• <takeaway or conclusion>
```

Grounding rules that keep summaries trustworthy:
- **Don't characterize what you haven't verified.** If a video's framing makes
  you want to call it "satire", "fake", "outdated", or "obviously true", resist
  unless the transcript itself establishes it. Report what it says; flag genre
  ("this is presented as comedy/commentary") only when the transcript supports
  it. Tone is not proof.
- Attribute claims to the video ("the host argues…", "she claims…"), don't
  launder them into your own assertions of fact.
- Keep names, numbers, and quotes accurate to the transcript.

### 4. Deliver

**Default — Telegram.** Send via the instance's proactive Telegram sender
(in this setup: `.bin/telegram-send.py`; the agent/bot mapping lives in your
private CLAUDE.md — pick the agent whose domain fits the video topic). Telegram
renders **HTML only**, not Markdown — use `<b>`, `<i>`, `<code>`, line breaks;
no `#` headers, no `*` bullets (use `•`), no code fences. Always write the
message body to a temp file and pass it with `--file`; inline multi-byte text on
the command line corrupts. Example:

```bash
python3 .bin/telegram-send.py --agent <agent> --file /tmp/yt_summary.html
```

**Other surfaces.** If the user named one, deliver there instead (a saved file,
a chat reply, an email draft, a note). Match that surface's formatting.

After delivering, give the user a short in-chat recap too, so they see the
result without leaving the conversation.

## Notes

- Pass all links to the script in one call — it's faster and keeps the videos
  grouped.
- Non-English captions: pass `--lang <code>` (e.g. `--lang de`). Summarize in
  the user's language unless told otherwise.
- This skill is for *consuming* a video (understanding/summarizing). For
  *editing* a video's own title/description/chapters, use
  `/youtube-metadata-updater`; for deep multi-source research off a video, use
  `/youtube-notebooklm-research`.
- Requires `yt-dlp` on PATH.
