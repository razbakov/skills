---
name: instagram-launch-grid
description: "Seed a new or empty Instagram account with a 9-post grid (3×3) so the profile looks established the moment a new visitor lands. Designed for festivals, new businesses, product launches, conferences, communities — any time an empty IG profile would hurt conversion from external traffic (QR scans, flyer drops, cross-promo). Generates assets via /image-from-gemini (per content-publishing rules — never HTML), writes captions with hashtag sets, and outputs a posting order + cadence plan. Trigger generously: phrases like '9 posts for instagram', 'fill my IG', 'starter grid', 'launch grid', 'instagram seed', '9-post grid', 'IG account not to look empty', 'first instagram posts', 'feed bootstrap', '3x3 grid', 'instagram launch content'. Even if the user mentions only one piece (just the images, just the captions, just the order), use this skill — the grid only works as an integrated bundle."
---

# Instagram Launch Grid

Seed a new Instagram account with **9 posts laid out as a 3×3 grid that reads as a single curated installation**. When someone lands on the profile from a flyer QR / a story-mention / a cross-promo, the first thing they see is 9 squares above the fold. Make those 9 squares answer "what is this?" before any scrolling happens.

## Why this skill exists

Every new brand hits the same wall: account is created → handle is in flyer / IG bio / press release → people arrive → see an empty grid → bounce. Conversion from external traffic dies in that gap.

A "feed-fill" run done ad-hoc usually produces:
- 9 random assets with no visual rhythm (alternating photo/type rows broken)
- Captions written on the fly with no hashtag strategy
- Wrong posting order (first post lands bottom-right of grid instead of top-left)
- No cadence plan (9 posts blasted in 30 minutes → algorithm chokes)

This skill captures the proven shape:
- A 3×3 grid plan with each cell having a job (hook / substance / brand)
- Asset inventory before generation (reuse existing → only generate gaps)
- Captions per post following per-cell-type patterns
- Reverse-grid posting order documented explicitly
- Cadence recommendation matching the launch context

## When to use it

Trigger on phrases like:

- "9 posts for instagram"
- "fill my IG / so the account doesn't look empty"
- "starter grid" / "launch grid" / "9-post launch"
- "IG seed posts" / "first instagram posts"
- "3×3 grid" / "instagram feed bootstrap"
- "we need posts before [event/launch/QR drop]"

Common contexts:
- A new festival or event handle ahead of a flyer drop
- A new business / product launch
- A new community account that's about to be linked from elsewhere
- A rebranded account that needs to look fresh, not stale

If you're already in a project where flyers exist, a website is live, and an IG handle is registered but empty — this is almost certainly the next step.

## When NOT to use it

- The account already has 9+ posts and the user wants ONE new post → use `/social-post` or `/brand-poster` instead.
- The user wants a weekly schedule of events → use `/event-poster-bundle` (9:16 with event list, not a 3×3 grid).
- The user wants social distribution across platforms → use `/social-post`.
- The brand has no visual language yet (no palette, no flyer, no logo direction) → tell them to nail the brand first; running this skill against an empty brand brief produces 9 inconsistent posts.

## Inputs you need from the user

Before generating, confirm these (ask if missing):

1. **IG handle** — exact `@handle` (matters for the captions' "follow @handle" CTAs and for confirming you're targeting the right account).
2. **Brand brief** — at least: name, one-line tagline, dates/key details, palette (hex codes if possible), one-paragraph "what this is and who it's for", things to avoid (clichés).
3. **Existing assets** — paths to any flyers / photos / logos already produced. Reusing existing assets keeps brand coherence and saves Gemini calls. List the assets and confirm which fit which cells.
4. **Grid narrative** — pick a 3-row story. Defaults are in [`references/grid-layouts.md`](references/grid-layouts.md). The most common is **Hook / Substance / Brand**, but **People / Place / Plan**, **About / Offer / Proof**, and others work — match the launch context.
5. **Caption language(s)** — EN-only, DE-only, EN+ES bilingual, etc. Affects caption length and hashtag mix.

