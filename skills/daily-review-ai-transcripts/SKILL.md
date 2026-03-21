---
description: Gather yesterday's AI session transcripts from Claude Code and Conductor, save structured summary to sessions file. Part of the daily review workflow.
user_invocable: true
---

# Daily Review — AI Transcripts

Gathers yesterday's AI session transcripts from Claude Code JSONL files and the Conductor app database, then saves a structured summary to `sessions/YYYY-MM-DD-ai-sessions.md`.

## Trigger

Invoked as part of `/daily-review` or independently via `/daily-review-ai-transcripts`.

## Context

- **Working directory:** `~/Projects/ikigai`
- **Session storage:** `sessions/`
- **Date:** Use yesterday's date (YYYY-MM-DD)

## Process

### Skip check

Skip if `sessions/YYYY-MM-DD-ai-sessions.md` already exists for yesterday. Report "already exists, skipping" and stop.

### Source A: Claude Code JSONL files

1. Find all JSONL files modified yesterday:

```bash
find ~/.claude/projects -maxdepth 2 -name "*.jsonl" -not -path "*/subagents/*" -type f | while read f; do
  mod=$(stat -f '%Sm' -t '%Y-%m-%d' "$f")
  if [ "$mod" = "YYYY-MM-DD" ]; then
    created=$(stat -f '%SB' -t '%H:%M' "$f")
    modified=$(stat -f '%Sm' -t '%H:%M' "$f")
    size=$(stat -f '%z' "$f")
    proj=$(echo "$f" | sed 's|.*/\.claude/projects/||' | sed 's|/[^/]*$||')
    echo "$proj|$created|$modified|$size|$f"
  fi
done | sort
```

2. Group by project. For the top 3 projects by total size, extract human messages:

```python
import json
with open('FILE') as f:
    for line in f:
        try:
            obj = json.loads(line)
            if obj.get('type') == 'human':
                msg = obj.get('message', {}).get('content', '')
                if isinstance(msg, list):
                    for c in msg:
                        if isinstance(c, dict) and c.get('type') == 'text':
                            t = c['text'].strip()
                            if t and not t.startswith('<'): print(t[:500])
                elif isinstance(msg, str) and msg.strip() and not msg.startswith('<'):
                    print(msg[:500])
        except: pass
```

### Source B: Conductor app database

3. Query the Conductor SQLite database for yesterday's sessions:

```bash
DB="$HOME/Library/Application Support/com.conductor.app/conductor.db"
sqlite3 "$DB" "
  SELECT s.title, w.directory_name, sm.role, sm.content, sm.created_at
  FROM session_messages sm
  JOIN sessions s ON sm.session_id = s.id
  LEFT JOIN workspaces w ON s.workspace_id = w.id
  WHERE date(sm.created_at) = 'YYYY-MM-DD'
    AND sm.role = 'user'
  ORDER BY sm.created_at
"
```

- Group by workspace (maps to project)
- Extract user prompts from `content` column (JSON format)
- Conductor sessions have titles and workspace context for richer summaries

### Save results

4. Save to `sessions/YYYY-MM-DD-ai-sessions.md` with:
   - Time spent per project (created->modified timestamps, session count, total size)
   - Insights and learnings from the top sessions
   - Full path to every raw transcript (JSONL paths for Claude Code sessions)
   - Conductor session titles and workspace names for Conductor sessions

## Output

The file path of the saved AI sessions file, or a note that it was skipped.
