#!/usr/bin/env python3
"""Build a Gemini Imagen prompt from an events.json bundle.

Usage:
    build-prompt.py <events.json> [--vibe <preset>] [--vibe-text "<freeform>"]

Vibe presets (see references/vibe-presets.md for full notes):
    salsa     — Cuban warm; burgundy + coral + marigold; salsa couple silhouette + palms
    bachata   — Sensual wine; wine + aubergine + rose gold; close-embrace dip
    kizomba   — Urban midnight; teal + emerald + gold; urban kiz couple, city bokeh
    festival  — International travel-poster; Cuban red + warm gold; Europe map silhouette

If neither flag is given, defaults to `salsa`. Use `--vibe-text` to fully override.

Prints the assembled prompt to stdout — pipe into image-from-gemini's generate.py.
"""
import argparse
import json
import sys
from pathlib import Path

VIBE_PRESETS = {
    "salsa": (
        "Warm Cuban / Havana aesthetic. Background is a deep burgundy and terracotta "
        "gradient with subtle film grain and soft golden bokeh lights. Vintage tropical "
        "mood. Faint silhouette of palm leaves and a couple dancing salsa in the upper "
        "third, faded into the background. Top header in bold condensed sans-serif "
        "typography (like Bebas Neue), color cream / warm white #FFF6E5. Accent color: "
        "marigold yellow #ffd166 and coral orange #ff8c5c."
    ),
    "bachata": (
        "Sensual Dominican / Caribbean night aesthetic. Background is a deep wine and "
        "aubergine gradient with subtle film grain and soft warm bokeh. Faint silhouette "
        "of a close-embrace bachata couple in the upper third — woman with flowing hair, "
        "intimate dip — faded into the background. Tropical mood with rose and amber "
        "bokeh lights. Top header in bold condensed sans-serif typography (like Bebas "
        "Neue), color cream / warm white #FFF6E5. Accent color: rose gold #f4a4a4 and "
        "amber #ffb84d."
    ),
    "kizomba": (
        "Lusophone / Angolan urban-night aesthetic. Background is a deep midnight teal "
        "and emerald gradient with subtle film grain and soft cyan and gold city-light "
        "bokeh. Smoky, intimate club mood. Faint silhouette of a close-embrace urban "
        "kizomba couple in the upper third — the woman's hand on the man's shoulder, "
        "slow connection — faded into the background. Top header in bold condensed "
        "sans-serif typography (like Bebas Neue), color cream / warm white #FFF6E5. "
        "Accent color: emerald teal #16A085 and warm gold #ffd166."
    ),
    "festival": (
        "Bold international travel-poster aesthetic. Background is a deep Cuban-red and "
        "warm rust gradient #C0392B with subtle film grain, faint vintage Cuban motifs "
        "(palm silhouettes, distressed paper texture), and a very faded outline of the "
        "world or regional map in the background with subtle gold pin markers. Tropical "
        "/ Havana-meets-passport mood. Top header in bold condensed sans-serif typography "
        "(like Bebas Neue), color cream / warm white #FFF6E5. Accent color: warm gold "
        "#ffd166 and bright cream."
    ),
}


def build_event_row(ev):
    """Format one event row as a pipe-separated line for the layout block."""
    parts = [
        f"{ev['day']} {ev['date']}",
        ev["name"],
        ev.get("venue", ""),
        ev.get("time", ""),
        ev.get("extra", ""),
        ev.get("price", ""),
    ]
    if ev.get("tag"):
        parts.append(f"[{ev['tag']}]")
    return " | ".join(p for p in parts if p)


def build_prompt(data, vibe_block):
    rows = "\n".join(build_event_row(ev) for ev in data["events"])

    return f"""Portrait 1080x1920 Instagram Story poster. Vertical 9:16 format. \
{data['title']} {data['subtitle']} schedule, period {data['weekLabel']}.

DESIGN: {vibe_block}

LAYOUT (top to bottom):

Header: {data['title']} {data['subtitle']}
Subtitle: {data['tagline'].upper()}
Date band: {data['weekLabel']}

Then a vertical schedule list, each row: weekday + date on the left, event name on \
the right, venue and time below in smaller type. Clean readable rows separated by \
thin accent-colored lines:

{rows}

Bottom call to action band on a coloured pill: {data['cta']}
Tagline below: {data['ctaSub']}

TEXT REQUIREMENTS: Spell every word, weekday code, date, time and venue exactly as \
written above. All text must be perfectly legible, sharp, no spelling errors. Preserve \
diacritics (umlauts, accents) exactly. Use European date format dd.mm. Times in \
24-hour format. The poster must look like a professionally designed event flyer, \
not a collage. No watermarks. No extra logos. No fictional events."""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events_json", help="Path to events.json")
    parser.add_argument(
        "--vibe",
        choices=list(VIBE_PRESETS),
        default="salsa",
        help="Vibe preset (default: salsa)",
    )
    parser.add_argument(
        "--vibe-text",
        help="Freeform vibe description (overrides --vibe)",
    )
    args = parser.parse_args()

    data = json.loads(Path(args.events_json).read_text())
    vibe_block = args.vibe_text if args.vibe_text else VIBE_PRESETS[args.vibe]

    print(build_prompt(data, vibe_block))


if __name__ == "__main__":
    main()
