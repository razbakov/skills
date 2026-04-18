---
name: event-flyer-pack
description: "Produce a print-ready Event Pack for a SPECIFIC upcoming event (has a date, venue, URL) using Gemini for the design and a real QR overlay. Builds 5+ assets — A6 flyer front/back, A4 4-up home-printable, DJ tent card, 1080×1920 Instagram story — by prompting Gemini to render each full asset (title, date, venue, price, dresscode, and QR *placeholder*) and then compositing a real scannable QR over the placeholder. Use when the user has a concrete event to promote (party, workshop, gig, pop-up, launch) and needs physical + digital promo together. For brand-only cards or single posters without an event, use brand-poster instead."
---

# Event Flyer Pack

One event → one set of Gemini prompts → five deliverables, each with a real scannable QR. The pack is the standard composition of `image-from-gemini` (each full asset, fully typeset by Gemini) + `qr-code-generator` (one real QR) + a minimal overlay step that replaces Gemini's drawn QR placeholder with the real one.

**Core workflow discovered on 2026-04-17 (Frida Cubana build):** Gemini renders gorgeous print assets with baked-in typography, but it cannot render a scannable QR — it produces decorative squares that look like QRs but do not encode anything. The fix is not to build a layout engine in Pillow, it's to let Gemini do the design and swap the fake QR for a real one.

## Trigger

Use when the user:
- Has a specific upcoming event (date, venue, entry, URL) and needs printed promo by a deadline.
- Asks for "flyers + QR," "table card for my gig," "promo pack," "ambience DJ set with my own promo," "party this weekend print material," etc.
- Says something like "*I need flyers for \<event\> tomorrow / next week*".

Do **not** use this skill for: brand-only cards (use `brand-poster`), single-channel IG graphics (use `image-from-gemini`), pure QR codes (use `qr-code-generator`).

## Deliverables (standard set)

| File | Size / aspect | Purpose |
|---|---|---|
| `<slug>-flyer-front.png` | A6 portrait (2:3), upscaled to 300 DPI | Vendor print master — front |
| `<slug>-flyer-back.png` | A6 portrait | Vendor print master — back |
| `<slug>-flyer-a4-4up-front.pdf` | A4 | Home printable 4-up + crop marks |
| `<slug>-flyer-a4-4up-back.pdf` | A4 | Home printable 4-up + crop marks |
| `<slug>-tent-card.png` | A6 portrait, top half mirrored 180° | DJ booth / bar table tent |
| `<slug>-instagram-story.jpg` | 1080×1920 | IG story / WhatsApp status |

All printed assets target **300 DPI** at A6 (1240×1748 px). Gemini outputs typically come at ~1024–2048 px on the long edge — upscale via `sips` or PIL resample before export if print sharpness matters.

## Required inputs

- **Event slug** — short filename prefix (e.g. `frida-cubana`).
- **Event title** (one or two lines).
- **Date** in the event's language + **time window** + **venue** + **entry price**.
- **Event URL** — the single URL encoded into every QR. Keep short (< 50 chars) so the QR stays readable at 18 mm print.
- **Style / program line** (optional — "Timba · Son · Rumba Cubana").
- **Highlights** (optional — for the back: "Free shot", "Domino table").
- **Dresscode / pull quote** (optional, 1 line).
- **DJ / host name** (optional).
- **Brand language** — what aesthetic Gemini should render (e.g. "warm Cuban editorial", "90s rave poster", "minimalist Scandinavian").
- **Language** — copy language (de, en, es, ru).
- **Output directory** — local path for the generated files.

## Process

For each of the 5 asset types, execute the same 3-step recipe:

### Step 1 — Generate the full asset with Gemini

Invoke skill **image-from-gemini** with a prompt that includes:

