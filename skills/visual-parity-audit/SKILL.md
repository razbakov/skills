---
name: visual-parity-audit
description: Drive two running UIs through matching states, capture side-by-side screenshots at a locked viewport, and produce a markdown + PDF report with per-screen diff notes. Use whenever the user asks to compare a prototype against a port, staging vs production, before vs after a refactor, "does the live site match the design", pixel-fidelity sign-off, visual regression check, or 1:1 parity audit — even if they don't say "audit". Strongly prefer this over ad-hoc screenshotting whenever two versions of the same UI need visual comparison.
---

# Visual Parity Audit

Drive two running instances of the "same" UI through matching states, take screenshots at a controlled viewport, and ship a reviewable PDF. Used to catch regressions that code review misses — typography, spacing, color, animation-entry state, or labels that drifted during a port.

## When to use

- **Port audits** — old framework vs new framework should render pixel-close. (e.g. Express + vanilla HTML → Nuxt)
- **Staging vs production** — before cutover, prove no drift.
- **Before client sign-off** — supplier-built UI has to match designer's reference.
- **After a "small" refactor** — prove nothing cosmetic changed unintentionally.

**Not this skill:** functional BDD testing, accessibility audits, performance profiling. This is a typography-and-layout eyeball check.

## Prerequisites

- Both apps reachable from this machine (one local, one live — or two URLs)
- A browser-automation MCP with viewport emulation + full-page screenshot saved to disk. In preference order: `chrome-devtools` (best: explicit emulate + filePath), `claude-in-chrome` or `agent-browser` (fallback: resize + saveScreenshot). If none is connected, stop and load one rather than taking skewed screenshots.
- A way to drive the state machine — either forms you can fill, or URL params that jump to each state
- `latex-pdf` skill available (for the PDF report)
- Basic knowledge of both apps' flows — which screens exist, how to reach each one

## Process — overview

1. **Lock the viewport** on both apps (same width × height × DPR, mobile/desktop flag identical). Sanity-check after every screenshot.
2. **Enumerate states** up front — 8–15 reachable screens, numbered so file order matches reading order.
3. **Drive both apps** through the states. Save to `docs/images/<audit>/{a,b}/<NN-slug>.png`. Clear PIN/auth cookies first if relevant.
4. **Write the markdown report** (verdict table → regression detail → side-by-side rows → not-captured list → action items). Commit to the repo.
5. **Generate the PDF** from the markdown via the bundled Python script (`scripts/build_parity_pdf.py`) — LaTeX with `\includegraphics` side-by-side tables.
6. **Open a PR** linking the report + PDF + any regression issues.

## Process — details

### 1. Pick the viewport — and lock it down

The #1 failure mode is a desktop screenshot vs mobile screenshot that look visually different for reasons *unrelated* to parity. **Always emulate the same viewport on both apps**, before any screenshot. For mobile UIs, use the design's target:

```
emulate viewport: 420x900x2,mobile,touch
```

The `x2` is `devicePixelRatio`. At 420 CSS × 2 DPR, full-page screenshots are 840 px wide. Sanity-check after each capture:

```bash
sips -g pixelWidth screenshot.png
```

If one side is 840 and the other is 1440, you broke the emulation somewhere (usually opening a new tab resets it). Re-emulate, re-capture.

### 2. List the states

Write down every reachable state *before* you start clicking. Example for a form-based app:

```
01-pin (locked entry)
02-staff-mode-default
03-staff-mode-quick      (mode hint text changes)
04-staff-mode-artist     (mode hint text changes)
05-dancer-p1             (flow entry)
06-handoff
07-dancer-p2
08-quick-entry-screen    (alternate flow)
09-artist-mode-screen    (alternate flow)
```

Number them so file order matches presentation order. 8–15 screens is a comfortable report size. More becomes tedious to review.

**Skip states that require destructive side effects** (payments, production DB writes, Airtable writes) — note them in the report as "verified via code review only" with a link to the component source.

### 3. Drive the state machine twice — once per app

Open two tabs (or one tab used sequentially). For each state:

1. Navigate / click into the state on **app A** → screenshot to `docs/images/capture-parity/A/{slug}.png`
2. Navigate / click into the state on **app B** → screenshot to `docs/images/capture-parity/B/{slug}.png`

Save paths are stable: `<repo>/docs/images/<audit-name>/{a,b}/{NN-slug}.png`.

Use `take_screenshot` with `fullPage: true` and an explicit `filePath` so images land in the repo, not an attachment.

**If an app gates state with a PIN / auth and caches the token**, clear it first:

```js
localStorage.clear();
sessionStorage.clear();
document.cookie.split(';').forEach(c => {
  const n = c.split('=')[0].trim();
  document.cookie = `${n}=;expires=Thu,01 Jan 1970 00:00:00 GMT;path=/`;
});
```

