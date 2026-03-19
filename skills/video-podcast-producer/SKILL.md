---
name: video-podcast-producer
description: "End-to-end video/podcast post-production pipeline: split recordings into topic-based clips, remove dead time, generate thumbnails (landscape 16:9 and vertical 9:16), create YouTube metadata (titles, descriptions, tags), and cut Shorts. Use when the user has a video or audio recording (meeting, podcast, interview, webinar, stream) and wants to process it for publishing on YouTube, social media, or any platform. Triggers: 'cut this recording', 'make YouTube clips', 'create thumbnails', 'process this meeting recording', 'split into episodes', 'make shorts from this video', 'publish this recording'."
---

# Video Podcast Producer

## Overview

Transform raw video/audio recordings into publish-ready content: trimmed, split by topic, with thumbnails and YouTube metadata. Uses ffmpeg for video processing and the `brand-poster` skill for professional thumbnails.

## Prerequisites

- **ffmpeg** (for audio extraction and video cutting)

## Workflow

### Step 1: Transcribe

Use the `transcribe-via-faster-whisper` skill to transcribe the recording. This produces `transcription.json` (timestamped segments) and `transcription.txt` (full text).

### Step 2: Analyze and Plan Cuts

Review timestamped segments to identify:
- **Topic boundaries** — where conversation shifts to a new subject
- **Dead time to remove** — login screens, tech issues, breaks, off-topic tangents, silence
- **Best 60s hooks** — most engaging moments for Shorts

Present a cut plan table to the user:
| # | Title idea | Time range | Duration |
|---|-----------|------------|----------|

Wait for user approval before cutting.

### Step 3: Cut Video Clips

Use ffmpeg stream copy for speed (no re-encoding):

```bash
# Single segment
ffmpeg -y -i "$SRC" -ss START -to END -c copy output.mp4

# Multi-part clip (skip dead time within a topic)
ffmpeg -y -i "$SRC" -ss START1 -to END1 -c copy /tmp/partA.mp4
ffmpeg -y -i "$SRC" -ss START2 -to END2 -c copy /tmp/partB.mp4
echo "file '/tmp/partA.mp4'
file '/tmp/partB.mp4'" > /tmp/concat.txt
ffmpeg -y -f concat -safe 0 -i /tmp/concat.txt -c copy output.mp4
```

Run independent cuts in parallel with `&` and `wait`.

### Step 4: Cut Shorts (9:16 Vertical)

For each clip, pick the most engaging 50-70 second moment. Crop center and scale to 1080x1920:

```bash
ffmpeg -y -ss START -to END -i "$SRC" \
  -vf "crop=405:720:437:0,scale=1080:1920" \
  -c:v libx264 -crf 23 -c:a aac output-short.mp4
```

The crop values assume 1280x720 source. Adjust for other resolutions:
- Crop width = source_height * 9/16
- Crop x offset = (source_width - crop_width) / 2

### Step 5: Generate Thumbnails

Use the `brand-poster` skill to generate thumbnails for each clip.

**For each clip, generate two thumbnails:**
- **16:9 landscape** (1280x720) — YouTube video thumbnail
- **9:16 vertical** (1080x1920) — Shorts thumbnail

**Design principles:**
- Massive bold text filling the frame — readable at small sizes
- 2-3 color palette per thumbnail (gradient background + accent)
- Clean geometric elements, no clutter
- Strong visual hierarchy: title > graphic > subtitle

### Step 6: Generate YouTube Metadata

For each clip, generate:
- **Title** — under 70 chars, hook-driven, not clickbait
- **Description** — summary + topic bullets + relevant links + hashtags
- **Tags** — 8-12 relevant keywords

Save all metadata in a single `youtube-metadata.md` file.

### Step 7: Organize Files

Structure output in a dated meeting/episode folder:

```
meetings/YYYY-MM-DD/
├── transcription.txt          # Full text
├── transcription.json         # Timestamped segments
├── 01-clip-name.mp4           # Topic clips (16:9)
├── 01-thumbnail.png           # Landscape thumbnail (1280x720)
├── 01-short.mp4               # Vertical short (9:16)
├── 01-short-thumb.png         # Vertical thumbnail (1080x1920)
├── ...
├── youtube-metadata.md         # Titles, descriptions, tags
└── cuts.txt                   # Cut plan documentation
```

### Step 8: Upload to YouTube

Use Claude in Chrome (MCP browser extension) to automate YouTube Studio uploads:

1. Navigate to `https://studio.youtube.com`
2. Click **Create → Upload videos**
3. **User must manually select the file** (browser security blocks programmatic file uploads)
4. While video uploads, fill in metadata:
   - **Title**: Use the hook-driven title from youtube-metadata.md
   - **Description**: Full description with timestamps, links, hashtags
   - **Tags**: Comma-separated keyword list
   - **Thumbnail**: User must manually upload (same browser restriction)
   - **Audience**: "No, it's not made for kids"
5. Click through: Video elements → Initial check → Visibility
6. Set visibility (Public/Unlisted/Private) — **always confirm with user before publishing**
7. Click **Publish**

**Important limitations:**
- Browser extensions cannot upload files to `<input type="file">` elements — user must do this manually
- Always confirm before clicking irreversible buttons (Publish, Send, Post)
- YouTube processing takes several minutes after upload; SD first, then HD

### Step 9: Promote

After publishing:
- Cut **YouTube Shorts** (60-90s vertical clips) as teaser content
- Share in relevant communities (Reddit, Telegram, X/Twitter)
- Consider creating a playlist for the series (e.g., "AI Study Group")
- Post short clips first — they drive discovery to the long-form videos

## Tips & Lessons Learned

- **Split long recordings into topic-based clips** — 48 min is too long for YouTube retention. 5-15 min per topic performs better.
- **Shorts drive discovery** — the counting demo and "elephant problem" are perfect 60s hooks.
- **Thumbnails matter most** — big text, 2-3 colors, readable at small sizes. Use `brand-poster` skill for consistency.
- **Remove dead time aggressively** — login screens, tech issues, coffee breaks, link searching. Keep only content.
- **Stream copy (`-c copy`)** for speed when cutting — only re-encode for crops (Shorts).
- **Parallel processing** — run independent ffmpeg cuts simultaneously.
- **Description SEO** — include timestamps (chapters), links, hashtags at the bottom.
- **Tags** — 8-12 keywords mixing broad ("AI") and specific ("ChatGPT count to 200").
- **Verify before publishing** — always ask user to confirm visibility setting before clicking Publish.
