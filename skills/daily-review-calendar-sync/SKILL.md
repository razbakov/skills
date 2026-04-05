---
description: Create Google Calendar events for the approved daily plan. Part of the daily review workflow.
user_invocable: true
---

# Daily Review — Calendar Sync

Creates Google Calendar events for each approved project block in today's plan.

## Trigger

Invoked as part of `/daily-review` or independently via `/daily-review-calendar-sync`.

## Context

- **Working directory:** `~/Projects/ikigai`
- **Google account:** From CLAUDE.md Personal Info
- **Calendar tool:** `gog cal`
- **Input:** The approved schedule from `/daily-review-suggest-plan` (user may have adjusted it)

## Process

### 1. Create calendar events

For each project block in the approved schedule, create a Google Calendar event:

```bash
gog cal create <GOOGLE_ACCOUNT> \
  --summary "<Project Name>" \
  --from "YYYY-MM-DDTHH:MM:00+01:00" \
  --to "YYYY-MM-DDTHH:MM:00+01:00" \
  --description="<id>) task, <id>) task"
```

**Important:** `--description` requires `=` sign (no space between flag and value).

### 2. Confirm

List all events created with their times and summaries.

## Output

Confirmation of all calendar events created.