### 4. Write the markdown report first

Before the PDF, produce `<repo>/docs/<audit-name>-<YYYY-MM-DD>.md` with:

- **Verdict table** — 1 row per aspect, ✓ / ✗ / ~ with one-line note
- **Regression detail** — if you find a drift that's actionable, write it up as a standalone section *with the CSS / markup diff*, not hidden in a table
- **Side-by-side rows** — one section per screen, markdown table with 2 cells holding `![](path/to/a.png)` and `![](path/to/b.png)`
- **Screens not captured** — explicit list with reason (transient, requires side effect, etc.)
- **Action items** — P0/P1/P2/P3 table with issue numbers if you open them

Commit this markdown as the canonical source. GitHub renders it fine for quick review.

### 5. Generate the PDF

The markdown is for engineering review; the PDF is for stakeholders who don't open GitHub. Use the bundled `scripts/build_parity_pdf.py` — a self-contained Python script that emits LaTeX and compiles with Tectonic. No runtime deps beyond `python3` + `tectonic` (`brew install tectonic`).

Workflow:

1. Copy `scripts/build_parity_pdf.py` to a working location (e.g. `~/Local/<org>/<project>/build-<audit>.py` so it lives next to the PDF output).
2. Edit the config block at the top: `AUDIT_NAME`, `IMG_DIR`, `OUTPUT_PDF`, `TITLE`, `SUBTITLE`, `HEADLINE_CALLOUT`, and populate the `ROWS`, `VERDICT`, `NOT_CAPTURED`, `ACTIONS` lists.
3. Run `python3 build-<audit>.py`. The script writes a `.tex` sidecar and the `.pdf` next to it.

The template is intentionally skeletal — it handles LaTeX preamble, fonts, colors, header/footer, half-width image cells with `keepaspectratio`, unnumbered `\section*`, and a red-bordered `tcolorbox` for the headline callout. You only supply the audit-specific content.

Key design decisions baked into the script:

- `height=0.52\textheight,keepaspectratio` stops tall mobile screenshots from pushing rows off the page
- `\section*` (unnumbered) keeps the TOC clean
- Row labels are "Reference (A) / Under audit (B)" — generic so the PDF reads right for both "prototype vs port" and "staging vs production" audits
- Saves to `~/Local/<org>/<project>/` per the media-path convention, not in the repo

If you need to deviate (full-width images, three-column comparison, etc.), edit the script directly — it's <200 lines.

### 6. Open a PR

One PR with:

- Markdown report
- Screenshot directory
- In the PR body: the same verdict table, a link to the PDF artefact, and a callout of any regression issues opened

Label with the relevant flow/area label and `documentation`. Milestone it if the audit is part of a sprint.

## Gotchas

- **Viewport drift between apps** — catch with `sips -g pixelWidth` sanity check. If both sides aren't the same width, redo.
- **Token / cookie persistence** — both apps may remember a prior session; clear storage before capturing the locked state (e.g. PIN screen).
- **Non-deterministic state** — counters, ads, seed data. Either seed the same state on both sides or acknowledge the difference in the row notes.
- **Side effects on the "under audit" side** — never click Save / Submit on production during an audit. Use the "not captured" list instead.
- **Scroll-dependent screenshots** — use `fullPage: true` always, not viewport-only.
- **Font smoothing / retina** — set `deviceScaleFactor: 2` on both sides for readable text at phone aspect ratios.

## Anti-patterns

- **Don't** write the markdown after the PDF. The markdown is the canonical version-controlled record; the PDF is a rendering.
- **Don't** let the audit conclude "looks good." The value is catching drift — if you find none, say so explicitly and note what you *did* verify.
- **Don't** skip the "not captured" list. Auditors reading the PDF assume absence means aligned; being explicit about what wasn't checked is the honest move.
- **Don't** trust a code-level audit to have surfaced everything. The visual pass exists precisely because code audits misread stylesheets (I learned this one the hard way — labels that looked "too big" in an earlier port audit were actually the designer's intent).

## Output layout

```
<repo>/docs/
  <audit-name>-<YYYY-MM-DD>.md     # canonical report (version-controlled)
  images/<audit-name>/
    a/NN-slug.png                  # reference side
    b/NN-slug.png                  # under-audit side

~/Local/<org>/<project>/
  <audit-name>-<YYYY-MM-DD>.pdf    # rendered artefact for stakeholders
  <audit-name>-<YYYY-MM-DD>.tex    # sidecar, regenerable
  build-<audit>.py                 # copy of scripts/build_parity_pdf.py with this audit's config
```

## Bundled resources

- `scripts/build_parity_pdf.py` — self-contained LaTeX builder. Copy, edit config block, run. No pip deps; needs `tectonic` installed.
