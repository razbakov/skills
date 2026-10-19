---
name: event-poster-bundle
description: "Generate a complete Instagram-ready event-list bundle: a 9:16 vertical poster (via Gemini Imagen) listing 6-9 events plus a structured caption (primary, short, pinned-comment), optionally delivered to Telegram Saved Messages for review. Use whenever the user wants to publish a recurring schedule or digest to social media — weekly dance schedules, monthly festival maps, club lineups, conference agendas, market days, anything where 'list of events + nice 9:16 poster + ready-to-post caption' is the deliverable. Trigger generously: phrases like 'schedule poster', 'weekly content', 'IG story for events', 'festival digest', 'reel with events', 'salsa events this week', 'kizomba poster', 'monthly festival map', 'event roundup', 'this week's schedule', 'gigs poster', or any case where the user has a curated event list and wants social-ready output. Even when the user only mentions one piece (just the image, just the caption, or just sending), use this skill — the bundle is integrated, and partial requests usually evolve into the full set."
---

# Event Poster Bundle

Produce a polished, Instagram-ready bundle for a list of events: **9:16 poster + caption + optional Telegram delivery**. The bundle is what you actually need to post — image alone is insufficient (no caption), caption alone is unposted (no image), and skipping the review step leads to typos going live.

## Why this skill exists

Recurring event-list content (weekly dance schedules, monthly festival digests, gig calendars) has a fixed shape but each instance has different data. Without a skill, every iteration:
- Hand-rolls a slightly different Gemini prompt → inconsistent aesthetic
- Composes a caption from scratch → missing pinned-comment, missing hashtags
- Forgets to send to a review surface → typos and wrong dates ship to followers

This skill captures the proven shape so each instance is just `events.json` + a vibe choice → bundle out.

## When to use it

Trigger when the user has (or implies) a list of events to publish. Common phrasings:
- "create a poster with [X] events this week / month"
- "9:16 schedule for [audience]"
- "weekly content for [account]"
- "festival digest for [niche]"
- "make an IG story for [event list]"
- "do [salsa / bachata / kizomba / festivals] this week"

If the user already has a previous bundle (folder with `events.json`, `schedule.png`, `caption.md`), this is almost certainly the next instance — use the skill.

## Inputs you need from the user

Before generating, confirm:

1. **Audience / account** — global vs local; which IG handle. Determines language (DE/EN mix vs EN-only) and reach hashtags.
2. **Cadence** — weekly, monthly, one-off. Determines folder naming (`2026-W18`, `2026-05`, `event-name`).
3. **Vibe / theme** — see `references/vibe-presets.md` for proven palettes (Cuban warm, sensual wine, urban teal, festival travel-poster). New themes are fine — describe colour, mood, silhouette.
4. **Event source** — a reference doc, a Google Calendar, a list pasted in chat. You'll curate it down to **6–9 rows** for poster readability. Cap is non-negotiable; more rows make the 9:16 unreadable on a phone.
5. **Delivery surface** — usually Telegram Saved Messages for Alex's review. Could be a folder open + manual upload.

If anything is unclear, ask before spending Gemini API time.

## Output structure

Always produce this exact shape inside one folder:

```
<bundle-folder>/
├── events.json      # the editable input — single source of truth
├── schedule.png     # 1080×1920 9:16 poster from Gemini Imagen
└── caption.md       # primary + short + pinned-comment + posting notes
```

Folder location is up to the caller — typically `~/Local/<org>/<account>/<cadence-dir>/<period>/`. Examples:
- `~/Local/ikigai/wedance-munich/weekly-poster/2026-W18/`
- `~/Local/ikigai/wedance-vip/festivals-monthly/2026-05/`

## Workflow

### 1. Build `events.json`

Schema (keep this schema stable — `scripts/build-prompt.py` reads it):

```json
{
  "weekLabel": "27.04 – 03.05",
  "weekISO": "2026-W18",
  "title": "SALSA",
  "subtitle": "in MÜNCHEN",
  "tagline": "Diese Woche",
  "cta": "Folge @WeDanceMunich",
  "ctaSub": "Salsa-Wochenplan jeden Sonntag",
  "events": [
    {
      "day": "MO",
      "date": "27. APR",
      "time": "19:00",
      "name": "La Frida Cubana",
      "venue": "Frida",
      "extra": "DJ Alösha · Cuba 80s Dresscode",
      "price": "€10",
      "tag": "TONIGHT"
    }
  ]
}
```

Field semantics:
- `weekLabel` — human-friendly date band shown on the poster (e.g. `27.04 – 03.05`, `MAY 2026`).
- `title` / `subtitle` — top header. Two lines because vertical 9:16 has the room and the contrast looks great.
- `tagline` — small line above the title (e.g. `DIESE WOCHE`, `MAY 2026`).
- `cta` / `ctaSub` — bottom band. The CTA is the IG handle; the sub explains the cadence.
- Each event: `day` is short (MO/DI/MI), `date` is human (`27. APR` or `→ 11 MAY` for ranges), `time` can be a time or a place name (digest posters use city instead of time). `extra` is one short qualifier line. `price` shows on a pill (€10, FREE, country flag emoji for festival posters). `tag` (optional) draws a red badge — use sparingly for "TONIGHT" or "⭐" headliners.

For canonical example see `assets/events.example.json`.

### 2. Generate the poster via Gemini Imagen

Run `scripts/build-prompt.py <events.json> [--vibe <preset>]` to assemble the Gemini prompt, then pipe it into the `image-from-gemini` skill. The script handles preset palettes (`salsa`, `bachata`, `kizomba`, `festival`, or freeform `--vibe-text "..."`).

