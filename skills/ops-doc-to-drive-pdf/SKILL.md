---
name: ops-doc-to-drive-pdf
description: Turn a markdown operational document (runbook, checklist, SOP, playbook, host script) into a styled print-ready PDF and upload it to a specific Google Drive folder, idempotently — so you can edit the source and regenerate without breaking the Drive link. Use when a user wants a markdown doc rendered as a PDF in Drive, when they ask to "make this printable", "put this in the team folder", "update the PDF in Drive", or whenever an ops doc needs a physical/printable artifact with a stable shareable link. Composes the `latex-pdf` skill (LaTeX template) and the `google-drive` skill (gog CLI) — use this one instead of calling those directly, because it handles the storage convention, the Unicode gotchas, and the re-upload-without-breaking-the-link pattern that you will get wrong by default.
---

# Ops Doc → Drive PDF

Glue skill. Takes a markdown operational document from an org repo, renders a styled A4 PDF, and uploads it to a Google Drive folder so the shareable link stays stable across edits.

## When to use

- "Make this runbook a PDF in Drive"
- "Put the host script / SOP / checklist in the team folder"
- "Update the PDF in Drive — I edited the markdown"
- Any long-form ops doc the user plans to **print** or **share a stable link to**

## When NOT to use

- Slide decks / presentations → `image-from-html`
- Branded marketing collateral (posters, flyers, social cards) → `image-from-html` or `brand-poster`
- One-off PDFs that will never be regenerated → invoke `latex-pdf` directly, skip the upload ceremony
- Ephemeral docs (<1 week lifespan) → don't PDF them at all

## What this skill produces

1. A Python build script at `<media-path>/<slug>/build_<slug>.py` — the source of truth for future rebuilds
2. `<slug>.tex` and `<slug>.pdf` in the same directory (artifacts)
3. An uploaded Drive file at a known `fileId` — captured so future re-uploads use `--replace <fileId>`
4. A one-line rebuild recipe returned to the user

## Pipeline

### 1. Confirm source + target

- **Source markdown path** — must already exist in an org repo (e.g. `~/Orgs/<Org>/domains/.../<doc>.md`). This skill does not write the content.
- **Target Drive folder ID** — find it with:
  ```bash
  gog drive search "<folder name>" --json
  ```
  Grab the `id` where `mimeType` contains `folder`. Never guess folder IDs.

### 2. Pick the media path

Artifacts live under a **non-git media path**, not in the org repo:

```bash
mkdir -p ~/Local/<org>/<project>/<slug>
```

The org's `CLAUDE.md` usually defines the media-path root (e.g. `~/Local/<org>/` for ikigai). The canonical markdown stays in the org repo (versioned content); the build script and compiled outputs live in media (ephemeral artifacts).

### 3. Write the build script

**Invoke the `latex-pdf` skill** for the Python + LaTeX template. It covers: Tectonic install check, Python preamble, `esc()` helper, `subprocess` compile step. Place the generated `build_<slug>.py` in the media directory.

