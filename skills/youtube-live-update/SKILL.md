---
name: youtube-live-update
description: "Update a YouTube live stream's title, description, and tags in real-time based on session agenda from Notion. Use when the user is streaming and wants to change the stream title, update the live stream description, or make the stream more discoverable. Triggers: 'update stream title', 'change live stream title', 'update my stream', 'make stream title better', or when user mentions they're streaming and wants metadata updated. This is the fast path — no transcription needed since the stream is live and the agenda is already known."
---

# YouTube Live Stream Updater

Update a live YouTube stream's title, description, and tags based on the session agenda. Fast path — no download or transcription needed.

## Prerequisites

- **uvx** with `yt-dlp` (stream discovery)
- **YouTube Data API** enabled in Google Cloud project
- **OAuth token** at `~/.config/youtube/token.json`
- **Update script** at `~/Projects/ikigai/.bin/youtube-update.py`

## Workflow

### Step 1: Find the agenda

Search Notion for today's stream agenda or plan:

```
Search Notion for: "live stream agenda", "stream plan", or today's date
Fetch the page to get the full agenda with topics
```

Extract the key topics, highlights, and demos planned for the session.

### Step 2: Find the live stream

```bash
uvx yt-dlp --flat-playlist --print "%(id)s %(title)s" \
  "https://www.youtube.com/@<YOUTUBE_CHANNEL>/live"
```

This returns the video ID and current title of the active stream. If no stream is live, tell the user.

### Step 3: Craft metadata

Based on the agenda, create optimized metadata:

**Title guidelines:**
- Under 70 characters
- Lead with the most compelling/clickable topic
- Include "Live" or "Live Coding" for discoverability
- Use a hook format: "I Built X with Y" or "Building X Live"

**Description guidelines:**
- 2-3 line summary at the top
- Bullet list of today's highlights (use emoji for visual scanning)
- "Ask questions in chat" CTA
- Links section (portfolio, project URLs)
- Hashtags at the bottom

**Tags:** 10-15 relevant tags covering the topics, tools, and audience.

Save metadata to `/tmp/youtube-update/youtube-update.json`:
```json
{
  "title": "...",
  "description": "...",
  "tags": ["..."],
  "categoryId": "28"
}
```

Category IDs: 22=People & Blogs, 27=Education, 28=Science & Technology.

### Step 4: Update via API

```bash
uvx --from google-api-python-client --with google-auth-oauthlib --with google-auth-httplib2 \
  python3 ~/Projects/ikigai/.bin/youtube-update.py $VIDEO_ID \
  --meta /tmp/youtube-update/youtube-update.json
```

### Step 5: Confirm

Show the user the new title and confirm it was applied. Provide the stream URL:
`https://www.youtube.com/watch?v=$VIDEO_ID`

## Notes

- This skill is for **live streams** where the agenda is already known. For recorded videos that need transcription and chapters, use `/youtube-metadata-updater` instead.
- The stream title can be updated multiple times during a stream — useful if the topic shifts.
- YouTube channel handle is in CLAUDE.md Personal Info.
