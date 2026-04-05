---
description: Save the complete daily review to sessions/YYYY-MM-DD-daily-review.md with all gathered data and decisions. Part of the daily review workflow.
user_invocable: true
---

# Daily Review — Save Review

Saves the complete daily review to `sessions/YYYY-MM-DD-daily-review.md` with all data gathered during the review process.

## Trigger

Invoked as part of `/daily-review` or independently via `/daily-review-save-review`.

## Context

- **Working directory:** `~/Projects/ikigai`
- **Session storage:** `sessions/`
- **Date:** Today's date (YYYY-MM-DD)
- **Input:** All outputs from previous daily review steps

## Process

### 1. Compile the review

Save to `sessions/YYYY-MM-DD-daily-review.md` with the following sections:

- **Telegram Inbox (Raw)** — exact messages, unedited (from telegram-inbox step)
- **Telegram Inbox (Processed)** — GTD summary table (from telegram-inbox step)
- **Git Pull Results** — table of pull outcomes per project (from sync-projects step)
- **Project Report** — numbered project list with a/b/c tasks, status, OKR mapping (from sync-projects step)
- **PROJECTS.md Changes** — diff summary of what changed (from sync-projects step)
- **Today's Plan** — the approved OKR view and schedule (from suggest-plan step)
- **Calendar Events Created** — list of events added (from calendar-sync step)
- **Actions Taken** — any project docs updated during the review
- **Summary Stats** — total projects, active/stale/archive counts, calendar events created

### 2. Personal journaling

Ask: "What happened today outside of work?" to capture life events, social interactions, and personal moments.

Save the response raw (exact user words, unedited) in a `## Personal` section.

### 3. Scrum standup

Ask the scrum standup questions:
- What did you do?
- What are you going to do?
- Any obstacles?

Save responses in a `## Standup` section.

## Output

The file path of the saved daily review file.
