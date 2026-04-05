---
name: logo-generator
description: Generate logo concepts using Gemini image generation. Creates a 3x3 grid of variations for review, then iterates on the chosen direction.
triggers:
  - create a logo
  - generate logo
  - logo concepts
  - brand logo
  - logo variations
---

# Logo Generator

Generate logo concepts as a 3x3 grid using Gemini, review with user, iterate on chosen direction.

## Process

### 1. Gather context

Before generating, establish:
- **Product name** — the text that appears in the logo
- **What it does** — one sentence (drives icon/symbol choices)
- **Brand personality** — modern/classic, playful/serious, technical/approachable
- **Color palette** — specific hex codes if available, or mood (dark, vibrant, etc.)
- **Symbol ideas** — relevant icons, metaphors, or visual concepts

### 2. Generate 3x3 grid

Use the `image-from-gemini` skill to generate 9 distinct logo variations in a single image:

```bash
python3 ~/.claude/skills/image-from-gemini/scripts/generate.py \
  "<prompt>" \
  -o /tmp/<product>-logos.png
```

**Prompt template:**

```
Generate a 3x3 grid of 9 different logo concepts for "<Product Name>" — <one-line description>.
Each logo should be distinct: try combinations of <symbol ideas> and the word "<Product Name>"
in different typographic treatments. Use a <dark/light> background (<hex>) with <accent color>
(<hex>) accents. Clean, minimal, suitable for a SaaS product. Each cell in the grid should be
clearly separated with thin lines.
```

### 3. Display and discuss

- Read the generated PNG to show it inline
- Open it with `open /tmp/<product>-logos.png` for full-size view
- Give an opinion on which works best and why (distinctiveness, scalability, clarity)
- Let the user pick a direction

### 4. Iterate on chosen concept

Once the user picks a favorite, generate focused variations:

```
Generate 9 variations of this logo concept for "<Product Name>": <description of chosen concept>.
Vary the proportions, line weight, icon placement, and typography. Keep the same color palette.
Show as a 3x3 grid on <background color>.
```

### 5. Export final logo

Once approved, generate the final logo as a standalone image (no grid):

```
Generate a clean logo for "<Product Name>": <final description>.
Output on a transparent/dark background, centered, with generous padding.
High quality, suitable for use as a website header logo.
```

Save to the project's assets folder (e.g., `avatars/`, `public/`, or `assets/`).

## Tips

- Always specify background color as hex — Gemini respects this
- Mention "suitable for favicon" if it needs to work at small sizes
- For dark products, specify both dark bg version and light bg version
- Include "no text" if you want icon-only variations
- Gemini handles typography better with simple, short words
