---
name: review-backlog
description: Use when reviewing user stories, auditing backlog quality, or checking story consistency before sprint planning. Use when docs/backlog.yaml and docs/issues/ exist and need quality validation.
---

# Review Backlog

## Overview

Parallel quality audit of all user stories in a backlog. Dispatches one sub-agent per epic to review every story file against a standard checklist, then consolidates findings into a single report with ratings, systemic issues, and prioritized fixes.

## When to Use

- Before sprint planning to catch gaps in acceptance criteria
- After generating stories with the `user-story` skill to validate quality
- When onboarding to a project to understand backlog health
- When a PM or tech lead asks "are our stories ready?"

## Requirements

- `docs/backlog.yaml` exists with phases and story references
- `docs/issues/*.md` story files exist (one per story)
- Story files follow the standard format: frontmatter (`estimation`, `story`, `jira`), Context, User Story, Acceptance Criteria

## Workflow

### Step 1: Load the backlog

Read `docs/backlog.yaml` to get:

- All phases and their stories
- Story keys (map to filenames in `docs/issues/`)
- Story IDs (map to story map numbering)
- Total story count

### Step 2: Group stories by epic/phase

Organize stories into groups for parallel review. Each group becomes one sub-agent task. Group by phase from the backlog (not by epic from the story map) since phases represent implementation order.

### Step 3: Dispatch parallel sub-agents

Launch one sub-agent per phase using the Task tool. All agents run in parallel.

Each sub-agent receives:

- The list of story file paths to review
- The review checklist (see below)
- Instructions to output per-story ratings and an epic-level summary

### Step 4: Consolidate results

After all agents return, compile:

1. **Ratings table** — every story with its rating (Good / Needs improvement / Problem)
2. **Systemic issues** — patterns that recur across multiple epics
3. **Top priority fixes** — ordered by impact, actionable

## Review Checklist (for sub-agents)

Each sub-agent evaluates every story against these criteria:

### Per-Story Evaluation

| # | Criterion | What to check |
|---|-----------|---------------|
| 1 | **Frontmatter** | Has `estimation`, `story`, `jira` fields? Values populated? |
| 2 | **Context** | Is the "why" clearly explained? Grounded in user need? |
| 3 | **User Story** | Follows "As a [persona], I want [action], so that [benefit]"? |
| 4 | **Acceptance Criteria** | Concrete, testable, checkbox-ready? Enough criteria for the scope? |
| 5 | **Edge Cases** | Missing error states? Empty/zero-result states? Failure paths? |
| 6 | **Consistency** | Story number, persona, and scope match the story map? |
| 7 | **Estimation** | Points reasonable for the described scope? Assumptions documented? |

### Per-Story Output Format

```
### File: `<filename>` (Story <id>)

**Rating: [Good | Needs improvement | Problem]**

**Issues:**
- Numbered list of specific problems

**Suggestions:**
- Concrete improvements with example wording
```

### Epic-Level Summary

After all stories in the group, the sub-agent outputs:

- Common strengths across the epic
- Recurring weaknesses
- Cross-story dependency gaps
- Estimation concerns

## Rating Scale

- **Good** — Frontmatter complete, user story well-formed, acceptance criteria testable with minor gaps only
- **Needs improvement** — Missing edge cases, underspecified criteria, or consistency issues that should be fixed before implementation
- **Problem** — Structural issues: missing sections, wrong persona, acceptance criteria that are not testable, or scope that contradicts the story map

## Sub-Agent Prompt Template

Use this when dispatching each sub-agent:

```
Review the user story files for [Phase Name]. Read each file and evaluate against these criteria:

1. **Frontmatter**: Does it have `estimation`, `story`, and `jira` fields?
2. **Context**: Is the "why" clearly explained?
3. **User Story**: Follows "As a [persona], I want [action], so that [benefit]" format?
4. **Acceptance Criteria**: Are they concrete, testable, and checkbox-ready? Are there enough criteria? Are any missing edge cases?
5. **Consistency**: Does the story match what's described in the story map (story number, persona, scope)?
6. **Estimation**: Does the story point estimate seem reasonable for the scope described?

Files to review:
- [list of absolute file paths]

For each story, output:
- **File**: filename
- **Rating**: Good / Needs improvement / Problem
- **Issues**: List specific problems or missing items
- **Suggestions**: Concrete improvements

At the end, provide a summary of common patterns across this phase.
```

## Systemic Issues to Watch For

These problems recur across most backlogs. Flag them in the consolidated report:

1. **Missing empty/zero-result states** — what does the user see before any data exists?
2. **Missing error and failure criteria** — network errors, API failures, partial failures
3. **Invisible cross-story dependencies** — one story assumes another is done but doesn't say so
4. **Undefined workflow handoffs** — multi-step workflows where step transitions are ambiguous
5. **Real-time propagation underspecified** — "takes effect immediately" without mechanism
6. **Unanchored estimates** — no assumptions documented to validate story points
7. **Missing Out of Scope sections** — especially for integration stories
8. **Story map mismatches** — title, persona, or scope drift between map and issue file
9. **Last-admin protection missing** — role/access stories that could orphan a project
10. **Heading/naming inconsistencies** — prefix conventions, title wording drift

## Output Format

The final consolidated report should include:

### 1. Ratings Overview Table

| Epic | Story | Key | Rating |
|------|-------|-----|--------|

### 2. Score Summary

X Good, Y Need improvement, Z Problems

### 3. Systemic Issues

Numbered list of cross-cutting problems with specific examples from the stories.

### 4. Top Priority Fixes

Ordered by impact. Each fix should be actionable (e.g., "Add empty state criteria to every story" not "improve stories").
