---
description: Gather yesterday's Chrome browser history, group by time blocks, and save to sessions file. Part of the daily review workflow.
user_invocable: true
---

# Daily Review — Browser History

Gathers yesterday's Chrome browser history and saves a structured summary to `sessions/YYYY-MM-DD-browser.md`.

## Trigger

Invoked as part of `/daily-review` or independently via `/daily-review-browser-history`.

## Context

- **Working directory:** `~/Projects/ikigai`
- **Session storage:** `sessions/`
- **Date:** Use yesterday's date (YYYY-MM-DD)

## Process

### Skip check

Skip if `sessions/YYYY-MM-DD-browser.md` already exists for yesterday. Report "already exists, skipping" and stop.

### 1. Copy Chrome history DB

Chrome locks its database file. Copy it first:

```bash
cp ~/Library/Application\ Support/Google/Chrome/Default/History /tmp/chrome_history.db
```

### 2. Query yesterday's URLs

```sql
SELECT url, title, datetime(last_visit_time/1000000-11644473600, 'unixepoch', 'localtime') as visit_time
FROM urls
WHERE date(last_visit_time/1000000-11644473600, 'unixepoch', 'localtime') = 'YYYY-MM-DD'
ORDER BY last_visit_time ASC
```

Replace `YYYY-MM-DD` with yesterday's actual date.

### 3. Save results

Save to `sessions/YYYY-MM-DD-browser.md` with:
- Summary grouped by time blocks (morning, afternoon, evening, late night)
- Key activities table (category, time spent, details)
- Notable observations

## Output

The file path of the saved browser history file, or a note that it was skipped.
