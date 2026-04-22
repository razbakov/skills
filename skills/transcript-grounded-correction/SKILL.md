---
name: transcript-grounded-correction
description: Re-ground a session/meeting summary (and every artifact built on it) against the raw transcript, when the summary was written first and the transcript became available later. Use whenever a raw transcript becomes accessible after a summary-based artifact exists, whenever the user pushes back on a fact in a summary, whenever you notice a downstream contradiction, or whenever you're about to edit a contact/reflection/issue that was built on a pre-transcript summary. Do not skip this even if the summary "seems fine" — summaries written from memory or from an AI auto-summary routinely contain speaker mis-attributions, framing drift, missed threads, and inverted consents, and every downstream artifact silently inherits those errors until somebody pulls the tape. This applies to any transcription source (Jamie, Fireflies, Otter, Granola, Rev, manual recording) and any artifact system (markdown sessions, CRM contacts, coaching journals, issue trackers).
user_invocable: true
---

# Transcript-grounded correction

## Why this exists

Meeting summaries written before the raw transcript is read contain errors that are invisible until somebody listens back. Two error modes matter:

1. **Factual errors** — wrong speaker, wrong name, wrong number, wrong sequence, inverted consent ("rejected" vs "agreed after reframe").
2. **Framing drift** — tone, register, emotional weight, what was foreground vs background. Auto-summaries flatten this. Memory-based summaries project mood.

Downstream artifacts (contact profiles, coaching reflections, issues, tasks) inherit these errors and **propagate them as facts**. By the time a mistake surfaces, three or four files quote the original wrong summary as source. Re-grounding fixes the root; the root fixes the tree.

This is not optional polish. A corrected coaching reflection that says "I was wrong about these three things" is higher-trust than one that silently edits history.

## When to invoke this

- A raw transcript becomes available for a session that was already summarized.
- The user corrects a fact in the summary ("no, that was X not Y", "it was my father, not my brother").
- Two artifacts contradict each other and the disagreement traces back to a summary.
- About to edit a downstream artifact (contact, reflection, issue) that was built on a pre-transcript summary — re-ground first, edit second.
- Systematic backfill: you notice the summary archive is unevenly transcripted, and you want to close the gap before more artifacts compound the drift.

## Process

### Step 1 — Pull the raw transcript

Find the authoritative source. This varies by tool (web UI, API, local file, DB). Get speaker-separated text with timestamps if possible. If the export has anomalies (missing speaker labels for a block, truncation, off-by-one attribution), **document the anomaly inline** in the session file, not just in your head — the next reader needs to know where to trust and where to verify.

### Step 2 — Attach the transcript to the session file

Append under a clear heading (`## Транскрипт` / `## Transcript`). Keep it verbatim; do not clean up ums, repetitions, or "bad grammar" — these carry register information. If the export had an anomalous block, add a one-line note in italics above that block describing what's wrong.

The session file becomes the **anchor** — every other artifact cites it, not the auto-summary.

### Step 3 — Diff pass: find what the summary got wrong

Read the original summary alongside the transcript. List:

- **Speaker mis-attributions** — who said what. This is the most common error, especially when a tool mislabels one recurring speaker.
- **Factual inversions** — "agreed" vs "agreed after reframe", "refused" vs "resisted then consented", "said yes" vs "said something adjacent".
- **Missed threads** — topics in the transcript that did not make the summary. Sometimes the most important thing in the call is what the summary cut.
- **Framing drift** — the summary's tone vs the actual register. Clinical vs political, grieving vs matter-of-fact, etc.
- **Name and identity errors** — wrong person, wrong relationship, wrong role.

Write this diff list compactly in your reply to the user before editing anything. It's their chance to push back before you propagate.

### Step 4 — Propagate correction by artifact class

Different artifacts need different treatment. Do not use one rule for all.

#### Session file — REWRITE
The session summary is a derivative of the transcript. It was wrong, and now we have the source. Rewrite it in place. Include at the top a small note like: "Corrected from original summary on YYYY-MM-DD after raw transcript reading."

#### Contact / profile file — UPDATE AND ADD
A contact file captures a person's identity across time. Don't rewrite history — **add** corrected observations and **update** specific fields that were wrong. If the original contact said "military surgeon" and the transcript reveals "civilian surgeon in a military hospital", update the field *and* keep a short note about the distinction so future readers understand why. For character notes, add a dated section anchored to the call date.