```bash
PROMPT=$(python3 SCRIPT_DIR/scripts/build-prompt.py path/to/events.json --vibe salsa)
python3 ~/.local/share/skill-mix/sources/skills@razbakov/skills/image-from-gemini/scripts/generate.py \
  "$PROMPT" \
  -o path/to/<bundle-folder>/schedule.png
```

Inspect the result — common Gemini glitches and how to handle them:
- **Text fragment / typo on a row** (e.g. "Cha" appearing next to a flag) — usually cosmetic. Note it for the caller; regenerate only if requested. Each regen costs ~60s and may introduce a different artifact.
- **Missing umlaut or accent** — regen with the umlaut spelled out twice in the prompt.
- **Event time/date misread** — verify against `events.json`. If wrong, regen.
- **Cropped header** (long titles overflow at top) — shorten `title` or `subtitle`.

### 3. Write `caption.md`

Use this exact section structure (callers expect to grep `## Primary` and `## Short` reliably):

```markdown
# IG caption — <descriptive label>

## Primary (DE/EN mix or EN, depending on audience)

<emoji> <SHOUTY HEADLINE> — <tagline>

<one-line intro>

<emoji> <DAY DATE> · <Event Name>
<Venue> · <time> · <price/note> — <one-line vibe>

<...one block per event...>

📌 Save / share / follow lines.
👉 Folge @handle — <cadence promise>.

#hashtag #hashtag #hashtag <about 20-28 hashtags>

---

## Short version (Story / Reel CTA)

<emoji> <one-liner>
<two short call-to-action lines>
👉 @handle
#fewer #hashtags

---

## First comment (pinned — venue addresses / links)

📍 Adressen
• Venue — Address, Postleitzahl Stadt
• ...

⚠️ Cancellations / time-TBC notes here.

---

## Notes for posting

- Best time slot: ...
- Cross-tag: @venue1 @venue2 ...
- Pairing: stagger with other style-bundles in the same week.
```

The `## Primary` block is what gets sent to Telegram for review. The other blocks are for the human posting later.

Tone:
- Match the audience language. Munich locals → DE/EN mix; global @wedance.vip → EN-only.
- Per-event line should be short, opinionated, useful. "Free für Members" beats "free entry for paying members".
- Hashtag block: ~20–28. Mix style-specific (#SalsaMünchen) + venue (#BuenaVistaMunich) + city (#München) + brand (#WeDanceMunich).

### 4. Send to Telegram Saved Messages (optional but default)

Use `scripts/send-to-telegram.py <image-path> <caption-md-path>` — sends image + the Primary section as 2 separate messages to the user's Saved Messages.

```bash
python3 SCRIPT_DIR/scripts/send-to-telegram.py \
  path/to/schedule.png \
  path/to/caption.md
```

Skip this if the user explicitly says "don't send" or there's no Telethon session set up.

If you get `ValueError: too many values to unpack (expected 5)`, the venv's Telethon is older than the session-file schema — see the inline comment in `scripts/send-to-telegram.py` for the fix.

### 5. Reveal the folder

Per the file-delivery rule (auto-open generated artifacts), end with:

```bash
open path/to/<bundle-folder>/
```

So the user can see the file on disk.

## Curation rules (the non-obvious quality gates)

These come from running the workflow many times. Skipping them produces visibly worse bundles.

- **Cap at 6–9 events.** More rows = unreadable 9:16. If you have 15 events, curate down by removing duplicates, dropping weakest, grouping consecutive same-day ones into one row.
- **Cancelled events go in the caption, not silently dropped.** If "Saturday Salsa Party is cancelled this week", flag it in the pinned-comment with ⚠️. People who would have gone need to know.
- **Cross-style events appear on every relevant style's poster.** A Salsa+Bachata Practice Party belongs on both posters. Same event, multiple lists.
- **Never invent missing data.** If time is unconfirmed, use "Abends" or "Zeit TBC". If venue address is unknown, omit from pinned-comment rather than hallucinate.
- **Preserve diacritics in the prompt.** MÜNCHEN, Salsamás, Guaguancó — write them with diacritics in the events.json so Gemini renders them correctly. Sanitizing to ASCII produces ugly output.
- **One headliner per poster.** If everything is "⭐ MUST GO", nothing is. Mark at most one event with `tag: "⭐"` or `tag: "TONIGHT"`.

## Vibe presets

See `references/vibe-presets.md` for proven palettes. Quick lookup:

| Preset | Use for | Palette | Silhouette |
|---|---|---|---|
| `salsa` | Cuban / casino / timba weeklies | Burgundy + coral + marigold | Couple dancing salsa, palms |
| `bachata` | Sensual / Dominican weeklies | Wine + aubergine + rose gold | Close-embrace dip |
| `kizomba` | Urban kiz / semba weeklies | Midnight teal + emerald + gold | Close-embrace urban couple, city lights |
| `festival` | International festival digest | Cuban red + warm gold | Faded Europe map + palm motifs |

For a one-off vibe, use `--vibe-text "your description here"` instead of a preset.

## Common failure modes

- **"The caption is just the image description."** You wrote the image prompt as the caption. Read this file again — caption ≠ prompt. Caption is human-facing copy.
- **"All 15 events on the poster."** You skipped the curation step. Cap at 6–9, always.
- **"Bundle is in the wrong folder."** Folder location matters because the user opens it later. Use the convention `~/Local/<org>/<account>/<cadence>/<period>/`.
- **"Gemini text is garbled."** Spell critical text twice in the prompt (the build-prompt.py script does this for headers; if a row is critical, repeat it in the freeform vibe block).
- **"User wanted a video reel, not a poster."** Ask up front. This skill is for static 9:16 image bundles. For video reels use `video-from-gemini` directly.
