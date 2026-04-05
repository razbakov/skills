---
name: youtube-metadata-updater
description: "Download a YouTube video, transcribe it, generate optimized title/description/chapters/tags, create a thumbnail, and update the video via YouTube Data API. Use when the user shares a YouTube URL and wants title, description, chapters, tags, or thumbnail updated. Triggers: 'update youtube', 'need title and description', 'add chapters', 'fix youtube metadata', 'generate thumbnail for youtube', or when user shares a youtube.com/watch URL and asks for metadata."
---

# YouTube Metadata Updater

Given a YouTube video URL, produce and apply optimized metadata: title, description with chapters, tags, and a thumbnail.

## Prerequisites

- **uvx** with `yt-dlp` (audio download)
- **faster-whisper** server at `localhost:8000` (transcription)
- **ffmpeg** (audio chunking)
- **Google Chrome** (thumbnail screenshot)
- **YouTube Data API** enabled in Google Cloud project
- **OAuth token** at `~/.config/youtube/token.json` (created on first run)
- **Update script** at `~/Projects/ikigai/.bin/youtube-update.py`

## Workflow

### Step 1: Extract video ID and download audio

```bash
# Extract video ID from URL (the ?v= parameter)
VIDEO_ID="HOzfntvOXMY"
MEETING_DIR="<project>/meetings/YYYY-MM-DD"
mkdir -p "$MEETING_DIR"

uvx yt-dlp -f "bestaudio" -o "$MEETING_DIR/livestream.%(ext)s" \
  "https://www.youtube.com/watch?v=$VIDEO_ID"
```

Also fetch existing metadata for context:
```bash
uvx yt-dlp --dump-json --no-download "https://www.youtube.com/watch?v=$VIDEO_ID" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print('Title:', d.get('title')); print('Duration:', d.get('duration_string')); print('Channel:', d.get('channel'))"
```

### Step 2: Transcribe with faster-whisper

The faster-whisper server crashes on large files. Split into 2-minute chunks and transcribe sequentially using the `small` model.

```bash
# Split into 2-min m4a chunks (copy codec, fast)
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$MEETING_DIR/livestream.m4a" | cut -d. -f1)
CHUNK=120
for i in $(seq 0 $CHUNK $((DURATION - 1))); do
  idx=$(printf "%02d" $((i / CHUNK)))
  ffmpeg -i "$MEETING_DIR/livestream.m4a" -ss $i -t $CHUNK -c copy "/tmp/mchunk_${idx}.m4a" -y
done
```

Transcribe all chunks with offset correction:
```python
# Use Systran/faster-whisper-small (not large-v3, crashes on CPU)
# Add chunk offset to each segment's start time
# Save combined result to $MEETING_DIR/transcription.txt
# Format: [M:SS] text
```

Key lessons:
- `Systran/faster-whisper-large-v3` crashes after 1-2 chunks on CPU — use `small`
- m4a chunks (codec copy) are faster to create than wav
- Wait for server health check between chunks if server restarts

### Step 3: Analyze transcript and generate metadata

Read the full transcript. Identify:
- **Topic transitions** for chapter markers (aim for 15-25 chapters)
- **Core theme** for the title (clickable, under 70 chars)
- **Key topics** for description and tags
- **Series context** (e.g., AI Study Group meeting number)

Output format — save to `$MEETING_DIR/youtube-metadata.md`:
```markdown
# YouTube Metadata — [Series] Meeting #N (YYYY-MM-DD)

**Title:** [Clickable title under 70 chars]

**Description:**
[2-3 sentence summary]

[Series context line]

Chapters:
0:00 [First chapter]
...

[Links section]

#tag1 #tag2 ...

**Tags:** tag1, tag2, ...
```

Also save `$MEETING_DIR/youtube-update.json` for the API:
```json
{
  "title": "...",
  "description": "...",
  "tags": ["..."],
  "categoryId": "28"
}
```

Category IDs: 22=People & Blogs, 27=Education, 28=Science & Technology.

### Step 4: Generate thumbnail

Create an HTML file (`$MEETING_DIR/thumbnail.html`) at 1280x720px with:
- Dark gradient background (purple/blue)
- Bold hero text (2-3 words max)
- Subtitle in monospace
- Terminal/code aesthetic elements
- Series badge (e.g., "LIVE — AI Study Group #3")

Capture at 2x resolution:
```bash
google-chrome --headless --screenshot="$MEETING_DIR/thumbnail.png" \
  --window-size=1280,720 --force-device-scale-factor=2 \
  "$MEETING_DIR/thumbnail.html"
```

Show the thumbnail to the user for approval before uploading.

### Step 5: Update YouTube via API

```bash
uvx --from google-api-python-client --with google-auth-oauthlib --with google-auth-httplib2 \
  python3 ~/Projects/ikigai/.bin/youtube-update.py $VIDEO_ID \
  --meta "$MEETING_DIR/youtube-update.json" \
  --thumbnail "$MEETING_DIR/thumbnail.png"
```

First run requires OAuth browser authorization. Token is cached at `~/.config/youtube/token.json`.

If YouTube Data API is not enabled, direct user to:
`https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project=PROJECT_ID`

### Step 6: Confirm

Verify the update by showing the video URL and confirming the title was applied.

## Output Files

| File | Purpose |
|------|---------|
| `livestream.m4a` | Downloaded audio |
| `transcription.txt` | Timestamped transcript |
| `youtube-metadata.md` | Human-readable metadata reference |
| `youtube-update.json` | API payload |
| `thumbnail.html` | Thumbnail source |
| `thumbnail.png` | Uploaded thumbnail |