#### Coaching / reflection / journal file — REWRITE WITH EXPLICIT ACCOUNTABILITY
These are interpretive files. When the interpretation was built on wrong facts, rewrite — but include a visible section at the top along the lines of:

> Previous version had N errors (list them). Transcript reading reversed them. This is the grounded rewrite.

This is not performative humility. It's epistemic hygiene: the reader needs to know the interpretation was revised, otherwise they'll trust the new one the same way they trusted the old one. If the file lives in version control, the diff already tells the story — but humans don't read diffs by default, and future you is a human.

#### Issue tracker / ticket / task — APPEND, DO NOT REWRITE BODY
**This is the rule that costs discipline to follow.**

If an issue captures a commitment, consent, or agreement ("X agreed to Y", "we decided Z"), the body is a historical record. Rewriting it erases the record and replaces it with a retconned version that looks like the truth was always known.

Instead: **add a comment** describing the correction. The comment can be long. It can reverse the body's conclusion. It can change the scope. But the body stays, so anyone reading in a year sees both what was agreed *and* what was learned. Title updates are acceptable when the title contains a status flag that's now wrong (e.g. `— parked` → `— active, first step pending`), because the title functions as current state, not historical record. Body stays.

This rule generalizes: **anywhere a commitment or consent is captured, append — don't overwrite**. The history of what was agreed is often more important than the refined scope that emerged later.

#### Follow-up tasks / calendar events — VERIFY, THEN UPDATE
Check that the surface still reflects reality. If the task was "check if X did Y by date", and the transcript shows the agreement was actually "X will do Z", update or replace the task. Calendar events with titles referencing the old framing should be updated; descriptions can keep the correction trail.

### Step 5 — Commit with a descriptive delta

One commit for the correction is usually right (all files that are sharing the same re-grounding). The commit message should name the specific errors corrected — not "fix summary" but "fix X, Y, Z in session file; scope change in issue #N; reflection rewrite with explicit 'was wrong about' section". Future you is searching commit history for this.

If the issue comment was added via API/CLI separately from the git commit, mention it in the commit message so the trail is findable from either direction.

### Step 6 — Report to the user

Summarize what was wrong, what changed, and what remains open. Include links/IDs to updated artifacts. If the diff revealed something that needs a new conversation with a human (e.g. a missed thread that needs to be raised on the next call), surface that as an open item — don't let the correction itself become the end of the thread.

## What this skill does not do

- Does not pull transcripts from a specific tool — use whatever the org has (Jamie, Fireflies, etc.). The skill is the re-grounding *process*; the pull method belongs in the org's CLAUDE.md.
- Does not re-analyze. Correction and re-analysis are different tasks. If you want a fresh interpretation from the transcript (a full new coaching read, a new S3 framing), that's a separate invocation — this skill's job ends at "the artifacts now reflect the transcript".
- Does not fix the upstream pipeline. If summaries are systematically written before transcripts arrive, the real fix is in the pipeline, not in serial corrections. After a few of these, raise the upstream issue with the user.

## Common failure modes

- **Rewriting the issue body** — hardest rule to follow because it feels cleaner. Resist. Commitments are history.
- **Silently editing a reflection** — looks harmless; destroys trust. The accountability section matters more than the corrected text.
- **Propagating the *new* framing as certainty** — the transcript is authoritative on *what was said*, not on your interpretation of it. When you write the grounded version, label inferences as inferences.
- **Stopping at the session file** — the whole point is the downstream propagation. A corrected session file with a stale contact and a stale reflection is worse than no correction, because the contradiction now lives across files.
- **Over-scoping the fix** — don't use a transcript correction as cover for expanding scope on unrelated artifacts. If you find additional issues while reading, surface them separately.

## Checklist

Before closing the correction:

- [ ] Raw transcript attached to session file, anomalies noted.
- [ ] Session file rewritten, with a one-line note about the correction.
- [ ] Contact/profile files updated (fields corrected, dated notes added).
- [ ] Coaching/reflection files rewritten with explicit accountability section.
- [ ] Issue bodies untouched; corrections added as comments. Titles updated only where they carry current-state flags.
- [ ] Follow-up tasks / calendar events verified or updated.
- [ ] Single commit (or two — one for files, one noting the issue-comment delta) with a descriptive message naming the specific errors corrected.
- [ ] Report to the user naming: what was wrong, what's now corrected, what stayed on purpose (bodies, history), what remains open.
