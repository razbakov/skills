# Vibe Presets

Aesthetic recipes for the 9:16 poster. Each preset has been validated visually — they reliably produce on-brand output from Gemini Imagen. Pick the closest preset, or use it as a starting point for a freeform variant via `--vibe-text`.

The presets are encoded in `scripts/build-prompt.py`. This doc explains the *why* so you can compose new ones intelligently.

## Why these specific elements

Every preset has the same shape:
1. **Cultural anchor** ("Cuban", "Lusophone", "Dominican") — gives Gemini a coherent visual world
2. **Background gradient** with two colour stops + grain — keeps the canvas warm and physical, not flat
3. **Silhouette in upper third** — the dance style told visually so the viewer reads "ah, this is a salsa poster" before reading words
4. **Bokeh / texture detail** — light leaks, palm shadows, city bokeh — adds depth, signals premium
5. **Typography note** ("bold condensed sans-serif") — pushes Gemini toward Bebas-Neue-style fonts that read well at small phone size
6. **Accent colours** — two named hex codes for pills, lines, day-codes

Drop any one of these and the poster gets visibly worse. Add a sixth element (e.g. specific musical instruments) and Gemini starts losing focus on the layout.

## Salsa preset

Use for: weekly/monthly posters featuring Cuban, casino, timba, salsa-on-1, son cubano content.

```
Warm Cuban / Havana aesthetic. Background is a deep burgundy and terracotta gradient
with subtle film grain and soft golden bokeh lights. Vintage tropical mood. Faint
silhouette of palm leaves and a couple dancing salsa in the upper third, faded into
the background. Top header in bold condensed sans-serif typography (like Bebas Neue),
color cream / warm white #FFF6E5. Accent color: marigold yellow #ffd166 and coral
orange #ff8c5c.
```

When to deviate: if the venue is a specific Cuban venue (Buena Vista, La Bodeguita), name it once in the freeform `--vibe-text` to anchor the visual.

## Bachata preset

Use for: bachata sensual / dominicana / moderna content. Sensual is the dominant style internationally so the silhouette leans into the close-embrace dip.

```
Sensual Dominican / Caribbean night aesthetic. Background is a deep wine and
aubergine gradient with subtle film grain and soft warm bokeh. Faint silhouette
of a close-embrace bachata couple in the upper third — woman with flowing hair,
intimate dip — faded into the background. Tropical mood with rose and amber bokeh
lights. Top header in bold condensed sans-serif typography (like Bebas Neue), color
cream / warm white #FFF6E5. Accent color: rose gold #f4a4a4 and amber #ffb84d.
```

The silhouette explicitly mentions "intimate dip" — without that, Gemini sometimes draws the same upright couple as the salsa preset, which loses the bachata distinctness.

## Kizomba preset

Use for: kizomba / urban kiz / semba / tarraxo / ghetto zouk content. Lusophone (Angolan/Cape Verdean) is the cultural anchor — keeps Gemini away from generic Latin imagery.

```
Lusophone / Angolan urban-night aesthetic. Background is a deep midnight teal and
emerald gradient with subtle film grain and soft cyan and gold city-light bokeh.
Smoky, intimate club mood. Faint silhouette of a close-embrace urban kizomba couple
in the upper third — the woman's hand on the man's shoulder, slow connection —
faded into the background. Top header in bold condensed sans-serif typography
(like Bebas Neue), color cream / warm white #FFF6E5. Accent color: emerald teal
#16A085 and warm gold #ffd166.
```

The teal/emerald palette also matches the conventional "Munich Kizomba" Google Calendar colour `#16A085` — useful if the brand has any colour identity.

## Festival preset

Use for: international festival digests, monthly maps, multi-country event roundups.

```
Bold international travel-poster aesthetic. Background is a deep Cuban-red and
warm rust gradient #C0392B with subtle film grain, faint vintage Cuban motifs
(palm silhouettes, distressed paper texture), and a very faded outline of the
world or regional map in the background with subtle gold pin markers. Tropical /
Havana-meets-passport mood. Top header in bold condensed sans-serif typography
(like Bebas Neue), color cream / warm white #FFF6E5. Accent color: warm gold
#ffd166 and bright cream.
```

Map silhouette is the distinguishing element — replace "regional map" with "Europe map", "Latin America map", "world map" depending on scope.

For festival posters the `time` field in events.json holds the **city** instead of a clock time, and `price` holds the **country flag emoji**. The preset is happy with either.

## Composing new presets

When making a new vibe (e.g. for "tango", "swing", "afrobeats", a non-dance niche):

1. Pick a cultural anchor specific enough that Gemini has visual training data (Buenos Aires, Harlem, Lagos)
2. Pick two background colours that contrast pleasantly. Avoid pure black or pure white.
3. Decide on a silhouette that telegraphs the style in one image.
4. Choose two accent hex codes that pop on the background.
5. Mention "bold condensed sans-serif typography (like Bebas Neue)" verbatim — Gemini knows this style class.
6. Mention "soft bokeh" or "soft grain" — keeps the canvas physical.

Test the new vibe via `--vibe-text "your description"` first. If it consistently produces good output across 3+ events.json files, promote it to a named preset by adding it to `VIBE_PRESETS` in `scripts/build-prompt.py`.
