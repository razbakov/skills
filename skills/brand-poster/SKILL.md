---
name: brand-poster
description: "Generate poster images. Use when the user asks to create a poster, flyer, print material, social media graphic, or any visual marketing asset"
---

# Brand Poster

Create on-brand visual assets (posters, flyers, table tents, social graphics) using a structured process.

## Required inputs

- **Brand guidelines** — colors, fonts, logo, tone of voice
- **Campaign brief** — placement strategy, copy, design specs, target dimensions
- **Technique** — choose one:
  - `image-from-html` — deterministic, version-controlled, pixel-perfect (best for print and complex layouts)
  - `image-from-latex` — vector-sharp typography and geometric graphics (best for thumbnails, diagrams, bold text designs)
  - `image-from-gemini` — AI-generated from a text prompt (best for illustrations, creative visuals, quick mockups)

## Process

1. **Gather inputs** — Confirm brand guidelines and campaign brief are available
2. **Choose technique** — Select based on the output requirements (see above)
3. **Design** — Create the asset using the chosen technique skill
4. **Review** — Show the result to the user for feedback
5. **Iterate** — Refine based on feedback until approved
6. **Deliver** — Provide final files (source + exported image)

## File naming convention

```
docs/posters/{poster-type}-{variant}.html    → source (html technique)
docs/posters/{poster-type}-{variant}.tex     → source (latex technique)
docs/posters/{poster-type}-{variant}.png     → exported image
```

## Technique delegation

- For `image-from-html`: invoke skill **image-from-html**
- For `image-from-latex`: invoke skill **image-from-latex**
- For `image-from-gemini`: invoke skill **image-from-gemini**
