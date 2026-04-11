---
name: process-livestream
description: |
  Process a livestream transcript into publishable content: blog post (all languages), YouTube metadata with chapters, thumbnail, hero image, and publish.
  TRIGGER when: user shares a livestream transcript, mentions processing a livestream, says "process stream", references a YouTube live stream recording they want to publish, or pastes a transcript with timestamps.
  DO NOT TRIGGER for: pre-recorded video editing, podcast episodes without video, or general YouTube video uploads without a transcript.
---

# Process Livestream

Turn a livestream transcript + YouTube link into a full content package: blog post, YouTube metadata with chapters, thumbnail, hero image, and publish everything.

## Inputs

The user provides:
1. **YouTube link** — the livestream recording URL
2. **Transcript** — timestamped transcript (from Jamie, Otter, or similar). Timestamps are relative to when transcription started, which may differ from the video start.

## Workflow

### Step 1: Identify the timestamp offset

The transcript tool (Jamie, etc.) may have started recording before or after the YouTube stream began. You need to find the offset.

1. Fetch the video's actual duration: `uvx yt-dlp --dump-json --no-download "<url>" | python3 -c "import json,sys; d=json.load(sys.stdin); print('Title:', d.get('title')); print('Duration:', d.get('duration_string'))"`
2. Ask the user: "What's the first recognizable moment in the video and its timestamp?" (e.g., "I say 'hello hello' at 6:41 in the video")
3. Find that moment in the transcript (e.g., "Hello? Hello, hello" at 00:05)
4. Calculate offset: `video_timestamp - transcript_timestamp` (e.g., 6:41 - 0:05 = +6:36)

All chapter timestamps must have this offset applied.

### Step 2: Analyze the transcript

Read the full transcript and extract:
- **Topic transitions** for chapter markers (aim for 20-30 chapters)
- **Key topics and takeaways** (5-7 bullet points)
- **Projects, tools, and links mentioned**
- **Participants** (names, roles)
- **Quotable moments** for social content hooks

Do NOT invent links or URLs that weren't explicitly mentioned. If a project was discussed but no URL was given, mention the project name without a link.

### Step 3: Create meeting directory

```
<project>/meetings/YYYY-MM-DD/
```

The project path depends on context (e.g., `~/Projects/learn-by-doing-academy/` for LBD streams). All assets go here.

### Step 4: Generate YouTube metadata

Create two files:

**`youtube-metadata.md`** — human-readable reference with:
- Optimized title (under 70 chars, clickable)
- Full description with chapters (offset-corrected timestamps)
- Tags (25-30 relevant tags)
- Key takeaways
- Links mentioned (only real, verified links)
- Social distribution hooks (X/Twitter, LinkedIn, Instagram angles)

**`youtube-update.json`** — API payload:
```json
{
  "title": "...",
  "description": "...",
  "tags": ["..."],
  "categoryId": "27"
}
```

Category IDs: 22=People & Blogs, 27=Education, 28=Science & Technology.

The first chapter must be `0:00` (either "Pre-stream" or the actual first topic if there's no dead time).

### Step 5: Generate thumbnail

Create `thumbnail.html` at 1280x720px with:
- Dark gradient background
- Bold hero text (2-4 words max, the core hook)
- Subtitle in monospace
- Series badge (e.g., "LIVE -- Learn By Doing #1")
- Clean, modern tech aesthetic

Capture at 2x resolution:
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \
  --screenshot="<meeting-dir>/thumbnail.png" \
  --window-size=1280,720 --force-device-scale-factor=2 \
  "file://<meeting-dir>/thumbnail.html"
```

Show the thumbnail to the user for approval before uploading.

### Step 6: Generate blog hero image

Use `/image-from-gemini` to generate the hero image. Never copy the thumbnail as the hero image — they serve different purposes (thumbnail = clickable at small size, hero = atmospheric at large size).

Save to the blog's public images directory (e.g., `~/Projects/razbakov.com/public/images/blog/<slug>/hero.png`).

### Step 7: Create blog post

Dispatch Luna (or create directly) to write a blog post summarizing the livestream. The post should:
- Have a compelling hook in the first paragraph
- Cover all major topics from the stream
- Include the YouTube embed/link as CTA
- Be translated to all required languages (check project CLAUDE.md for language requirements)
- Reference the hero image in frontmatter

Do NOT include links that don't exist. Verify any URLs before including them.

### Step 8: Upload YouTube metadata

```bash
uvx --from google-api-python-client --with google-auth-oauthlib --with google-auth-httplib2 \
  python3 ~/Orgs/ikigai/.bin/youtube-update.py <VIDEO_ID> \
  --meta "<meeting-dir>/youtube-update.json" \
  --thumbnail "<meeting-dir>/thumbnail.png"
```

OAuth token cached at `~/.config/youtube/token.json`.

### Step 9: Publish blog

Commit all blog files + hero image and push to trigger auto-deploy.

### Step 10: Verify and report

Report what was done:
- Blog URL(s)
- YouTube video URL with updated metadata
- Number of chapters
- Files created/committed
- Any items needing manual attention (e.g., timestamp verification)

## Output Files

| File | Location | Purpose |
|------|----------|---------|
| `youtube-metadata.md` | `<meeting-dir>/` | Human-readable reference |
| `youtube-update.json` | `<meeting-dir>/` | YouTube API payload |
| `thumbnail.html` | `<meeting-dir>/` | Thumbnail source |
| `thumbnail.png` | `<meeting-dir>/` | Uploaded thumbnail |
| `hero.png` | Blog public images | Blog hero image |
| Blog posts | Blog content dir | Published articles |

## Common Pitfalls

- **Inventing URLs**: Never create links for projects that don't have a live website. Just mention the project name.
- **Wrong timestamps**: Always confirm the offset with the user before generating chapters. A wrong offset makes every chapter wrong.
- **Thumbnail as hero**: The thumbnail and blog hero image serve different purposes. Always generate the hero image separately via `/image-from-gemini`.
- **Missing languages**: Check the project's CLAUDE.md for translation requirements before creating blog posts.