On top of the `latex-pdf` template, you MUST add the fixes in the [Gotchas](#unicode-gotchas) section below before your first compile. These are not optional — they are the difference between a usable PDF and one with missing glyphs that looks fine on screen and breaks on paper.

**Do not try to parse the markdown programmatically.** Hand-translate section by section into the Python script's `CONTENT` list. This is deliberate: you keep control over page breaks, callouts, table formatting, checklists, and brand voice. A pandoc auto-conversion loses all of this and produces ugly defaults. The 20 extra minutes of hand-translation is what makes the PDF printable and professional.

### 4. Compile

```bash
cd ~/Local/<org>/<project>/<slug> && python3 build_<slug>.py
```

First compile is slow (~60s) because Tectonic downloads fonts and packages. Subsequent compiles are fast.

**Verification checklist before moving on** (this is the step new users skip and regret):

1. **Unicode check** — grep the build output:
   ```
   warning.*could not represent
   warning.*Missing character
   ```
   Must return empty. A non-zero exit code from tectonic is NOT the success criterion — it will happily produce a PDF full of missing-glyph boxes with exit code 0.

2. **Visual check** — use the `Read` tool on the first 2-3 pages of the PDF. Look for:
   - Garbled escape sequences (`\textbackslash{}ldots\{\}`)
   - Literal `\u2019` text reading as "Ž019" (the raw-string trap — see gotchas)
   - Empty boxes where glyphs should be
   - Layout overruns

If anything is off, fix the script and rebuild. **Never upload a broken PDF and fix later** — it burns a Drive revision and confuses anyone who grabbed the file between uploads.

### 5. Upload to Drive

**First upload:**

```bash
gog drive upload ~/Local/<org>/<project>/<slug>/<slug>.pdf \
  --parent <folderId> --json
```

Parse `file.id` from the response. **Save this ID immediately** — it's the idempotency key. Write it in the session notes, memory, or handoff message. Without it, the next "just update the PDF" request creates a duplicate instead of replacing.

**All subsequent updates** — same file ID, link unchanged, share permissions preserved:

```bash
gog drive upload ~/Local/<org>/<project>/<slug>/<slug>.pdf \
  --replace <fileId> --json
```

Success looks like `{"preservedFileId": true, "replaced": true}`. The `--replace` flag is the entire reason this skill exists as a separate thing. Without it, every edit produces a new file, breaks existing share links, and forces the user to clean up duplicates.

### 6. Return the rebuild recipe

End your response with a one-liner the user (or a future agent) can run unsupervised:

```bash
python3 ~/Local/<org>/<project>/<slug>/build_<slug>.py && \
  gog drive upload ~/Local/<org>/<project>/<slug>/<slug>.pdf --replace <fileId>
```

This matters because the user will come back in three weeks, edit the markdown, and not remember the pipeline. The one-liner is the handoff.

## Unicode Gotchas

Tectonic's default font (`ec-lmr10`) does not contain smart quotes, em-dashes, en-dashes, arrows, ellipsis, or non-breaking spaces. A PDF with these characters "compiles" (exit 0) but renders empty boxes. The fix is character substitution at three layers — miss any one layer and glyphs go missing.

### Gotcha 1 — Substitute punctuation inside `esc()`, before backslash escaping

```python
def esc(text: str) -> str:
    unicode_map = [
        ("\u2014", "---"),   # em-dash
        ("\u2013", "--"),    # en-dash
        ("\u201C", "``"),    # left double quote
        ("\u201D", "''"),    # right double quote
        ("\u2018", "`"),     # left single quote
        ("\u2019", "'"),     # right single quote / apostrophe
        ("\u2026", "..."),   # ellipsis
    ]
    for old, new in unicode_map:
        text = text.replace(old, new)
    # ... then the latex-pdf skill's standard backslash/&/%/$/#/_/{/}/~/^ escaping
```

### Gotcha 2 — Do NOT substitute to LaTeX commands inside `esc()`

**Wrong:**

```python
("\u2026", "\\ldots{}"),   # DON'T — the later backslash escape pass mangles this
```

The `\\` → `\textbackslash{}` pass that `esc()` runs turns `\ldots{}` into `\textbackslash{}ldots\{\}`, which renders as literal text. **Rule:** inside `esc()`, substitute Unicode to plain ASCII only (`...`, `--`, `` ` ``). If you need a LaTeX command, do it in the final sweep (Gotcha 4).

### Gotcha 3 — The raw-string `\u` trap

**Wrong:**

```python
CONTENT.append(r"\subsection*{Nominated candidate\u2019s speech}")
```

The `r` prefix makes `\u2019` six literal characters, not a Unicode escape. This renders as "candidateŽ019s" in the PDF — extremely confusing because the bug is invisible in the Python source.

**Rule:** when a string needs BOTH LaTeX backslashes AND a Unicode char, either drop the `r` prefix and double the backslashes, or use a plain ASCII apostrophe in raw strings. Never mix `r"..."` with `\u....` escapes. One literal, one concern.

### Gotcha 4 — Final whole-document sweep for raw-LaTeX strings