## Process

### 1. Plan the 3×3 grid on paper first — and validate rhythm before generating

Always produce the grid plan as a markdown table before generating anything. Each cell has:
- Position (A1, A2, A3 / B1–B3 / C1–C3)
- Job ("hook", "substance — dates card", "brand — wordmark")
- Asset source ("reuse: `path/flyer.png`" OR "generate: prompt summary")
- Medium ("photo" or "type-led")

This step prevents two failures: generating 9 posts then realizing 5 are visually identical, and spending a generation on something that already exists.

**Then validate the plan against these rhythm rules before generating:**

- **No row of 3 same-medium cells.** A row of 3 type-led cards reads as a brochure; a row of 3 photos reads as chaos. Aim for 1-2 photos per row, the rest type-led. Or any permutation that breaks runs of 3 same-medium posts.
- **At least 2-3 photographs in the full grid.** Real-human photographs (or photorealistic Gemini outputs) anchor emotion in a way typography can't. Force at least 2 cells to be photographic.
- **Repeat 2-3 palette accents across all 9.** Typically one accent color (e.g. terracotta) appears in 4-6 of 9 posts to unify the grid visually.
- **Bottom-right cell (C3) = the foundation.** It stays visible forever as the grid fills, and shows when a visitor scrolls back. Make it the wordmark / logo / brand-mark — NEVER anything time-bound (no dates, no "tickets dropping soon").
- **Top-left cell (A1) = first impression.** Always the single strongest visual you have.

If the plan fails any of these checks, revise BEFORE generating. Iterating after generation costs API calls and your time.

### 2. Inventory existing assets, identify gaps

Check the user's local media folder (typical: `~/Local/<Org>/flyers/`, `~/Local/<Org>/logo/`). Map existing files to cells. Note which cells need new generation.

For a typical festival launch, you reuse 2-4 cells from an existing flyer suite and generate 5-7 new ones.

### 3. Generate missing posts via `/image-from-gemini`

Per `content-publishing.md` framework rule: **flyers, posters, social posts, and event graphics must use `/image-from-gemini` only — never `/image-from-html`** (HTML path produces flat, off-brand output).

For efficiency, batch all missing posts in a single Python script (see `scripts/batch_generate.py`). Sequential `/image-from-gemini` calls cost more total time.

**Expect 1-2 of 6-7 generations to refuse on first try.** Gemini refuses ~10-20% of brand-asset generations — common triggers are specific physical descriptors of real-people likenesses, ambiguous anatomy/clothing combinations, ampersand-heavy lockups, or trademark-adjacent compositions. When a generation returns no image, retry with the prompt softened: drop specific physical descriptors, rephrase the format hint, use a reference photo if available. Don't retry more than twice — if it keeps refusing, redesign the composition.

See [`references/gemini-gotchas.md`](references/gemini-gotchas.md) for the full list of recurring Gemini issues (apostrophe blindspot, ampersand rendering, fake Instagram chrome, refusal triggers) and the proven workarounds.

### 4. Write captions

For each post, write:
- A caption (50-200 words depending on post type — see [`references/caption-patterns.md`](references/caption-patterns.md) for per-cell shapes)
- A hashtag set (8-15 tags — mix of brand-specific, location, niche, and 1-2 broader)

If multilingual was requested, write the caption in EN with a 1-line ES (or DE) hook for the most relevant posts (typically the mission and revolution posts). Don't bilingual every post; it dilutes.

