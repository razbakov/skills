---
name: image-from-gemini
description: "Generate images using Google Gemini API. Use when the user asks to generate, create, or make an image, illustration, poster design, mockup, thumbnail, or any visual asset using AI. Supports uploading reference photos for poster/flyer generation with real people. Also trigger when the user mentions Gemini image generation or asks to visualize something as an image."
---

# Gemini Image Generation

Generate images from text prompts using Google's Gemini API, optionally with uploaded reference photos.

## Requirements

- `GEMINI_API_KEY` environment variable (or set in `~/.zshrc`)
- `python3` (standard on macOS/Linux)
- Get a key at https://aistudio.google.com/apikey

## Workflow

### 1. Text-only generation

```bash
python3 ~/.claude/skills/image-from-gemini/scripts/generate.py \
  "your detailed image prompt here" \
  -o /path/to/output.png
```

### 2. Photo-to-poster generation

Upload one or more reference photos. Gemini will incorporate the people into the generated design.

```bash
# Single photo
python3 ~/.claude/skills/image-from-gemini/scripts/generate.py \
  -i /path/to/person.jpg \
  "Square Instagram post. Place the person from the photo as the hero..." \
  -o /path/to/output.png

# Multiple photos
python3 ~/.claude/skills/image-from-gemini/scripts/generate.py \
  -i /path/to/person1.jpg \
  -i /path/to/person2.jpg \
  -i /path/to/person3.jpg \
  "Instagram story with all uploaded people as instructors..." \
  -o /path/to/output.png
```

### 3. Display and iterate

After generation, use the **Read tool** to display the image inline. Adjust the prompt and regenerate as needed.

### 4. Batch generation (multiple styles)

For generating multiple variants, use Python directly to avoid repeated shell calls:

```python
python3 << 'EOF'
import base64, json, os, urllib.request

api_key = os.environ.get("GEMINI_API_KEY")
model = "gemini-3.1-flash-image-preview"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

with open("photo.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

prompts = {
    "v1-style": "prompt for style 1...",
    "v2-style": "prompt for style 2...",
}

for name, prompt in prompts.items():
    payload = {
        "contents": [{"parts": [
            {"inlineData": {"mimeType": "image/jpeg", "data": img_b64}},
            {"text": prompt}
        ]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=180)
    result = json.loads(resp.read())
    for candidate in result.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if "inlineData" in part:
                img_data = base64.b64decode(part["inlineData"]["data"])
                with open(f"output-{name}.png", "wb") as f:
                    f.write(img_data)
                break
EOF
```

## Photo-to-poster prompting tips

When uploading photos of real people for event posters:

- Say "Place the person from the photo" — Gemini understands the reference
- Say "remove the original background" — Gemini will cut out the person
- Use `rembg` (Python) beforehand for cleaner cutouts if needed: `uvx --with "rembg[cpu,cli]" rembg i input.jpg output.png`
- Specify exact text: spell out every word, every number, every address
- Repeat critical text in the prompt (addresses, URLs) to avoid hallucination
- Say "DO NOT include any logo" if you plan to overlay it later with HTML
- For multiple photos, upload all and number them: "Photo 1: Name1, Photo 2: Name2"

## Style presets

Proven styles for event/dance posters:

| Style | Description | Best for |
|-------|------------|----------|
| **Neon** | Dark bg, neon pink/cyan streaks, nightclub vibe | Club events, parties |
| **Cuban** | Cuban flag colors, distressed texture, palm shadows, Havana aesthetic | Latin dance, cultural events |
| **Minimal** | Black bg, gold circle frame, Swiss typography | Premium/luxury feel |
| **Fire** | Flames, sparks, dramatic lighting from below | High-energy concerts, competitions |
| **Warm bokeh** | Burgundy/maroon, golden bokeh lights | Warm, inviting classes |

## General prompting tips

- Be specific about layout, colors, fonts, and mood
- For posters with text: spell out every word exactly as it should appear
- Mention dimensions: "Square 1080x1080" or "Portrait 1080x1920"
- Gemini avoids contractions — use "will not" instead of "won't"
- For dark backgrounds, specify hex colors (e.g., "#1E1B2E")

## Available models

| Model | Best for |
|-------|----------|
| `gemini-3.1-flash-image-preview` | Fast, good quality (default) |
| `gemini-3-pro-image-preview` | Higher quality, slower |

## Troubleshooting

- **"API key not found"** — Set `export GEMINI_API_KEY=your-key` in `~/.zshrc`
- **404 model not found** — List models: `curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | python3 -c "import json,sys; [print(m['name']) for m in json.load(sys.stdin)['models'] if 'image' in m['name']]"`
- **Argument list too long** — The script uses `urllib` internally, not `curl`. If using the API directly, avoid `subprocess` with large base64 payloads.
- **500 Internal Server Error** — Image may be too small or corrupted. Use the original full-resolution photo, not a tiny crop.
- **No image returned** — Rephrase or simplify the prompt. Gemini may refuse certain compositions.