Unicode characters also sneak in via raw LaTeX you write directly — tables, callouts, titles, emergency-protocol rows. These never pass through `esc()`, so they escape Gotcha 1. Add a final sweep on the assembled TeX string right before writing to disk:

```python
BODY = "\n\n".join(CONTENT)
TEX = PREAMBLE + r"\begin{document}" + "\n" + BODY + "\n" + r"\end{document}" + "\n"

_FINAL_SWEEP = [
    ("\u2014", "---"),
    ("\u2013", "--"),
    ("\u201C", "``"),
    ("\u201D", "''"),
    ("\u2018", "`"),
    ("\u2019", "'"),
    ("\u2026", "..."),
    ("\u2192", "$\\rightarrow$"),  # OK here — nothing runs after this
]
for _old, _new in _FINAL_SWEEP:
    TEX = TEX.replace(_old, _new)
```

In the final sweep you **can** safely substitute to LaTeX commands, because nothing else touches the string afterward. That's why `→` → `$\rightarrow$` belongs here, not in `esc()`.

### Gotcha 5 — Tildes in content text

`esc()` turns `~` into `\textasciitilde{}`, which renders as a tilde glyph. That's usually fine, but if you have "~50 seconds" meaning "approximately 50", the visual result is awkward. Normalize at the top of `esc()`:

```python
text = text.replace("~50", "approximately 50").replace("~3", "approximately 3")
```

Or fix at the source — either works.

## Storage Convention

| Thing | Location | Why |
|---|---|---|
| Canonical markdown source | Org repo (e.g. `~/Orgs/<Org>/domains/.../<doc>.md`) | Content is versioned, reviewable, and the source of truth |
| Python build script | Media path (`~/Local/<org>/<project>/<slug>/`) | Tightly coupled to generated artifacts and specific fileId; not generic enough to belong in git |
| Generated `.tex` and `.pdf` | Media path | Artifacts — rebuilt from source on demand |
| Drive file ID | Session notes / memory / handoff message | Required for `--replace`; losing it forces a re-search or creates duplicates |

If you find yourself writing a build script that would work for many different docs (a true template), promote it into the org repo and parametrize it. That's a different pattern from this skill — this skill is "one doc, one script, one Drive file."

## Edge Cases

- **Drive folder doesn't exist yet.** Create it once in the Drive web UI, grab the ID, reuse forever. `gog drive` folder creation exists but the one-time browser step is simpler.
- **Need to share the PDF with specific people.** Sharing permissions are deliberately not handled by this skill — per the global CLAUDE.md rule, modifying access controls is something the user does themselves. Upload, return the link, tell the user to share it in the Drive UI.
- **User wants an archive alongside the live version** (e.g., v1-2026-04, v2-2026-05). Use different filenames and track multiple file IDs. `--replace` is for "the current version of this doc"; versioned archives are a different pattern.
- **Build fails with unexplained LaTeX errors.** Check `~/Local/<org>/<project>/<slug>/<slug>.tex` directly — look at the exact line the error references. 90% of the time it's an unescaped character that got through all four gotchas.

## Composes with

- **`latex-pdf`** — invoke this for the LaTeX template, Python preamble, and Tectonic compile setup. This skill adds the Unicode fixes, the media-path storage convention, and the Drive upload layer on top.
- **`google-drive`** — the underlying `gog` CLI reference. This skill uses `gog drive search`, `gog drive upload --parent`, and `gog drive upload --replace` as its only Drive touchpoints; read that skill for anything beyond those three commands.

## Do Not

- **Do not parse the markdown programmatically** to auto-generate LaTeX. Hand-translate section by section. You're not saving time — you're gaining brand control and printable quality.
- **Do not commit the build script to the org repo** unless it's genuinely reusable across multiple docs. Coupled scripts with hardcoded file IDs belong next to their artifacts in the media path.
- **Do not upload without the Unicode check and visual check.** A broken PDF with empty boxes looks fine on screen.
- **Do not forget to capture and return the Drive file ID.** Without it, the next edit creates a duplicate and breaks existing share links.
