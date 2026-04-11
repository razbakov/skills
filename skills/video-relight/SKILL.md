---
name: video-relight
description: "Transform video/image lighting, backgrounds, and environments using Beeble SwitchX API. Use this skill when the user wants to relight a video, replace a video background, improve lighting in footage, make a clip look more cinematic or professional, add studio lighting to a recording, or do any video-to-video visual effects transformation. Also trigger when the user mentions Beeble, SwitchX, or wants VFX on short clips."
---

# Video Relight with Beeble SwitchX

Transform lighting, backgrounds, and environments in video clips and images while preserving the original subject. Powered by the Beeble SwitchX API.

## When to use

- Relight dark venue footage (e.g. dance festivals, meetups, talks)
- Replace messy backgrounds with clean/branded ones
- Give raw recordings a cinematic or studio look
- Process short clips for social media, thumbnails, or promotional content

## Prerequisites

- `BEEBLE_API_KEY` environment variable set (get one at developer.beeble.ai)
- `ffmpeg` and `ffprobe` installed (for video inspection and trimming)
- `curl` available

## Constraints

- **Max 240 frames per job** (~8s at 30fps, ~10s at 24fps). Longer videos must be split into chunks.
- **Processing time:** ~6 minutes for an 8-second clip (varies by resolution and queue).
- **Cost:** $0.10 per generation (pay-as-you-go).
- **Output URLs expire after 72 hours.** Re-poll the job status endpoint to get fresh URLs.

## Workflow

### 1. Inspect the source video

Before anything, check the video specs to know what you're working with:

```bash
ffprobe -v quiet -print_format json -show_streams INPUT_FILE | python3 -c "
import json,sys
d=json.load(sys.stdin)
for s in d['streams']:
    if s['codec_type']=='video':
        fps = s.get('r_frame_rate','?')
        dur = s.get('duration','?')
        w, h = s.get('width','?'), s.get('height','?')
        print(f'Resolution: {w}x{h}, FPS: {fps}, Duration: {dur}s')
"
```

Calculate total frames: `duration * fps`. If over 240 frames, you need to trim or split.

### 2. Trim if needed

SwitchX accepts max 240 frames. Calculate the safe duration: `240 / fps` seconds. Then trim:

```bash
ffmpeg -y -i INPUT_FILE -t SAFE_DURATION -c copy /tmp/switchx-clip.mp4
```

For longer videos, split into sequential chunks and process each separately. Reassemble with ffmpeg concat after all jobs complete.

### 3. Upload to Beeble

Create a presigned upload URL and upload the file:

```bash
# Get upload URL
UPLOAD_RESP=$(curl -s -X POST https://api.beeble.ai/v1/uploads \
  -H "x-api-key: $BEEBLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"filename": "clip.mp4"}')

UPLOAD_URL=$(echo "$UPLOAD_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin)['upload_url'])")
BEEBLE_URI=$(echo "$UPLOAD_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin)['beeble_uri'])")

# Upload file
curl -s -X PUT "$UPLOAD_URL" \
  -H "Content-Type: video/mp4" \
  --data-binary @/tmp/switchx-clip.mp4
```

For images, use the appropriate content type (`image/png`, `image/jpeg`).

### 4. Start generation

```bash
curl -s -X POST https://api.beeble.ai/v1/switchx/generations \
  -H "x-api-key: $BEEBLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"generation_type\": \"video\",
    \"source_uri\": \"$BEEBLE_URI\",
    \"alpha_mode\": \"auto\",
    \"max_resolution\": 1080,
    \"prompt\": \"YOUR PROMPT HERE\"
  }"
```

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `generation_type` | Yes | `"video"` or `"image"` |
| `source_uri` | Yes | Beeble URI from upload, or a public URL |
| `alpha_mode` | Yes | How to separate subject from background (see below) |
| `max_resolution` | No | `720` or `1080` (default varies) |
| `prompt` | No | Text describing desired output look |
| `reference_image_uri` | No | Beeble URI or public URL of a reference image for style guidance |
| `alpha_uri` | No | Required for `custom` alpha mode |
| `callback_url` | No | Webhook URL for completion notification |

