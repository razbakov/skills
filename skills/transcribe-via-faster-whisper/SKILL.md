---
name: transcribe-via-faster-whisper
description: "Transcribe video or audio recordings locally using faster-whisper via Docker. Sets up the transcription service, extracts audio, and produces timestamped transcription (JSON + plain text). Use when the user asks to transcribe a video, audio file, meeting recording, podcast episode, or any media file. Triggers: 'transcribe this video', 'transcribe this audio', 'get transcript', 'transcribe recording', 'speech to text'."
---

# Transcribe via Faster Whisper

## Overview

Free, local transcription using faster-whisper running in Docker. Extracts audio from video, sends it to the local whisper server, and produces both full text and timestamped JSON output.

## Prerequisites

- **Docker** (for faster-whisper transcription service)
- **ffmpeg** (for audio extraction)

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

### Step 2: Extract Audio

Extract audio from video to reduce upload size (skip if input is already audio):

```bash
ffmpeg -i "$INPUT" -vn -acodec libmp3lame -q:a 4 /tmp/audio.mp3 -y
```

### Step 3: Transcribe

1. Wait for whisper server health check:
   ```bash
   curl -s http://localhost:8000/health
   ```

2. Send for transcription with timestamps:
   ```bash
   curl -s http://localhost:8000/v1/audio/transcriptions \
     -F "file=@/tmp/audio.mp3" \
     -F "model=Systran/faster-whisper-small" \
     -F "response_format=verbose_json" \
     -o transcription.json
   ```

3. Save both the full text and the timestamped JSON.

### Step 4: Output

Produce two files in the output directory:
- `transcription.json` — timestamped segments with start/end times
- `transcription.txt` — full plain text transcript

## Tips

- First run downloads the model (~500MB) — subsequent runs are fast.
- For long recordings (>1h), transcription may take several minutes.
- The `verbose_json` format includes per-segment timestamps, which are essential for downstream tools like video cutting.
- If the server is not responding, check `docker compose logs faster-whisper`.