Each caption should include:
- A clear CTA ("link in bio" or "join the WhatsApp group" or "tickets at the-domain.com")
- The IG handle reference (for cross-tagged posts)
- Hashtags arranged in one line at the bottom (no `.\n.\n.\n` separator block — that's outdated)

### 5. Document posting order (reverse-grid)

**This is the most-missed detail.** Instagram displays newest top-left, oldest bottom-right. To achieve the visual grid you planned, post in **reverse-grid order**:

```
Posting order: C3 → C2 → C1 → B3 → B2 → B1 → A3 → A2 → A1
```

The wordmark goes up first (and lands bottom-right of the grid); the hero goes up last (and lands top-left, the spot a new visitor sees first).

### 6. Recommend a cadence

Pick one based on launch context:

| Cadence | When | Pro | Con |
|---|---|---|---|
| **All-at-once burst (2-3 hours)** | Profile needs to look real NOW (QR is going live tonight, flyer is dropping tomorrow) | Established profile immediately for any new visitor | First 2-3 posts soak all organic; remaining 6 get nothing |
| **Staggered 3-3-3 across 3 days** | The launch is 3-5 days out, peak anticipation builds toward it | Each post gets its own organic shot; final 3 posts (hero + reveal) land on launch eve | Profile looks empty/light for ~48h |
| **Drip 1/day for 9 days** | Launch is 2-4 weeks out | Maximum organic per post; sustains anticipation | Too slow for tight launches; profile still light for first week |

Recommend, don't decide — the user knows their launch calendar.

### 7. Deliver as a spec doc

Output the full plan as a markdown spec in the org's `domains/marketing-community/operations/` folder (or equivalent). The spec should contain:
- Grid layout
- Posting order
- Captions per post (copy-paste ready)
- Hashtag sets per post
- Cadence recommendation
- File paths to all 9 assets in `~/Local/<Org>/instagram/grid-launch-N/`
- Known issues (refer to `references/gemini-gotchas.md`)

Open the folder so the user can review the assets in Finder.

## Outputs

For each run, you produce:

1. **9 PNG files** in `~/Local/<Org>/instagram/grid-launch-N/` (with `post-A1-*.png`, `post-A2-*.png`, ... naming so the file-name encodes the grid position).
2. **A markdown spec** in the org's `domains/marketing-community/operations/instagram-launch-grid.md` (or equivalent) documenting grid layout, posting order, captions, hashtag sets, cadence recommendation.
3. **A git commit** to the org workspace covering only the spec doc (the 9 PNGs live outside git per the framework "large media outside git" rule).
4. **An `open <folder>` shell call** so the user can review the assets in Finder.

## Example reference run

The first full deployment of this skill was the launch grid for the **Agua Pichi** Cuban festival (Munich, July 2027) ahead of the Charanga Habanera concert flyer drop.

- **9 final assets:** `~/Local/AguaPichi/instagram/grid-launch-9/post-{A1,A2,A3,B1,B2,B3,C1,C2,C3}-*.png`
- **Spec doc with full captions + hashtags + cadence:** `~/Orgs/AguaPichi/domains/marketing-community/operations/instagram-launch-grid.md`

That run reused 3 cells (2 existing flyers + 1 logo concept) and generated 6 new ones, with 1 refusal that required a softened retry. The recommended cadence was staggered 3-3-3 across the 3 days before the launch event. Use it as a reference implementation when the patterns above feel abstract.

## References

- [`references/grid-layouts.md`](references/grid-layouts.md) — proven 3-row narrative shapes (Hook/Substance/Brand, People/Place/Plan, About/Offer/Proof, etc.)
- [`references/caption-patterns.md`](references/caption-patterns.md) — caption shapes per cell type
- [`references/gemini-gotchas.md`](references/gemini-gotchas.md) — recurring Gemini issues and proven workarounds
- [`scripts/batch_generate.py`](scripts/batch_generate.py) — Python script template for batched Gemini generation
- Framework rule: `~/Projects/ikigai-team/rules/content-publishing.md` — flyers/posters/social posts must use `/image-from-gemini`, never `/image-from-html`

## Related skills

- **`/image-from-gemini`** — used internally for every generated cell
- **`/brand-poster`** — for one-off posters; this skill builds 9 at once with grid logic
- **`/event-poster-bundle`** — single 9:16 with event list (different shape, different use case)
- **`/social-post`** — cross-platform distribution after posts are made
