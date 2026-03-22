---
description: Export Telegram saved messages via tdl, apply GTD clarify, update project docs with actionable items. Part of the daily review workflow.
user_invocable: true
---

# Daily Review — Telegram Inbox (GTD Collect + Clarify)

Telegram Saved Messages are the GTD inbox — voice notes, ideas, links, reminders captured throughout the day. This step collects, saves raw, and processes them into actionable items.

## Trigger

Invoked as part of `/daily-review` or independently via `/daily-review-telegram-inbox`.

## Context

- **Working directory:** `~/Projects/ikigai`
- **Session storage:** `sessions/`
- **Projects directory:** `~/Projects/`
- **Requirement:** `tdl` CLI installed and authenticated
- **Date:** Use yesterday's date for export range

## Process

### 1. Export saved messages

Export since last daily review:

```bash
tdl chat export --all --with-content -T time -i $(date -v-1d +%s),$(date +%s) -o /tmp/tdl-saved.json
```

### 2. React 👀 to exported messages (mark as "seen")

After export, immediately mark all exported messages with 👀 in Telegram. This tells the user which messages have been picked up for processing.

```bash
# Extract timestamps from exported messages
TIMESTAMPS=$(cat /tmp/tdl-saved.json | python3 -c "
import json, sys, datetime
data = json.load(sys.stdin)
msgs = data.get('messages', [])
ts_list = []
for m in msgs:
    ts = m.get('date', 0)
    dt = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
    ts_list.append(dt)
print(','.join(ts_list))
")

# Mark as seen in Telegram
cd ~/.config/telegram && uvx --python python3 --from telethon python3 react.py --mark-seen "$TIMESTAMPS"
```

### 3. Parse and display messages

```bash
cat /tmp/tdl-saved.json | python3 -c "
import json, sys, datetime
data = json.load(sys.stdin)
msgs = data.get('messages', [])
for m in msgs:
    ts = m.get('date', 0)
    dt = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
    text = m.get('text', '(no text)')
    print(f'--- {dt} ---')
    print(text)
    print()
"
```

### 4. Apply GTD Clarify to each message

- **Is it actionable?** If yes -> extract a task with project assignment
- **Is it reference material?** If yes -> note which project/contact it relates to
- **Is it already done?** If yes -> mark as actioned
- **Is it a someday/maybe idea?** If yes -> note it but don't create a task

**Important:** Never mark voice notes or reflections as "Reference" — they are content ideas. Classify them as Action for razbakov.com or smm-manager (blog post, thread, social media post). Every thought Alex captures is potential content.

### 5. Present summary table

```
| # | Time | Preview | GTD | Project | Task |
|---|------|---------|-----|---------|------|
| 1 | 08:05 | WeDance logo... | Action | WeDance | Integrate logo |
| 2 | 08:06 | GitHub ticket... | Action | ikigai | Publish ticket from feature file |
| 3 | 13:02 | codex in slack... | Reference | brievcase | — |
```

### 6. Update project docs (source of truth)

For each actionable item:
- Read the project's `README.md` (or `TODO.md`, `docs/backlog.yaml` if they exist)
- Add the task to the project's next steps / backlog
- This is where the task actually lives — not in the daily review file

### 7. Save to inbox file

Save to `inbox/YYYY-MM-DD-HH-MM.md` (timestamp of the first message in the batch):
- `## Raw` — exact messages, unedited
- `## Processed` — the GTD summary table
- Note which project docs were updated (traceability)

The daily review file (`sessions/YYYY-MM-DD-daily-review.md`) should only contain a link to the inbox file, not the full content.

### 8. React with GTD emojis in Telegram

After saving the inbox file, upgrade all 👀 reactions to GTD-specific emojis:

```bash
cd ~/.config/telegram && uvx --python python3 --from telethon python3 react.py --file ~/Projects/ikigai/inbox/YYYY-MM-DD-HH-MM.md
```

This replaces the 👀 "seen" reaction with:
- 👍 Action — will do
- 🏆 Done — already handled
- 🔥 Idea — captured for later
- 🤔 Someday — someday/maybe
- 🫡 Rule — rule applied
- ✍ Content Idea — content to create
- 👌 Reference — filed

### 9. Append PR links to messages (when available)

When work on an inbox item produces a PR, edit the original Telegram message to append the link:

```bash
# Single PR
cd ~/.config/telegram && uvx --python python3 --from telethon python3 react.py --add-pr '2026-03-21 08:05|https://github.com/razbakov/festival-schedule/pull/23'

# Bulk from JSON
cat > /tmp/prs.json << 'EOF'
[
  {"ts": "2026-03-21 08:05", "pr": "https://github.com/.../pull/23", "title": "Add hero image"}
]
EOF
cd ~/.config/telegram && uvx --python python3 --from telethon python3 react.py --add-pr /tmp/prs.json
```

The original message becomes:
```
We dance. We need to integrate a logo.
→ PR: Add hero image
  https://github.com/razbakov/festival-schedule/pull/23
```

**Information flow:** Telegram -> 👀 (seen) -> `inbox/` file (raw + processed) -> Project README (source of truth) -> GTD emoji in Telegram -> PR link in Telegram -> PROJECTS.md (cache) -> Daily Review (link only).

## Output

The GTD summary table and a list of project docs that were updated.
