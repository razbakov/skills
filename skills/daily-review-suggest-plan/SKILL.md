---
description: Read calendar, OKRs, yesterday's activity, and project list to propose today's schedule with task IDs. Part of the daily review workflow.
user_invocable: true
---

> **⚠️ Migration in progress (razbakov/ikigai#73):** Control Center has moved from Notion to GitHub Issues + Project v2. When this skill references creating/reading/updating Notion cards or pages, translate to GitHub equivalents:
> - **Create card** → `gh issue create --repo <project-repo> --title "<title>" --label agent:<name> --body "<S3 body>"` then `gh project item-add 5 --owner razbakov --url <issue-url>`
> - **Read cards** → `gh issue list --repo <repo> --label agent:<name> --state open` (or across repos via `gh search issues "org:razbakov label:agent:<name> state:open"`)
> - **Update card status** → move on board: `gh project item-edit` with the Status field, or close via `gh issue close`
> - **Board columns**: Inbox → To do → In progress → To review → Done
> - **Do not call any `notion-*` MCP tools** — the Notion MCP is disabled.



# Daily Review — Suggest Today's Plan (GTD Reflect + Engage)

Uses task IDs from the project sync step. Reorganizes tasks by objective, adds risks/unknowns, and picks what matters today.

## Trigger

Invoked as part of `/daily-review` or independently via `/daily-review-suggest-plan`.

## Context

- **Working directory:** `~/Projects/ikigai`
- **Google account:** From CLAUDE.md Personal Info
- **Calendar tool:** `gog cal`
- **OKRs:** `README.md` in ikigai workspace
- **Project list:** Output from `/daily-review-sync-projects` (numbered tasks with a/b/c IDs)
- **Yesterday's activity:** `sessions/YYYY-MM-DD-browser.md`, `sessions/YYYY-MM-DD-ai-sessions.md`

## Process

### 1. Read today's calendar

```bash
gog cal ls --from today --to today
```

### 2. Read OKRs

Read `README.md` for current OKRs and focus areas.

### 3. Review yesterday's activity

From browser history, AI sessions, and app usage files — what had momentum?

### 4. Check contacts for pending commitments

Scan `contacts/*/contact.md` for deadlines or promises.

### 5. Present the OKR view

One section per objective, referencing task IDs from the project list:

```
## Yesterday
<2-3 sentence summary from browser + AI session + app usage files>

## Today's Calendar
<existing events>

## O1: <Objective name>

**Risks:** what could stop us from reaching the objective?
**Unknowns:** what should we figure out to avoid obstacles?

**Next Steps:**
- <id> — <project> — <task>
- <id> — <project> — <task>

## O2: <Objective name>

**Risks:** ...
**Unknowns:** ...

**Next Steps:**
- <id> — <project> — <task>
- <id> — <project> — <task>

### Proposed Schedule

| Time | Tasks |
|------|-------|
| HH:MM-HH:MM | <id>, <id> — <project> — <summary> |
| HH:MM-HH:MM | <id>, <id> — <project> — <summary> |
```

**Format rules:**
- Task IDs reference the project list (e.g., "2a" = project 2, task a)
- Each next step line format: `<id> — <project> — <task>`
- Tasks are defined once in the project list, only referenced here — no duplication
- Next Steps are ordered by priority within each objective, not by project number
- The schedule uses the same IDs so the user can trace back to the project
- Output headings should NOT include internal step numbers (no "Step 4", "Step 5")

**Prioritization rules:**
- Deadlines first (what's due soonest?)
- OKR alignment (does it move a key result?)
- Partner commitments (promises to Kirill, etc.)
- Momentum (what was in progress yesterday?)
- Avoid context switching — max 3 projects per day

### 6. Mention suggested agent tasks

If `/suggest-tasks` ran before this step (e.g., as part of daily-review step 6.5), include a section:

```
## Agent Tasks (Suggested)

N new tasks suggested in Notion Control Center:
- <task> → <Agent> (Priority)
- <task> → <Agent> (Priority)

To approve: review in Notion → drag "Suggested" → "To do" → run `/dispatch-approved`
```

If suggest-tasks did not run, skip this section.

### 7. Add meal suggestion to lunch/dinner blocks

When the proposed schedule includes a lunch or dinner block, invoke `/meal-suggestion` to populate it with inventory-checked meal options. The meal suggestion output goes into the calendar event description when syncing.

### 8. Check current time

Always check the system clock to avoid suggesting past time blocks.

### 9. Saturday reminder

If today is Saturday, remind about the weekly review + planning ritual (10:00-11:00).

Ask: "Does this plan work, or do you want to adjust?"

## Output

The full OKR view with proposed schedule, printed to chat.
