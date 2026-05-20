# Gemini Gotchas — recurring issues when generating brand assets

These are issues that recur across most Gemini-generated brand work (any skill that uses `/image-from-gemini`). Read this before generating, especially when text accuracy or specific compositions matter.

## Text rendering issues

### Apostrophe blindspot

Gemini drops apostrophes about 60% of the time. `MUNICH'S` becomes `MUNICHS`. `WE'RE` becomes `WERE`.

**Mitigation:** Add explicit instructions to the prompt:
- `use the apostrophe character`
- `spell exactly: MUNICH'S (with apostrophe)`

Even with explicit instructions, expect ~30% of runs to still drop it. For brand-foundation pieces (logo, primary tagline card), iterate until correct. For incidental copy (event-listing cards), accept v1.

### Ampersand renders as the word "AND"

Same problem as apostrophes. `ROOTS & REVOLUTION` becomes `ROOTS AND REVOLUTION`.

**Mitigation:** Add to the prompt:
- `use the ampersand & character (not the word AND)`
- `do NOT substitute AND for the ampersand symbol`

For taglines that include the ampersand as part of the locked brand voice, force it explicitly. For body text where AND reads naturally, let it go.

### Long URLs and unusual punctuation

Gemini may garble long URLs, em-dashes, and non-ASCII characters. Where possible, use a short brand URL in posters and let the body caption carry the long version.

## Composition issues

### Fake Instagram chrome appears when format mentions "Instagram"

When a post is described as "Instagram story format" or "1080x1920 Instagram", Gemini sometimes draws a literal Instagram UI inside the canvas — `instagram 9:16` text in the header, "Send message" box at the bottom, even reply heart icons. When the actual image gets posted to Instagram, the real chrome overlaps this fake chrome and the result looks broken.

**Mitigation:** Avoid the word "Instagram" in the format spec. Describe formats by aspect and safe zones instead:
- `vertical 9:16 poster (1080x1920), top 15% safe zone, bottom 20% safe zone`
- `square 1:1 poster (1080x1080)`

### Refusals on certain compositions

Gemini refuses (returns no image) on ~10-20% of brand-asset generations. Common refusal triggers:

- **Specific physical descriptors of real-people likenesses** without a reference photo (`a young Cuban male dancer with bare arms` may refuse where `a young Cuban dancer mid-spin` works)
- **Anatomy + clothing combinations** that trigger safety filters
- **Brand-name overlap** with corporate trademarks rendered too literally
- **Ampersand-heavy lockups** combined with monogram letters (the AP-monogram failed twice in the Agua Pichi run)

**Mitigation:**
- Generate in a batch script with try/except so refusals don't block the whole run
- On refusal, retry with the prompt softened: drop specific physical descriptors, drop ambiguous clothing, rephrase the format hint, use a reference photo if available
- Don't retry more than twice — if it keeps refusing, redesign the composition

### Photo > text card for emotional anchor

A grid of 9 text-only cards reads as a brochure. Real photographs (or photorealistic Gemini outputs of people) anchor emotion in a way typography can't.

**Mitigation:** Force at least 2-3 cells per 9-post grid to be photographic. Plan this at the grid-layout stage, not after.

## When iteration is worth it

Gemini outputs aren't free (API cost + your time). Set an iteration budget per cell:

| Issue | Iteration budget |
|---|---|
| Apostrophe/ampersand wrong on brand-foundation piece (logo, hero) | 2 retries |
| Apostrophe/ampersand wrong on incidental piece | 0 — ship v1 |
| Fake IG chrome on a story post | 1 retry (fix is reliable) |
| Refusal (no image returned) | 2 retries with softened prompt; then redesign |
| Composition mostly right but one element off | 0 — iterate the prompt only if the element is brand-defining |

## Versioning

When a generation fails or you iterate, keep both versions:
- `post-A1.png` — final / canonical
- `post-A1-v1-TYPO.png` — earlier version with the noted issue
- Document the iteration in the spec doc so the next person knows why a version was deprecated

Don't delete versions silently — Gemini outputs are not reproducible (same prompt → different image), and a "good" v1 might be worth keeping as an alternative even if v2 is more accurate.