- Full event copy (title, date, venue, entry, program, dresscode, DJ).
- Target aspect ratio (2:3 portrait for A6, 9:16 for IG story, tent card has **two mirrored halves**).
- Brand aesthetic.
- **Explicit QR placeholder instruction**: `"leave a clean solid-white square, roughly 20–25% of the short edge, in the {bottom-center | bottom-right | specified area} of the design, for a QR code overlay. Do not render a QR pattern — leave the square empty white."`

Prompt templates per asset: see `assets/templates/gemini_prompts.md`.

### Step 2 — Generate the real QR

Invoke skill **qr-code-generator** with:
- the event URL
- error correction H
- black on white
- size: aim for `target_qr_side_px = short_edge_px * 0.22` (roughly 20–24 mm at print scale for A6; ~360 px for IG story)

### Step 3 — Composite the QR over Gemini's placeholder

Detect the white placeholder square in the Gemini output (either by eye + manual coordinates, or by simple color-threshold detection — see `scripts/overlay_qr.py`). Paste the QR there, preserving a small white quiet-zone margin (≥ QR/18) around it.

**Verify the composite scans** — reload the output PNG with any QR detector (OpenCV's `QRCodeDetector`, pyzbar, or a phone) and assert the decoded URL matches the event URL. For multi-QR sheets (A4 4-up, tent card with mirrored halves), crop each QR region and test individually — single-code detectors return "NO DECODE" when two identical codes share one frame.

See `qr-code-generator`'s "Embedding QR codes inside a larger composition" section for the full embedding checklist.

## Hard-learned rules (from the Frida Cubana build)

1. **Gemini will draw a fake QR even if you ask it not to.** It renders something that looks like a QR — black-and-white modules in a square — but it encodes nothing. Always overlay a real one. This is the entire reason this skill exists.
2. **Tell Gemini exactly where the placeholder goes.** Ambiguous instructions ("include a QR") → the fake QR ends up in random positions across retries, making overlay coordinates non-reproducible. Pin it: *"in the bottom center, 20% from the bottom edge, a 200×200 px pure-white square."*
3. **Shorten URLs before generating.** A URL over ~50 chars forces a denser QR grid; below 18 mm print it stops scanning. Use a short event URL (e.g. wedance.vip/events/\<id\>), not a full UTM-laden campaign link — put UTMs on the landing page.
4. **One event ≠ one Gemini call.** Each asset (flyer front, back, tent, IG story) is a separate prompt. They share copy and aesthetic but differ in aspect ratio and emphasis. Don't try to make Gemini output all 5 in one go.
5. **Generate 2 variants per asset, pick one.** Gemini's compositional variance is high — the second attempt is often dramatically better. Budget 10–15 seconds per retry.
6. **For the tent card, generate each half separately** (wine-red top, navy bottom, both with the same copy), then mirror the top 180° and stack. Gemini cannot reliably render a single image with one half rotated.

## Output format (required when reporting back)

- 5–6 files produced with local paths.
- QR verification results per asset (expected URL + pass/fail).
- Per-asset note: which Gemini variant was picked and why.
- Delivery checklist (see `assets/templates/delivery_checklist.md`).

## Bundled assets

- `assets/templates/gemini_prompts.md` — prompt templates for flyer front, flyer back, tent card halves, IG story. Each has `{placeholders}` that the caller fills in from the event spec.
- `assets/templates/event_spec_example.json` — the Frida Cubana inputs as a concrete example.
- `assets/templates/gemini_hero_prompt.md` — historical reference; skip unless generating a hero-only asset.
- `assets/templates/delivery_checklist.md` — what to print, how many, where to place.
- `scripts/overlay_qr.py` — **thin** helper that takes a Gemini output PNG + a QR PNG + placeholder coordinates (or auto-detect) and writes the composite. ~40 lines. Deliberately minimal — this skill does not own layout, Gemini does.

## Delegation

- Hero / full asset art → **image-from-gemini** (5 calls, one per asset).
- QR code → **qr-code-generator** (1 call, reused across all 5 composites).
- Brand-wide style decisions (palette, typography voice) → **brand-poster** if the event doesn't yet have a visual language.
