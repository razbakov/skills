---
name: image-from-gemini
description: "Generate images using Google Gemini 3.1 Flash Image Preview API. Use when the user asks to generate, create, or make an image, illustration, poster design, mockup, thumbnail, or any visual asset using AI. Also trigger when the user mentions Nano Banana, Gemini image generation, or asks to visualize something as an image. This skill handles the full pipeline: API call, image extraction, and display."
---

# Gemini Image Generation

Generate images from text prompts using Google's Gemini 3.1 Flash Image Preview model via REST API.

## Requirements

- `GEMINI_API_KEY` environment variable (or set in `~/.zshrc`)
- `curl` and `python3` (standard on macOS/Linux)
- Get a key at https://aistudio.google.com/apikey

## Workflow

### 1. Run the generation script

Use the bundled script to generate the image. The script handles API key discovery, the API call, and image extraction automatically.

```bash
python3 ~/.claude/skills/image-from-gemini/scripts/generate.py \
  "your detailed image prompt here" \
  -o /path/to/output.png
```

### 2. Display the result

After generation, use the **Read tool** to display the image to the user:

- Read the generated PNG file — Claude's multimodal capability will render it inline

### 3. Iterate if needed

If the user wants changes, adjust the prompt and regenerate. Gemini responds well to detailed, specific prompts describing layout, colors, typography, and mood.

## Prompting tips

- Be specific about layout, colors, fonts, and mood
- For posters/designs with text: spell out every word exactly as it should appear
- Mention dimensions if relevant (e.g., "A3 portrait poster", "16:9 landscape banner")
- Gemini avoids contractions in rendered text — use "will not" instead of "won't" if text accuracy matters
- For dark backgrounds, specify hex colors for precision (e.g., "#1E1B2E")

## Available models

| Model                            | Best for                     |
| -------------------------------- | ---------------------------- |
| `gemini-3.1-flash-image-preview` | Fast, good quality (default) |
| `gemini-3-pro-image-preview`     | Higher quality, slower       |
| `gemini-2.5-flash-image`         | Older, still available       |

Switch models with the `-m` flag if the default doesn't produce the desired quality.

## Troubleshooting

- **"API key not found"** — Set `export GEMINI_API_KEY=your-key` in `~/.zshrc` and restart terminal
- **404 model not found** — List available models: `curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | python3 -c "import json,sys; [print(m['name']) for m in json.load(sys.stdin)['models'] if 'image' in m['name']]"`
- **No image returned** — The model may have refused the prompt. Try rephrasing or simplifying.
