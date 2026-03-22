# Skill Similarity Analysis Report

Date: 2026-03-22

## Critical Overlaps

### 1. Issue Implementation — 3 skills doing the same thing differently

| Skill | Source | Scope | Tracker | Branch strategy |
|-------|--------|-------|---------|-----------------|
| `github-issue` | GitHub issue URL | Single issue, end-to-end | GitHub only | `feat/<desc>` |
| `developing-tickets` | Ticket ID (any tracker) | Single ticket, with story rewrite + estimation | Jira or GitHub | Plan mode handoff |
| `thank-you-next` | Auto-pick from `backlog.yaml` | Single story, auto-select | Local YAML file | `feature/<id>-<key>` |

All three fetch an issue, plan, implement, and PR. The differences:
- `github-issue` is GitHub-native, skips story rewriting, includes PR review handling
- `developing-tickets` adds story refinement (user-story + estimation skills) and supports Jira
- `thank-you-next` auto-selects from a local backlog file

**Action:** Clarify when to use each; consider extracting a shared implementation core.

### 2. "Pick next and dispatch" — 2 skills with same pattern

| Skill | Scope | Source | Dispatch |
|-------|-------|--------|----------|
| `github-next-issue` | Pick 1 Todo from GitHub Project board | GitHub Project V2 | Via `/inbox` |
| `thank-you-next` | Pick 1 not_started from `backlog.yaml` | Local YAML | Implements inline |

Both pick the next item and start work. Different data sources and execution models.

### 3. Sprint execution — `run-sprint` is `github-next-issue` in a loop

| Skill | What it does |
|-------|-------------|
| `github-next-issue` | Pick **1** Todo, move to In Progress, dispatch `/inbox` agent |
| `run-sprint` | Pick **ALL** Todos, move to In Progress, dispatch `/inbox` agents in parallel |

Steps 1-4 are copy-pasted between them. `run-sprint` should call `github-next-issue` per item.

### 4. PR Review — batch vs single

| Skill | Scope |
|-------|-------|
| `pr-review-responder` (installed) | Address comments on **1** PR |
| `review-all-prs` | Discover all PRs with unresolved threads, dispatch agent per PR |

Clean relationship — `review-all-prs` delegates to the pr-review-responder workflow. No action needed beyond documenting the relationship.

### 5. `workflow` duplicates CLAUDE.md

The `workflow` skill is a verbatim copy of the global CLAUDE.md `## Workflow Orchestration` section. It adds no new behavior — it's already loaded in every session via CLAUDE.md.

**Action:** Delete or repurpose.

## Secondary Overlaps

### Image Generation (4 skills)
- `image-from-gemini`, `image-from-html`, `image-from-latex` — three techniques
- `brand-poster` — orchestrates the above three
- Consider making `image-from-*` internal to `brand-poster` rather than standalone

### Coaching & Assessment
- `personal-coach` has an "Assessment" session type
- `year-review` is a specific L10L assessment — subset of `personal-coach`
- Risk of divergence over time

### "Start something new" space (4 skills)
- `startup`, `startup-coach`, `project-start`, `design-sprint`
- Different methodologies but overlapping triggers
- Could cause confusion about which to use

## Skills with No Overlap (well-scoped)
`estimation`, `dependency-vuln-report`, `export-chat-history`, `google-drive`, `image-to-svg`, `latex-pdf`, `s3-collaboration`, `storyteller-tactics`, `viral-threads`, `website`, `zoomer`, `north`, `freelance-job-hunt`, `daily-review-browser-bookmarks`, `weekly-review`, `review-backlog`, `research`, `analyze`
