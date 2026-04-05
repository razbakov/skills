---
description: "Daily Review (Meta-Skill) — orchestrates 10 child skills: gather browser history, AI transcripts, app usage, process Telegram inbox, process Chrome bookmarks, sync all projects, suggest agent tasks, suggest today's plan, sync to calendar, and save the review."
user_invocable: true
---

# Daily Review (Meta-Skill)

Run from the ikigai project directory. Gathers yesterday's activity, syncs all project next steps (with full git analysis), suggests today's plan, and adds approved plan to Google Calendar. Saves the review to `sessions/YYYY-MM-DD-daily-review.md`.

This meta-skill orchestrates the following child skills in order:

1. **daily-review-browser-history** — Gather yesterday's Chrome browser history
2. **daily-review-ai-transcripts** — Gather yesterday's AI session transcripts
3. **daily-review-app-usage** — Query macOS app focus time
4. **process-inbox** — Collect Telegram + process Notion "To do" cards (GTD full pipeline)
5. **daily-review-browser-bookmarks** — Process Chrome bookmarks (GTD)
6. **daily-review-sync-projects** — Discover, pull, analyze all projects
6.5. **suggest-tasks** — Propose agent tasks with assignments (Viktor/Luna/Marco/Kai)
7. **daily-review-suggest-plan** — Propose today's schedule with OKR view
8. **daily-review-calendar-sync** — Create Google Calendar events
9. **daily-review-save-review** — Save complete review to sessions file

## Trigger

User says "daily review", "let's review projects", "daily check-in", or invokes `/daily-review`.

## Context

- **Working directory:** `~/Projects/ikigai`
- **Google account:** From CLAUDE.md Personal Info
- **Calendar tool:** `gog cal`
- **Projects directory:** `~/Projects/`
- **Project inventory:** `PROJECTS.md` in ikigai workspace
- **OKRs and focus:** `README.md` in ikigai workspace
- **Session storage:** `sessions/`

## Execution

### Phase 1 — Gather Yesterday's Data (parallel)

Run steps 1-5 in parallel where possible to save time.

#### Step 1: Browser History
Invoke: `//daily-review-browser-history`
Captures: `sessions/YYYY-MM-DD-browser.md`

#### Step 2: AI Transcripts
Invoke: `//daily-review-ai-transcripts`
Captures: `sessions/YYYY-MM-DD-ai-sessions.md`

#### Step 3: App Usage
Invoke: `//daily-review-app-usage`
Depends on: Step 1 (appends to browser.md)
Captures: App usage section in `sessions/YYYY-MM-DD-browser.md`

#### Step 4: Process Inbox (Telegram + Notion)
Invoke: `//process-inbox`
Captures: Telegram export → Notion cards → agent dispatch. Saves `inbox/YYYY-MM-DD-HH-MM.md`, creates Control Center cards, dispatches agents for "To do" items.

#### Step 5: Browser Bookmarks
Invoke: `//daily-review-browser-bookmarks`
Captures: `inbox/YYYY-MM-DD-HH-MM-bookmarks.md`, updated project docs

### Phase 2 — Sync & Plan (sequential)

#### Step 6: Sync Projects
Invoke: `//daily-review-sync-projects`
Depends on: Steps 4-5 (Telegram and bookmark items may add tasks to projects)
Captures: Numbered project list with a/b/c task IDs, updated PROJECTS.md

**User interaction:** "Which projects do you want to focus on today?"

#### Step 6.5: Suggest Agent Tasks
Invoke: `//suggest-tasks`
Depends on: Step 6 (needs project list, PROJECTS.md, and Notion state)
Captures: "Suggested" cards in Notion Control Center with agent assignments (Viktor/Luna/Marco/Kai)

No user interaction needed — cards are created silently. The suggest-plan step (7) will mention how many agent tasks were suggested.

#### Step 7: Suggest Plan
Invoke: `//daily-review-suggest-plan`
Depends on: Steps 1-6 (needs yesterday's data + project list with task IDs)
Captures: OKR view with proposed schedule

**User interaction:** "Does this plan work, or do you want to adjust?"

#### Step 8: Calendar Sync
Invoke: `//daily-review-calendar-sync`
Depends on: Step 7 (needs approved schedule)
Captures: List of calendar events created

#### Step 9: Save Review
Invoke: `//daily-review-save-review`
Depends on: All previous steps
Captures: `sessions/YYYY-MM-DD-daily-review.md`

**User interaction:** Personal journaling prompt. (Scrum standup is handled separately by `/daily-standup` at 9am.)

## Notes

- Each child skill can also be run independently via `/daily-review-{name}`
- If a step fails, fix the issue and re-run that specific child skill
- If the user says "skip yesterday" — jump straight to Step 6
- Steps 1, 2, 4, and 5 have no dependencies on each other and should run in parallel
- Step 3 depends on Step 1 (appends to the same file)
- Sub-agents in Step 6 should run in parallel for speed — one agent per project
- If today is Saturday, Step 7 will remind about the weekly review
- **Always print the full output (project list + OKR view) to chat.** Saving to file is not a substitute for showing the user. This applies to BOTH interactive and automated/scheduled runs — the user reads the output after the fact
- Actionable items from Telegram inbox and bookmarks should be merged into the project list
- **Automated runs:** When running as a scheduled task without the user present, still execute ALL steps including full project sync (Step 6). Skip only steps that truly require real-time user input (plan approval, journaling). Always produce the complete report with git pull table + numbered project list + OKR view
- **Project paths:** Many repos are nested. Always read the Project Path Registry from CLAUDE.md — never assume `~/Projects/<name>/.git`
