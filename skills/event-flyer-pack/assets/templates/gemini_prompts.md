# Gemini prompt templates — per asset

Each template has `{placeholders}` to be filled from the event spec. Feed to **image-from-gemini** one at a time. Generate 2 variants per asset and keep the better one.

General rules:
- Always end with the QR-placeholder instruction verbatim — Gemini ignores soft requests.
- Describe the **aesthetic** in 2–3 concrete adjectives ("warm editorial, cinematic, 1950s Havana"), not generic words ("beautiful, professional").
- Forbid text features you don't want: `NO logos, NO watermarks, NO stock-photo vibe, NO generic fonts`.

---

## Flyer FRONT (A6 portrait, 2:3)

```
A vertical 2:3 portrait print flyer for "{title}" — {aesthetic}.

Copy to render (typeset cleanly, editorial layout, serif display face for the
title, legible at A6 print size):
  - Eyebrow (small, top, letter-spaced): "{eyebrow}"
  - Title (large, serif display, can break into 2 lines): "{title_line1}" / "{title_line2}"
  - Tagline (italic, small, under title): "{tagline}"
  - Date (mid-size serif): "{date}"
  - Time · Venue · Entry (one line, sans-serif): "{time} · {venue} · {entry}"
  - Program (small, spaced): "{program}"
  - Dresscode pill (if given, terracotta rounded rectangle with cream text): "{dresscode}"
  - DJ / host (italic, small): "{dj}"

Scene: {scene_description — crowd, venue, mood, era}. The scene sits behind
the copy with a dark vignette so all text reads cleanly.

QR PLACEHOLDER — CRITICAL:
In the bottom-center of the flyer, 8% above the bottom edge, render a
SOLID PURE-WHITE SQUARE occupying 22% of the flyer width. LEAVE IT EMPTY —
do NOT render any QR modules, dots, patterns, or pixels inside it. Just a
blank white square. A real QR will be composited on top later.

Constraints: NO placeholder text like "SCAN ME", NO logos, NO watermarks.
Typography must be sharp and print-ready. No hands holding phones.
```

---

## Flyer BACK (A6 portrait, 2:3)

```
A vertical 2:3 portrait print flyer BACK for "{title}" — matching the front
aesthetic but with a solid warm gradient background (wine-red fading to navy),
no scene photography. Editorial typography, generous whitespace.

Copy:
  - Eyebrow top: "{eyebrow}"
  - Large serif title: "{title_line1} {title_line2}"
  - Date/time/venue block (centered, serif for date, sans for details):
    "{date}" / "{time} · {venue} · {entry}"
  - Section label (small, gold, letter-spaced): "PROGRAMM" / "PROGRAM"
  - Body (italic serif): "{program}"
  - Section label: "HIGHLIGHTS"
  - Body (stacked, small serif, one per line): {highlights[0]}, {highlights[1]}
  - Dresscode pill: "{dresscode}"

QR PLACEHOLDER — CRITICAL:
In the bottom-center, 8% above the bottom edge, render a SOLID PURE-WHITE
SQUARE occupying 22% of the flyer width. LEAVE IT EMPTY.

Constraints: NO logos, NO watermarks, NO stock illustrations. Color palette:
cream text on wine-red/navy background with gold accents for section labels.
```

---

## Tent card HALF (generate twice — once in wine-red, once in navy)

```
A vertical 2:3 portrait DJ booth tent-card HALF — {color_variant: "wine-red
gradient" OR "navy-blue gradient"} background. Intended to be folded at the
bottom edge into a standing tent card on a DJ table, read from ~1 m away.

Copy (all centered, vertically balanced):
  - Eyebrow (small, gold, letter-spaced, top): "HEUTE · AMBIENTE DJ"
  - DJ name (large, serif display): "{dj_name}"
  - Style line (italic serif): "{program}"
  - Small gold section label: "NÄCHSTES EVENT · {title}"
  - Date line (sans-serif): "{date} · {time} · {entry}"

QR PLACEHOLDER — CRITICAL:
Bottom-center, 6% above the bottom edge, SOLID PURE-WHITE SQUARE, 24% of
the half's width. EMPTY. No QR pattern.

Constraints: NO logos. Typography must be large enough to read from 1 m.
Generate this twice — one time with "wine-red" background, one time with "navy-blue".
```

After generation: rotate the wine-red variant 180°, stack it on top of the
navy variant to form the full tent card.

---

## Instagram story (1080×1920, 9:16)

```
A 9:16 vertical Instagram story for "{title}" — {aesthetic}.

Composition: {scene_description} fills the frame; a dark gradient overlay
sits at the top 40% and bottom 30% for text legibility.

Copy:
  - Title top-third (large serif, white/cream, 2 lines): "{title_line1}" / "{title_line2}"
  - Date + time (medium sans): "{date} · {time}"
  - Venue + entry (medium sans, below): "{venue} · {entry}"

QR PLACEHOLDER — CRITICAL:
In the bottom-center, 200 px above the bottom edge, SOLID PURE-WHITE SQUARE
of 360×360 px. EMPTY — no QR pattern.

Above the placeholder: small text "SCAN · ANMELDEN" or equivalent in event
language.

Constraints: NO IG UI elements baked in (no fake "swipe up", no fake handles).
NO text that isn't listed above. Pure static image — do not add stickers or emoji.
```

---

## Variants to ask for

When requesting a second variant, ask Gemini to vary ONE of:
- lighting (warmer / cooler)
- composition (tighter crop / wider scene)
- foreground emphasis (text-forward / image-forward)

Do not ask for a "completely different" variant — that produces chaos rather than a comparable option.
