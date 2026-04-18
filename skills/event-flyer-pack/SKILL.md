---
name: event-flyer-pack
description: "Produce a print-ready Event Pack for a SPECIFIC upcoming event (has a date, venue, URL). Builds 5+ assets from one hero image: A6 flyer front/back with bleed, A4 4-up home-printable, DJ tent card with mirrored top half, and a 1080×1920 Instagram story — all sharing one verified QR code. Use when the user has a concrete event to promote (party, workshop, gig, pop-up, launch) and needs physical + digital promo together. For brand-only cards or single posters without an event, use brand-poster instead."
---

# Event Flyer Pack

One event → one hero image → five deliverables, all vendor-ready. The pack is the standard composition of `image-from-gemini` (hero art) + `qr-code-generator` (event QR) + `brand-poster` (layout), wired together by a single Python build script.

## Trigger

Use when the user:
- Has a specific upcoming event (date, venue, entry, URL) and needs printed promo by a deadline.
- Asks for "flyers + QR," "table card for my gig," "promo pack," "ambience DJ set with my own promo," "party this weekend print material," etc.
- Says something like "*I need flyers for \<event\> tomorrow / next week*".

Do **not** use this skill for: brand-only cards (use `brand-poster`), single-channel IG graphics (use `image-from-gemini`), pure QR codes (use `qr-code-generator`).

## Deliverables (standard set)

| File | Size | Purpose |
|---|---|---|
| `<slug>-flyer-front-bleed.pdf/png` | A6 + 3 mm bleed (111×154 mm) | Vendor print master — front |
| `<slug>-flyer-back-bleed.pdf/png` | A6 + 3 mm bleed | Vendor print master — back |
| `<slug>-flyer-a4-4up-front.pdf/png` | A4 | Home printable 4-up + crop marks |
| `<slug>-flyer-a4-4up-back.pdf/png` | A4 | Home printable 4-up + crop marks |
| `<slug>-tent-card-bleed.pdf/png` | A6 + bleed, top half mirrored 180° | DJ booth / bar table tent |
| `<slug>-instagram-story.jpg` | 1080×1920 | IG story / WhatsApp status |

Resolution: **300 DPI** for all print assets. Color space: sRGB (home printers + most local print shops accept; convert to CMYK only if vendor asks).

## Required inputs

Collect these before building. If anything is missing, ask once and stop — don't invent.

- **Event slug** — short filename prefix (e.g. `frida-cubana`).
- **Event title** — main headline (supports two-line split).
- **Date** (human-readable, localized to event language) + **time window**.
- **Venue** (short name + city).
- **Entry** (price or "free").
- **Event URL** — the one URL that encodes into every QR. Keep it short (<50 chars) so the QR module density stays scannable at 18 mm.
- **Short style/program** line (e.g. "Timba · Reparto · Son").
- **Highlights** (optional, 2–3 short items for back of flyer).
- **Dresscode / pull-quote** (optional, goes in pill callout).
- **DJ / host name** (optional).
- **Language** (de / en / es / ru — affects date format and fallback copy).
- **Hero art** — either an existing image path, or a Gemini prompt if it needs generating.
- **Brand palette** — cream/terracotta/gold/navy/ink hexes (defaults in `assets/templates/palette_default.json`).
- **Output directory** — where the `print/` folder gets written. Upload to a canonical print destination (print shop, Drive folder, vendor portal) is the caller's responsibility, not the skill's.

## Process

1. **Generate hero art** (if not provided). Delegate to `image-from-gemini` with a prompt that **leaves the bottom third empty** (low contrast, dark space) for copy overlay. Generate 2 options, pick the one with more overlay space.
2. **Build the QR** via `qr-code-generator` with ECC-H, 4-module border. Size:
   - Flyer front: **22 mm** square.
   - Tent card: **24 mm** square (read from ~1 m at the booth).
   - IG story: **360 px** square.
3. **Compose each asset** with `scripts/build_flyer_pack.py`. The script enforces:
   - Bottom-margin-first layout (QR anchored `mm(8–10)` from canvas bottom, content flows above).
   - White quiet-zone card behind every QR (padding ≥ QR/18).
   - Crop marks on A4 4-up sheets.
   - Top half of tent card mirrored 180° (readable when folded at the equator).
4. **Verify QR scans.** Reload each PNG with `cv2.QRCodeDetector` and assert decoded URL == event URL. For sheets with multiple identical QRs (4-up, tent card), crop each region individually — cv2's single-code detector returns NO DECODE when two identical codes are in one frame even though each scans fine on a phone.
5. **Preview.** Show front, back, tent card, and IG story to the user before upload. Catch visual issues (text clipping hero, pill overlapping QR) that QR-scan verification won't catch.
6. **Upload.** If the user has a canonical print folder (e.g. Google Drive via `gog drive upload --parent=<folder_id>`), upload the PDFs + IG story JPG. Leave PNGs as local previews only.

## Hard-learned rules

1. **Layout overflow is the #1 cause of unscannable QRs.** If the QR top+size exceeds `canvas_height - safe_margin`, the QR gets clipped off the bottom. Anchor the QR to the canvas bottom *first*, then lay out above. See `qr-code-generator` SKILL for the full embedding checklist.
2. **Shorten URLs before generating.** A URL over ~50 chars forces a denser QR grid; below 18 mm print it stops scanning. Use a short event URL (e.g. wedance.vip/events/\<id\>) not a full campaign URL with UTMs. Put UTMs on the landing page, not the print QR.
3. **Never upload raw `.md`/`.txt` to the print folder** (per user's print-folder rule). Only print-ready PDFs/PNGs/JPGs. Notes go to a Google Doc (`gog drive upload --convert-to=doc`).
4. **One hero across all 5 assets** keeps the pack coherent. Don't generate five different images.
5. **Top half of tent card is rotated 180°.** When the card is folded at the midline and stood up, both sides read correctly from opposite sides of the table.

## Output format (required)

- Summary of 5–6 files produced with Drive/local links.
- QR verification results (expected URL, per-asset pass/fail).
- Any copy changes made to fit the layout (e.g. dropped line, shortened headline).
- Delivery checklist: how many sheets to print, where to stand the tent card, when to post IG story.

## Scripts & templates

- `scripts/build_flyer_pack.py` — main builder. Takes a JSON event spec + hero image + output dir → emits 10+ files (PNG + PDF for each size). Builds flyer front, flyer back, tent card, A4 4-up (both sides), and IG story.
- `assets/templates/event_spec_example.json` — concrete example input (copy + edit; don't edit the template in place).
- `assets/templates/gemini_hero_prompt.md` — hero-image prompt template (leaves bottom third dark for overlay).
- `assets/templates/delivery_checklist.md` — what to print, how many, where to place.

## Platform assumptions

The reference script uses macOS system fonts (`/System/Library/Fonts/Supplemental/Didot.ttc`, `Baskerville.ttc`, `HelveticaNeue.ttc`). On Linux or in Docker, override via the `FONT_PATHS_OVERRIDE` environment variable (JSON object mapping `didot` / `baskerville` / `helvetica` to local font file paths) or edit the `FONT_PATHS` dict at the top of the script. Color space is sRGB; convert to CMYK only if the vendor specifically asks.

## Delegation

- Hero art → invoke skill **image-from-gemini** with the template prompt.
- QR code → invoke skill **qr-code-generator** (read its "Embedding QR codes inside a larger composition" section first).
- Base layout engineering → invoke skill **brand-poster** if the event needs a non-standard layout (multi-page booklet, roll-up banner, etc.).
