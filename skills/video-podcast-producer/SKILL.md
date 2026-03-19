---
name: video-podcast-producer
description: "End-to-end video/podcast post-production pipeline: transcribe recordings, split into topic-based clips, remove dead time, generate thumbnails (landscape 16:9 and vertical 9:16), create YouTube metadata (titles, descriptions, tags), and cut Shorts. Use when the user has a video or audio recording (meeting, podcast, interview, webinar, stream) and wants to process it for publishing on YouTube, social media, or any platform. Triggers: 'transcribe this video', 'cut this recording', 'make YouTube clips', 'create thumbnails', 'process this meeting recording', 'split into episodes', 'make shorts from this video', 'publish this recording'."
---

# Video Podcast Producer

## Overview

Transform raw video/audio recordings into publish-ready content: transcribed, trimmed, split by topic, with thumbnails and YouTube metadata. Uses faster-whisper for free local transcription, ffmpeg for video processing, and LaTeX/TikZ for professional thumbnails.

## Prerequisites

- **Docker** (for faster-whisper transcription service)
- **ffmpeg** (for audio extraction and video cutting)
- **tectonic** (for LaTeX thumbnail generation): `brew install tectonic`
- **ImageMagick** (for PDF-to-PNG conversion): `brew install imagemagick`

## Workflow

### Step 1: Set Up Transcription Service

Check if a `compose.yaml` exists in the project with a faster-whisper service. If not, create one:

```yaml
services:
  faster-whisper:
    image: fedirz/faster-whisper-server:latest-cpu
    container_name: faster-whisper
    ports: ["8000:8000"]
    volumes:
      - ./hf_cache:/root/.cache/huggingface
    restart: unless-stopped
```

Add `hf_cache/` to `.gitignore`. Start with `docker compose up -d`.

### Step 2: Transcribe

1. Extract audio from video (reduces upload size):
   ```bash
   ffmpeg -i "$VIDEO" -vn -acodec libmp3lame -q:a 4 /tmp/audio.mp3 -y
   ```

2. Wait for whisper server health check:
   ```bash
   curl -s http://localhost:8000/health
   ```

3. Send for transcription with timestamps:
   ```bash
   curl -s http://localhost:8000/v1/audio/transcriptions \
     -F "file=@/tmp/audio.mp3" \
     -F "model=Systran/faster-whisper-small" \
     -F "response_format=verbose_json" \
     -o transcription.json
   ```

4. Save both the full text and the timestamped JSON.

### Step 3: Analyze and Plan Cuts

Review timestamped segments to identify:
- **Topic boundaries** — where conversation shifts to a new subject
- **Dead time to remove** — login screens, tech issues, breaks, off-topic tangents, silence
- **Best 60s hooks** — most engaging moments for Shorts

Present a cut plan table to the user:
| # | Title idea | Time range | Duration |
|---|-----------|------------|----------|

Wait for user approval before cutting.

### Step 4: Cut Video Clips

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

### Step 5: Cut Shorts (9:16 Vertical)

For each clip, pick the most engaging 50-70 second moment. Crop center and scale to 1080x1920:

```bash
ffmpeg -y -ss START -to END -i "$SRC" \
  -vf "crop=405:720:437:0,scale=1080:1920" \
  -c:v libx264 -crf 23 -c:a aac output-short.mp4
```

The crop values assume 1280x720 source. Adjust for other resolutions:
- Crop width = source_height * 9/16
- Crop x offset = (source_width - crop_width) / 2

### Step 6: Generate Thumbnails

Use the `latex-pdf` skill workflow with TikZ for professional thumbnails.

**Design principles:**
- Massive bold text filling the frame — readable at small sizes
- 2-3 color palette per thumbnail (gradient background + accent)
- Clean geometric elements, no clutter
- Strong visual hierarchy: title > graphic > subtitle
- Drop shadows on text via duplicate offset nodes
- Use `\usepackage{lmodern}` and `\sffamily\bfseries` for fonts at large sizes

**16:9 landscape** (YouTube): 25.6cm x 14.4cm canvas, convert to 1280x720 PNG
**9:16 vertical** (Shorts): 10.8cm x 19.2cm canvas, convert to 1080x1920 PNG

See `references/thumbnail-template.md` for the TikZ boilerplate and helper functions.

Convert PDF to PNG:
```bash
magick -density 300 thumbnail.pdf -resize 1280x720! -quality 95 thumbnail.png
```

### Step 7: Generate YouTube Metadata

For each clip, generate:
- **Title** — under 70 chars, hook-driven, not clickbait
- **Description** — summary + topic bullets + relevant links + hashtags
- **Tags** — 8-12 relevant keywords

Save all metadata in a single `youtube-metadata.md` file.

### Step 8: Organize Files

Structure output in a dated meeting/episode folder:

```
meetings/YYYY-MM-DD/
├── transcription.txt          # Full text
├── transcription.json         # Timestamped segments
├── 01-clip-name.mp4           # Topic clips (16:9)
├── 01-thumbnail.pdf           # Vector thumbnail
├── 01-thumbnail.png           # Raster thumbnail (1280x720)
├── 01-short.mp4               # Vertical short (9:16)
├── 01-short-thumb.pdf         # Vertical thumbnail vector
├── 01-short-thumb.png         # Vertical thumbnail (1080x1920)
├── ...
├── youtube-metadata.md         # Titles, descriptions, tags
└── cuts.txt                   # Cut plan documentation
```

### Step 9: Upload to YouTube

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

### Step 10: Promote

After publishing:
- Cut **YouTube Shorts** (60-90s vertical clips) as teaser content
- Share in relevant communities (Reddit, Telegram, X/Twitter)
- Consider creating a playlist for the series (e.g., "AI Study Group")
- Post short clips first — they drive discovery to the long-form videos

## Tips & Lessons Learned

- **Split long recordings into topic-based clips** — 48 min is too long for YouTube retention. 5-15 min per topic performs better.
- **Shorts drive discovery** — the counting demo and "elephant problem" are perfect 60s hooks.
- **Thumbnails matter most** — big text, 2-3 colors, readable at small sizes. Use LaTeX/TikZ for consistency.
- **Remove dead time aggressively** — login screens, tech issues, coffee breaks, link searching. Keep only content.
- **Stream copy (`-c copy`)** for speed when cutting — only re-encode for crops (Shorts).
- **Parallel processing** — run independent ffmpeg cuts simultaneously.
- **Description SEO** — include timestamps (chapters), links, hashtags at the bottom.
- **Tags** — 8-12 keywords mixing broad ("AI") and specific ("ChatGPT count to 200").
- **Verify before publishing** — always ask user to confirm visibility setting before clicking Publish.
