---
name: qr-code-generator
description: Generate QR codes with URLs and UTM tracking. Exports PNG/SVG with captions. Supports styled QR codes with custom module shapes (rounded, circle, gapped, bars), colors, gradients (radial, square, horizontal, vertical), and logo overlay. Use for single codes, batch generation, or marketing campaigns with tracking parameters.
---

# QR Code Generator

## What this skill does
Given a URL, this skill generates:
- a QR code that **encodes the URL**
- optional **styled modules** (rounded dots, circles, gapped squares, bars)
- optional **custom colors** and **gradients** (radial, square, horizontal, vertical)
- optional **logo overlay** centered in the QR code
- optional captions (human-readable URL or short label)
- exports in PNG and/or SVG
- optional batch runs from a CSV

## Guardrails
- Don't generate QR codes for suspicious links (phishing, credential prompts, malware). If unsure, ask for confirmation or suggest a safer destination page.
- Prefer HTTPS URLs.
- If the QR is for print, prefer **SVG** (scales cleanly) and **high error correction**.
- When using a logo, auto-upgrade error correction to **H**.
- Styled output (shapes, colors, gradients, logo) is **PNG only** — SVG uses basic rendering.

## Embedding QR codes inside a larger composition (flyers, cards, posters)

When the QR is composited into a bigger canvas (Pillow, brand-poster, event-flyer-pack), four rules keep it scannable:

1. **Reserve the bottom margin first.** Position the QR relative to the canvas *bottom edge*, not by stacking content top-down. Target: QR bottom sits at `H - safe_margin` (e.g. `mm(8)` to `mm(10)` for print). Then lay out the rest *above* it. Most scan failures in composite designs are QR overflow off the canvas, not encoding problems — the QR image is generated fine but placed partially outside the bounds.
2. **Always verify `qr_top + qr_size <= canvas_height - safe_margin` before saving.** If it fails, shrink the QR or reflow the block above. Do not silently export an overflowing design.
3. **Post-build decode check.** After export, reload the PNG with any QR detector (e.g. OpenCV's `QRCodeDetector`, `pyzbar`, or an equivalent) and assert it returns the expected URL. For sheets with *multiple identical QRs* (A4 4-up, tent cards with mirrored halves) single-code detectors often return NO DECODE — not because the QRs are broken but because they can't disambiguate two identical codes in one frame. Crop each QR region and test individually.
4. **White quiet-zone card behind the QR.** Always composite a white rectangle under the QR with padding ≥ `qr_size / 18` (3–4 module widths) even if the canvas background is light. Printers darken edges; phone cameras need the contrast.

Minimum print sizes that reliably scan from arm's length (~30-50 cm):
- Business card / flyer corner: **18–22 mm** square
- Poster / DJ tent card (read from 1-2 m): **24–32 mm**
- Large venue signage (read from 3+ m): **50+ mm**

URL length matters: for a 40-char URL at ECC-H, the QR grid is ~37×37 modules — below 18 mm print the modules blur. Shorten the URL (custom short domain) if you need a smaller QR.

## Inputs
Required:
- URL

Optional:
- label/caption text (e.g., "Scan to book a call")
- whether to show the URL under the QR (yes/no)
- output formats: PNG, SVG
- UTM params (source, medium, campaign, content, term)
- size intent: screen / print / sticker
- **style**: module shape — `square` (default), `rounded`, `circle`, `gapped`, `vertical-bars`, `horizontal-bars`
- **fg**: foreground color (hex, e.g. `#E5383B`)
- **bg**: background color (hex, e.g. `#FFFFFF`)
- **gradient**: type — `radial`, `square`, `horizontal`, `vertical`
  - radial/square: `--gradient-center` and `--gradient-edge` colors
  - horizontal: `--gradient-left` and `--gradient-right` colors
  - vertical: `--gradient-top` and `--gradient-bottom` colors
- **logo**: path to image file to embed in the center

## Workflow
1) Validate the URL (scheme + domain).
2) Optionally append UTM parameters (using `assets/templates/utm_template.json`).
3) Generate QR:
   - Error correction: M (default), H for print/logo/complex usage
   - Border: 4 (default)
4) Apply styling (PNG only):
   - Module drawer for dot shape
   - Color mask for solid colors or gradients
   - Embedded image for logo overlay
5) Export:
   - PNG (good for web, supports all styling)
   - SVG (best for print, basic style only)
6) If caption enabled:
   - PNG: add label and/or URL under the QR
   - SVG: add a text element under the QR
7) Return links + a quick "usage notes" block (recommended minimum size, print tips).

## Output format (required)
- Encoded URL (final URL after UTM, if used)
- Files generated (with links)
- Recommendations (error correction, min size, when to use SVG vs PNG)

## Scripts in this pack
- `scripts/generate_qr.py` — single QR (PNG/SVG, optional caption, styled modules, colors, gradients, logo)
- `scripts/batch_generate.py` — batch from CSV (id,url,label)

## Templates
- `assets/templates/utm_template.json`
- `assets/templates/print_notes.md`
- `assets/templates/prompt_snippets.md`
