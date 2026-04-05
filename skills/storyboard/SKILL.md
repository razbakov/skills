---
name: storyboard
description: Generate visual storyboards for video ads, product demos, and marketing videos. Creates a grid of frames with captions using Gemini image generation.
triggers:
  - create a storyboard
  - storyboard for
  - video ad concept
  - shot list
  - video frames
---

# Storyboard Generator

Generate visual storyboards for video concepts using Gemini image generation.

## Process

### 1. Gather context

Before generating, establish:
- **Product/brand** — what's being advertised
- **Video angle** — the story or concept (e.g. "dead time", "before/after", "day in the life")
- **Target audience** — who watches this
- **Duration** — determines number of frames (15s = 3-4 frames, 30s = 5-6 frames, 60s = 8-10 frames)
- **Visual style** — cinematic, minimalist, illustrated, iPhone-shot, etc.
- **Platform** — YouTube, X/Twitter, LinkedIn, TikTok (affects aspect ratio and pacing)

### 2. Write the frame descriptions

Plan each frame before generating:
- **Frame number + timing** (e.g. "Frame 1 (0-5s)")
- **Visual description** — what's on screen, camera angle, setting
- **Text overlay** — any words shown on screen
- **Audio note** — voiceover, music mood, sound effects

### 3. Generate storyboard grid

Use the `image-from-gemini` skill:

```bash
python3 ~/.claude/skills/image-from-gemini/scripts/generate.py \
  "<prompt>" \
  -o /tmp/<project>-storyboard.png
```

**Prompt template:**

```
A cinematic storyboard grid, <rows> rows x <cols> columns, <total> frames total,
for a <duration>-second video ad. <visual style>. Each frame has a small white
number in the corner (1-<total>) and a one-line caption below.

Frame 1: <detailed visual description>
Frame 2: <detailed visual description>
...

Style: <realistic/illustrated/minimalist>. Like frames from <reference style>.
<lighting and mood>.
```

**Grid sizing guide:**
- 3-4 frames: 1 row x 3-4 cols
- 5-6 frames: 2 rows x 3 cols
- 8-10 frames: 2-3 rows x 3-4 cols

### 4. Review and iterate

- Open the image for full-size review
- Discuss which frames work and which need adjustment
- Regenerate with updated descriptions if needed
- Use `-i` flag to pass previous storyboard as reference for consistency

### 5. Write the full script

After visual approval, produce a script document with:
- Frame-by-frame timing
- Voiceover lines (exact words)
- On-screen text
- Music/sound cues
- Camera directions

Save to the project's marketing folder.

## Tips

- Be specific about camera angles: "over-the-shoulder", "close-up", "wide shot"
- Mention lighting: "morning light", "blue hour", "overhead fluorescent"
- Include props and wardrobe details for consistency across frames
- For product UI shots, describe the screen content explicitly
- Reference real film styles: "iPhone-shot indie commercial", "Apple product video", "Wes Anderson framing"
- Always include the product name and URL in the final CTA frame
- For phone screens, describe what the UI shows — Gemini renders text and UI elements well at this scale