**Alpha modes:**

| Mode | When to use |
|------|-------------|
| `auto` | Default. AI detects and preserves the foreground subject automatically. Best for most cases. |
| `fill` | Keep everything in the original scene, just transform lighting/style. No background replacement. |
| `select` | Provide a first-frame mask image; AI propagates it across the video. For precise subject selection. |
| `custom` | Provide a full frame-by-frame mask video. Maximum control. |

### 5. Poll for completion

```bash
JOB_ID="the id from step 4"
while true; do
  RESULT=$(curl -s "https://api.beeble.ai/v1/switchx/generations/$JOB_ID" \
    -H "x-api-key: $BEEBLE_API_KEY")
  STATUS=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin)['status'])")
  PROGRESS=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('progress',0))")
  echo "Status: $STATUS, Progress: $PROGRESS%"
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    echo "$RESULT" | python3 -m json.tool
    break
  fi
  sleep 10
done
```

### 6. Download outputs

A completed job returns three output URLs:

| Output | Description |
|--------|-------------|
| `render` | The final transformed video — this is what you deliver |
| `source` | The original re-encoded by Beeble (for comparison) |
| `alpha` | The mask showing what was kept vs replaced |

```bash
OUTPUT_DIR="/path/to/output"
mkdir -p "$OUTPUT_DIR"

RENDER_URL=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin)['output']['render'])")
SOURCE_URL=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin)['output']['source'])")
ALPHA_URL=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin)['output']['alpha'])")

curl -s -o "$OUTPUT_DIR/render.mp4" "$RENDER_URL"
curl -s -o "$OUTPUT_DIR/source.mp4" "$SOURCE_URL"
curl -s -o "$OUTPUT_DIR/alpha.mp4" "$ALPHA_URL"
```

## Prompt tips

The prompt describes how you want the output to look. Good prompts are specific about lighting and environment:

- **Studio look:** "Professional podcast studio with warm soft lighting, clean modern background with subtle neon accent lights, cinematic look"
- **Outdoor daylight:** "Bright natural daylight, outdoor park setting, soft shadows, golden hour warmth"
- **Stage performance:** "Concert stage with dramatic colored spotlights, haze, dark background, high contrast"
- **Clean corporate:** "Modern office with neutral lighting, white walls, minimalist background, even soft illumination"

Using a `reference_image_uri` alongside the prompt gives more precise control — upload a photo of the exact look you want.

## Processing longer videos

For videos over 240 frames, split into chunks, process each, then reassemble:

```bash
# Split into 8-second chunks (at 30fps = 240 frames)
ffmpeg -i long_video.mp4 -c copy -segment_time 8 -f segment -reset_timestamps 1 /tmp/chunk_%03d.mp4

# Process each chunk through steps 3-6...

# Reassemble (create file list first)
for f in /tmp/output_chunk_*.mp4; do echo "file '$f'"; done > /tmp/chunks.txt
ffmpeg -f concat -safe 0 -i /tmp/chunks.txt -c copy final_output.mp4
```

Note: chunk boundaries may have visible seams since each is processed independently. For best results, overlap chunks slightly and crossfade.

## Error handling

| Error | Meaning | Fix |
|-------|---------|-----|
| `VIDEO_TOO_MANY_FRAMES` | Over 240 frames | Trim or split the video |
| `SOURCE_TOO_LARGE` | File too big | Compress or reduce resolution before upload |
| `RATE_LIMIT_EXCEEDED` | Over 5 requests/min | Wait and retry with backoff |
| `CONCURRENT_LIMIT_EXCEEDED` | Over 10 in-flight jobs | Wait for running jobs to finish |
| `INSUFFICIENT_BALANCE` | Credits depleted | Top up at developer.beeble.ai |

## API reference

- **Base URL:** `https://api.beeble.ai/v1`
- **Auth:** `x-api-key` header
- **Docs:** `https://developer.beeble.ai/docs`
- **Status page:** `https://status.beeble.ai`
- **Rate limits:** 5 RPM write, 5 RPM read, 10 concurrent jobs
