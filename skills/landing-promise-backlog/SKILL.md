---
name: landing-promise-backlog
description: Turn a product's landing/marketing pages into a prioritized, gap-analyzed backlog. Use this whenever the user wants to audit what a site promises vs. what is actually built, convert marketing/landing copy into user stories, map work to Critical User Journeys (CUJs) and Jobs-To-Be-Done (JTBDs), score a backlog with WSJF, or populate an issue tracker (Linear, Jira, GitHub Issues) plus a tracking spreadsheet from a product's promises — even if they don't say the word "backlog" or "skill". Reach for it on requests like "audit our landing pages", "promise vs reality / what do we promise that we haven't built", "turn the marketing into a backlog", "make user stories from the site", "build a CUJ/JTBD map", "prioritize this with WSJF", or "get our promises into Linear/Jira". Also use it to maintain such a backlog after it exists.
compatibility: Works best with parallel sub-agents (for extraction, classification, and bulk tracker writes) and an issue-tracker reachable via API or MCP. Degrades gracefully without them (do the phases serially). Pairs with the `user-story` skill for the repo story format.
---

<role>
You are a product operator who converts a product's outward promises into an honest, prioritized, buildable backlog. You read the marketing surface, verify each claim against the actual codebase, and turn the gap into work that is traceable across three surfaces (repo, tracker, sheet) and never drifts. You are blunt about what is not built — the value of this exercise is the gap, not a tidy list.
</role>

## When to use

The user has a product with landing/marketing pages (a home page, "for organizers", pricing, feature pages, etc.) and wants any of: an audit of promises vs. what's built, a user-story backlog derived from the copy, a CUJ/JTBD map, WSJF prioritization, or a populated issue tracker + tracking sheet. Also use to *maintain* such a backlog after it exists.

## Core principles

- **One source of truth per thing.** Story *content* lives in repo files. The *work* lives in the tracker. The *index* lives in a sheet. Keep them 1:1 by a stable id; never duplicate full story text into the sheet (it drifts).
- **Ground every claim in the code.** Status (built / partial / not-built) is verified against the real codebase, not guessed. The gap is the point.
- **One rubric for the whole set.** WSJF and every scoring dimension use a single rubric applied uniformly, or the relative ranking is meaningless.
- **Fan out, stay consistent.** Use parallel sub-agents for extraction, classification, and tracker writes — but give them a shared rubric/reality-map so their output is comparable.
- **Short titles, detail in the body.** Tracker/issue titles are 2–4 word spoken handles ("Who's Going", "One-Tap Ticket"). All detail lives in the description.

## Process

### Phase 1 — Inventory the surface
List every landing/marketing page (routes). Exclude prototypes, legal, and purely functional pages. Confirm the list with the user if ambiguous.

### Phase 2 — Extract promises (fan out)
Dispatch one reader per page or small group. Each returns rows in a fixed shape:
`Page | Type | Claim | Section | Audience`
- **Type** ∈ Promise · Feature · Use case · CTA.
- **Claim** = verbatim/lightly-trimmed copy (join styled-span headlines into a readable line).
- **Audience** = the persona it targets (or "All").
Be exhaustive — capture every distinct claim, don't summarize into fewer.

### Phase 3 — Assign ids + order
Give each row a stable id and a plain sequential **Order** (so the original sort is always recoverable). A good id scheme groups by audience/journey then numbers within the group (e.g. `P<group><nn>` → `P205`, `P732`). The id is the join key across repo, tracker, and sheet — keep it forever.

### Phase 4 — Define CUJ + JTBD taxonomies, classify
Define the product's **Critical User Journeys** (CUJs — the handful of end-to-end paths that matter, e.g. C1..C8) and **Jobs-To-Be-Done** (JTBDs — the underlying jobs, J1..Jn). Write them to a reference doc. Classify each row to one CUJ and one JTBD (a page+audience+keyword heuristic is a fine first pass; state that it's automated so the user can correct).

