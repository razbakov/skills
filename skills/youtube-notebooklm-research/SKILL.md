# YouTube NotebookLM Research

Search YouTube for videos on a topic, add them to a NotebookLM notebook, and ask questions about the content.

## Trigger

When the user asks to research a topic using YouTube videos, find videos and add to NotebookLM, or learn about something from YouTube content.

## Prerequisites

- `notebooklm` CLI installed (`pipx install "notebooklm-py[browser]"`)
- `yt-dlp` installed (`brew install yt-dlp`)
- Authenticated: `notebooklm login` (one-time browser auth)
- Chromium for playwright: `pipx run --spec "notebooklm-py[browser]" playwright install chromium`

## Process

### Step 1: Search YouTube

Use yt-dlp to find relevant videos on the topic:

```bash
yt-dlp "ytsearch${COUNT}:${TOPIC}" --flat-playlist --print "%(id)s | %(title)s | %(duration)s | %(channel)s | %(view_count)s" 2>/dev/null
```

- Default COUNT: 5 (adjustable by user)
- Filter out videos shorter than 2 minutes (likely shorts/clips)
- Filter out videos longer than 120 minutes unless user wants deep dives
- Prefer videos with higher view counts when relevance is similar

### Step 2: Present results and confirm

Show the user the found videos with title, channel, duration, and view count. Ask which ones to add (default: all).

### Step 3: Create or select NotebookLM notebook

```bash
# Create a new notebook for the topic
notebooklm create "Research: ${TOPIC}"

# Or list existing to reuse
notebooklm list
notebooklm use <notebook_id>
```

### Step 4: Add YouTube videos as sources

```bash
# Add each selected video
notebooklm source add "https://www.youtube.com/watch?v=${VIDEO_ID}"
```

Wait for each source to be indexed before adding the next. Check with:
```bash
notebooklm source list
```

### Step 5: Ready to query

```bash
# Ask questions about the content
notebooklm ask "What are the key points across all videos?"
notebooklm ask "${USER_QUESTION}"
```

### Step 6: Optional - Generate artifacts

```bash
# Generate a podcast-style audio summary
notebooklm generate audio "Focus on practical takeaways" --wait

# Generate a study guide
notebooklm generate report --style study-guide --wait

# Generate quiz
notebooklm generate quiz --difficulty medium

# Download artifacts
notebooklm download audio ./research-${TOPIC}.mp3
```

## Output

- NotebookLM notebook with YouTube videos as sources
- Answers to user's questions grounded in video content
- Optional: audio summary, study guide, quiz

## Notes

- NotebookLM uses Gemini to process video transcripts — answers are grounded in actual content, not hallucinated
- The `add_youtube` method extracts transcripts automatically, no need for manual transcript download
- Auth token stored at `~/.notebooklm/storage_state.json` — refresh with `notebooklm login` if expired
- For batch research across multiple topics, create separate notebooks per topic
