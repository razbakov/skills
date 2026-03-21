---
description: Discover all projects, git pull, spawn sub-agents to analyze each, update PROJECTS.md with consolidated report. Part of the daily review workflow.
user_invocable: true
---

# Daily Review — Sync All Project Next Steps (GTD Organize)

Discovers all projects, pulls latest changes, analyzes each via sub-agents, updates PROJECTS.md, and produces a consolidated report with numbered tasks.

## Trigger

Invoked as part of `/daily-review` or independently via `/daily-review-sync-projects`.

## Context

- **Working directory:** `~/Projects/ikigai`
- **Projects directory:** `~/Projects/`
- **Project inventory:** `PROJECTS.md` in ikigai workspace
- **OKRs:** `README.md` in ikigai workspace

## Process

### 5a — Discover Projects

1. List all directories in `~/Projects/` that contain a `.git/` folder (skip `.archive/`, `node_modules/`, etc.).
2. Build the project list with their paths.

### 5b — Git Pull All Projects

For each discovered project, run `git pull --ff-only` on the default branch. Collect results.

Present a quick summary:

```
## Git Pull Results
| Project | Branch | Result |
|---------|--------|--------|
| wedance | main | Already up to date |
| sdtv | main | 3 new commits pulled |
| brievcase | main | Error: no remote |
```

### 5c — Spawn Sub-agents per Project

Launch one sub-agent per project **in parallel** using the Agent tool. Each sub-agent receives:

**Prompt template:**
```
Analyze the project at {project_path}. This is a read-only analysis — do NOT modify any files.

1. **Git history** — Run `git log --oneline --since="2 weeks ago"` and `git log --oneline -20`. Summarize:
   - Last commit date
   - Number of commits in the last 2 weeks
   - Key changes (group by theme, not individual commits)
   - Active contributors

2. **Read project docs** — Read `README.md`, `CLAUDE.md`, `TODO.md`, `CHANGELOG.md`, `package.json`, or any top-level docs that exist. Extract:
   - Project description / purpose
   - Current status (if stated)
   - Stated next steps or TODOs
   - Tech stack
   - Any deadlines or commitments mentioned

3. **Identify next tasks** — Based on git history and docs, suggest 1-3 concrete next actions for this project. Be specific (e.g., "Fix the Dropbox sync error in src/sync.ts" not "Continue working on sync").

4. **Activity assessment** — Classify the project:
   - **Active**: commits in the last 2 weeks, or stated deadlines/commitments ahead
   - **Stale**: no commits in 2+ weeks but has stated goals or unfinished work
   - **Archive candidate**: no commits in 4+ weeks, no stated goals, no deadlines

Return your findings in this exact format:

## {project_name}
- **Path:** {project_path}
- **Description:** one-line summary
- **Tech stack:** key technologies
- **Last commit:** YYYY-MM-DD
- **Commits (2 weeks):** N
- **Status:** Active / Stale / Archive candidate
- **Reason:** why this classification
- **Next tasks:**
  - task 1
  - task 2
  - task 3
```

### 5d — Consolidate Report and Update PROJECTS.md

After all sub-agents complete:

1. Read current `PROJECTS.md` and update:
   - **Status** and **Next actions** from sub-agent findings
   - Flag any projects recommended for archiving
   - Flag stale deadlines (dates that have passed)
   - Only update fields that changed — do NOT rewrite the entire file

2. Present the project summary in this exact format:

```
1. **ProjectName** — O1: KR1 (short KR description)
   - a) First next task
   - b) Second next task
   - c) Third next task

2. **ProjectName** — O2: KR3 (short KR description)
   - a) First next task
   - b) Second next task
   - c) Third next task
   - *Archive candidate: reason*
```

**Format rules:**
- Every project gets exactly 3 concrete next tasks (a/b/c)
- Each project maps to one OKR objective + key result (or "none" if no alignment)
- Archive candidates get all 3 tasks AND an extra italic note — "decide to archive" is NOT a task
- Tasks must be specific and actionable, not vague
- User can refer to tasks as "1a", "2b", etc.

3. Present a diff summary: what changed in PROJECTS.md since last sync.

Ask: "Which projects do you want to focus on today?"

## Output

The numbered project list with a/b/c tasks and OKR mapping, plus PROJECTS.md diff summary.
