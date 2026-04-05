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
