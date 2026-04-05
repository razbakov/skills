---
description: Generate videos using Google Veo via Gemini API. Use when the user asks to generate, create, or make a video, animation, clip, or motion content from text or images using AI. Triggers include 'generate a video', 'make a video of', 'animate this image', 'create a clip', 'video from image', or when the user wants to bring a still image to life.
---

# Video Generation with Google Veo

Generate videos from text prompts or images using Google's Veo model via the Gemini REST API.

## Requirements

- `GEMINI_API_KEY` environment variable (same key as image-from-gemini)
- `curl` and `python3` (standard on macOS/Linux)

## Workflow

### 1. Run the generation script

**Text-to-video:**
```bash
source ~/.zshrc; python3 ~/.claude/skills/video-from-gemini/scripts/generate.py \
  "your detailed video prompt here" \
  -o /tmp/output.mp4
```

**Image-to-video (animate a still image):**
```bash
source ~/.zshrc; python3 ~/.claude/skills/video-from-gemini/scripts/generate.py \
  "description of the motion and camera movement" \
  -i /path/to/input.png \
  -o /tmp/output.mp4
```

**Important:** Always `source ~/.zshrc` before running to load the API key.

### 2. Open the result

```bash
open /tmp/output.mp4
```

The video is an MP4 file. Use `open` on macOS to play it in the default video player.

### 3. Iterate if needed

Adjust the prompt and regenerate. Veo responds well to:
- Specific camera movements: "slow orbit", "push in", "dolly zoom"
- Lighting descriptions: "warm golden hour", "dramatic side lighting"
- Motion descriptions: "gracefully spinning", "walking slowly forward"
- Style cues: "cinematic", "documentary", "dreamy"

## Script options

| Flag | Default | Description |
|------|---------|-------------|
| `-i` / `--image` | none | Input image for image-to-video |
| `-o` / `--output` | `/tmp/veo-output.mp4` | Output file path |
| `-m` / `--model` | `veo-3.1-generate-preview` | Model name |
| `-d` / `--duration` | `8` | Duration in seconds (4-8) |
| `-a` / `--aspect-ratio` | `16:9` | Aspect ratio (`16:9` or `9:16`) |
| `-t` / `--timeout` | `300` | Max wait time in seconds |

## Available models

| Model | Best for |
|-------|----------|
| `veo-3.1-generate-preview` | Best quality, audio support (default) |
| `veo-2.0-generate-001` | Faster, good quality fallback |

## Notes

- Generation takes ~60 seconds typically
- Output is MP4, usually 4-8MB for 8 seconds
- The script auto-retries with veo-2.0 if veo-3.1 fails
- Image-to-video preserves the visual style of the input image
- For vertical video (Shorts/Reels), use `-a 9:16`