### Phase 5 — Status vs. the codebase (the gap analysis)
Classify each item **built / partial / not-built** against the real code:
- built = works in prod with a real backend/data path
- partial = UI or partial impl only — stubbed, mock-only, session-only, lead-gen-by-email, or missing its backend
- not-built = aspirational copy, no implementation
Write a shared **reality-map** (what you know is built/partial/not-built) and hand it to the classifier sub-agents so they stay consistent; tell them to verify against routers/schema/components/mocks and, when torn between built and partial, choose partial.

### Phase 6 — WSJF score (one rubric)
Score each item: **WSJF = (Business Value + Time Criticality + Risk-Reduction/Opportunity) ÷ Job Size**, Fibonacci-scaled (1,2,3,5,8,13). Assign the Cost-of-Delay components by *theme* (e.g. flagship differentiator = highest value) and Job Size by *status* (built≈1, partial 3–5, not-built 8–13, larger for backend-heavy work). A script applying the rubric keeps it comparable and transparent — report the distribution so the user can sanity-check. Highest WSJF = cheap high-value wins; big differentiators land mid (high value, high size) — sequence them deliberately, not first.

### Phase 7 — Generate user stories (repo, source of truth)
One markdown file per item, e.g. `docs/issues/<id>-<slug>.md`. Use the INVEST/user-story format (see the `user-story` skill): frontmatter (`title`, `type`, `id`/`p`, `page`, `audience`, `cuj`, `jtbd`, `status`, WSJF components, `source`) + an "As a … I want … so that …" sentence + ≤8 plain-language acceptance criteria grounded in real page names. Titles are short handles.

### Phase 8 — Sync to the tracker (the work)
Create one issue per story (or the actionable subset) via the tracker's API/MCP, using **parallel sub-agents over sliced payloads** (bulk one-at-a-time creation is otherwise too slow). Then organize:
- **Group into Projects by CUJ** (one project per journey).
- **Labels** for every filter axis: `status:*`, `cuj:*`, `jtbd:*`, `aud:*`, plus a run tag.
- **Priority** from WSJF band. **State** from status (built→Done, partial→Todo, not-built→Backlog).
- **Seed the first cycle/sprint** with the highest-WSJF *unblocked* items (skip anything gated on a big not-built dependency).
Verify with a read-only agent: distinct id count == expected, no duplicates, every issue has a project + labels.

### Phase 9 — Sheet index + links
Put the flat table in a spreadsheet tab (id, page, type, claim, audience, CUJ, JTBD, status, WSJF) and add a **link column** pointing each row to its tracker issue. The sheet is the index; the tracker is the detail; do not copy full story text into it.

## Execution pattern (important)

- **Parallelize** extraction, status-classification, story-generation, and tracker-writes with sub-agents over slices (~6 slices). Give each the shared rubric/reality-map inline so results are consistent.
- **Verify with a separate read-only agent** after each bulk write (counts, duplicates, coverage) rather than trusting the writers' self-reports.
- **Scripts for anything mechanical** (id assignment, WSJF math, slug generation, sheet writes) so it's deterministic and re-runnable.

## Outputs

1. `docs/issues/<id>-*.md` — one story per promise (+ a CUJ/JTBD reference doc).
2. Tracker issues — organized by project, labeled, prioritized, first cycle seeded.
3. Spreadsheet tab — the linked index.
All three kept 1:1 by the stable id.

## Integration points

- **Trackers:** any with an API/MCP — Linear, Jira, GitHub Issues. Bulk-create via sub-agents; group/label/prioritize per the tracker's model.
- **Sheets:** Google Sheets (via a sheets CLI/API) or Excel. Add tabs/columns; link to the tracker.
- **User-story format:** reuse the `user-story` skill's INVEST template for the repo files.

## Pitfalls

- **Don't guess status.** Verify against code; a mis-labeled "built" hides the real gap.
- **Don't inconsistently score.** One WSJF rubric across the whole set, or the ranking lies.
- **Don't duplicate content into the sheet.** Link, don't copy — a 4th copy of the stories will drift and nobody will trust either.
- **Don't put big not-built epics in sprint 1.** They're high-value but large and often block partials; bank cheap wins first.
- **Titles are handles, not sentences.** Keep the id as a short prefix only if the tracker needs it; otherwise the filename/field carries traceability.
