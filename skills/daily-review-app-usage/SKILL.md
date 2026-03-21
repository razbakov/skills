---
description: Query macOS knowledgeC.db for yesterday's app focus time and append to browser history file. Part of the daily review workflow.
user_invocable: true
---

# Daily Review — App Usage

Queries the macOS Knowledge Store database for app focus time and appends the results to `sessions/YYYY-MM-DD-browser.md`.

## Trigger

Invoked as part of `/daily-review` or independently via `/daily-review-app-usage`.

## Context

- **Working directory:** `~/Projects/ikigai`
- **Session storage:** `sessions/`
- **Date:** Use yesterday's date (YYYY-MM-DD)
- **Requirement:** Full Disk Access for `/usr/bin/sqlite3` (System Settings > Privacy & Security > Full Disk Access)

## Process

### Skip check

Skip if `sessions/YYYY-MM-DD-browser.md` already exists and contains an "App Usage" section. Report "already exists, skipping" and stop.

### 1. Query macOS Knowledge Store

```bash
sqlite3 ~/Library/Application\ Support/Knowledge/knowledgeC.db "
SELECT
  ZOBJECT.ZVALUESTRING as app,
  ROUND(SUM(ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) / 3600.0, 1) as hours,
  ROUND(SUM(ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE) / 60.0, 0) as minutes
FROM ZOBJECT
WHERE ZSTREAMNAME = '/app/usage'
  AND date(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch', 'localtime') = 'YYYY-MM-DD'
GROUP BY ZOBJECT.ZVALUESTRING
ORDER BY hours DESC
LIMIT 20
"
```

Replace `YYYY-MM-DD` with yesterday's actual date.

If the query fails (no Full Disk Access), skip and note the failure in the review.

### 2. Append to browser history file

Append results to `sessions/YYYY-MM-DD-browser.md` as an "App Usage" section with a table:

```markdown
## App Usage

| App | Time |
|-----|------|
| Chrome | 4h 22m |
| Zed | 4h 20m |
```

Map bundle IDs to friendly names:
- `com.google.Chrome` -> Chrome
- `dev.zed.Zed` -> Zed
- `com.conductor.app` -> Conductor
- `com.mitchellh.ghostty` -> Ghostty
- `com.apple.Safari` -> Safari
- `com.tinyspeck.slackmacgap` -> Slack
- `com.hnc.Discord` -> Discord
- `us.zoom.xos` -> Zoom

Include total active screen time at the bottom.

## Output

Confirmation that app usage was appended, or a note that it was skipped/failed.
