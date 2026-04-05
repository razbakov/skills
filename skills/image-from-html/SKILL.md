---
name: image-from-html
description: "Generate images from self-contained HTML/CSS designs. Use when the user wants a reproducible, code-first pipeline to produce print or social graphics (posters, flyers, ads) from HTML and screenshot automation."
---

# HTML-to-Image Technique

Use this skill when you need pixel-perfect output, brand-accurate typography, and a reproducible pipeline for producing print/social collateral from code.

## When to use

- The design must match brand guidelines exactly (fonts, spacing, colors)
- You need a reproducible, version-controlled source file (HTML + CSS)
- You want a deterministic workflow that can be regenerated or automated
- You need print-quality output (300 DPI) from a simple source format

## Requirements

- A self-contained HTML file (inline CSS, embedded fonts/assets)
- A modern browser (Chrome/Chromium) or headless browser tool (Puppeteer/Playwright)
- Target dimensions (e.g., A4, social size) expressed in CSS (mm, px)

## Workflow (high level)

1. **Build the HTML source**
   - Use inline CSS and embedded assets (SVG or base64)
   - Set exact dimensions using CSS `width`/`height` in `mm` or `px`
   - Import brand fonts via `@import` or inline font definitions

2. **Preview in a browser**
   - Open the HTML at 100% zoom and confirm spacing, typography, and layout

3. **Capture a high-resolution screenshot**
   - Use a headless browser to export a PNG at 2×/3× scale for 300 DPI (print)
   - Optionally use Puppeteer/Playwright for scripted exports in a pipeline

4. **Deliver outputs**
   - Provide the source HTML (version-controlled) and exported PNG/JPG
   - Optionally provide a template version for reuse and updates

## Helpful patterns

- Keep layout logic simple (flexbox/grid) so it renders consistently across browsers
- Prefer SVG for logos and icons to avoid raster artifacts when scaling
- When embedding QR codes, use inline SVG so you can regenerate them programmatically

## Slide Deck Pattern (HTML → PDF presentation)

For branded presentations, create one HTML file with multiple `.slide` divs (1280x720px each). Then capture each slide individually and combine into a PDF.

**HTML structure:**
```html
<div class="slide dark"><!-- navy background slide --></div>
<div class="slide light"><!-- white background slide --></div>
```

**Capture script (Python):**
```python
# For each slide, inject CSS that hides all others via nth-child
for i in range(num_slides):
    single_html = html.replace('</head>', f"""<style>
  body {{ margin:0 !important; overflow:hidden !important; }}
  .slide {{ display:none !important; }}
  .slide:nth-child({i+1}) {{ display:block !important; }}
</style></head>""")
    # Write to temp file, screenshot with Chrome headless
    # --window-size=1280,720 --force-device-scale-factor=2

# Combine PNGs into PDF with img2pdf
import img2pdf
with open('deck.pdf', 'wb') as f:
    f.write(img2pdf.convert(png_list))
```

**Key rules for slide decks:**
- Use 1280x720px per slide (16:9, standard presentation)
- Alternate dark/light slides for visual rhythm
- All content must fit within 720px height — no scrolling
- Use `overflow: hidden` on `.slide` to catch clipping issues during preview
- Never use Chrome's `--print-to-pdf` for slides — it uses A4 paper size and breaks layout

## Example screenshot command (Chrome headless)

```bash
# A4 poster at 300 DPI (210mm × 297mm → 2480 × 3508px at 300dpi)
google-chrome --headless --screenshot=poster-b.png \
  --window-size=2480,3508 \
  --force-device-scale-factor=1 \
  poster-b.html
```
