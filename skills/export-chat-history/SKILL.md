---
name: export-chat-history
description: Export chat history from Cursor or Claude Code sessions. Extracts conversations from agent-transcripts (Cursor) or JSONL session files (Claude Code). Use when the user asks to export, backup, save, or review chat history.
---

# Export Chat History

Supports two sources: **Cursor** (agent-transcripts) and **Claude Code** (JSONL sessions).

## Source: Cursor

### Storage Locations

| Data             | Location                                                                        |
| ---------------- | ------------------------------------------------------------------------------- |
| Session metadata | `~/Library/Application Support/Cursor/User/workspaceStorage/{hash}/state.vscdb` |
| Full transcripts | `~/.cursor/projects/{project-name}/agent-transcripts/*.txt`                     |

### Export Workflow

1. **Find project folder** in `~/.cursor/projects/`
2. **Copy transcripts** to target directory with formatted names
3. **Add metadata** (date, source file) to each export

### Manual Steps

```bash
ls ~/.cursor/projects/ | grep "project-name"
# Then copy and format transcripts from agent-transcripts/ folder
```

### File Format

- User queries (`<user_query>` blocks)
- AI thinking (`[Thinking]` blocks)
- Tool calls and results
- Full AI responses

## Source: Claude Code

### Storage Locations

| Data             | Location                                                            |
| ---------------- | ------------------------------------------------------------------- |
| Session files    | `~/.claude/projects/{project-path-with-dashes}/*.jsonl`             |
| Conductor        | `~/.claude/projects/-Users-{user}-conductor-workspaces-*/*.jsonl`   |

The project path is the absolute path with `/` replaced by `-` (e.g., `/Users/me/Projects/foo` becomes `-Users-me-Projects-foo`).

### JSONL Structure

Each line is a JSON object with a `type` field:

| Type                   | Description                              |
| ---------------------- | ---------------------------------------- |
| `permission-mode`      | Session config (permissionMode, sessionId)|
| `system`               | System prompts (CLAUDE.md, etc.)         |
| `user`                 | User messages                            |
| `assistant`            | Claude responses (text, tool_use)        |
| `attachment`           | File attachments                         |
| `file-history-snapshot`| File state snapshots                     |

### Listing Sessions

```bash
# List recent sessions for a project, sorted by modification time
ls -lt ~/.claude/projects/-Users-me-Projects-foo/*.jsonl | head -20
```

### Extracting Session Summaries

```python
import json, os, glob, datetime

dir_path = os.path.expanduser("~/.claude/projects/{project-dir}/")
files = sorted(glob.glob(dir_path + "*.jsonl"), key=os.path.getmtime, reverse=True)

for f in files[:20]:
    dt = datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M")
    size = os.path.getsize(f)
    size_h = f"{size/1024:.0f}K" if size < 1048576 else f"{size/1048576:.1f}M"

    first_msg = "(empty)"
    with open(f) as fh:
        for line in fh:
            try:
                obj = json.loads(line)
                if obj.get("type") == "user":
                    content = obj["message"].get("content", "")
                    text = ""
                    if isinstance(content, str):
                        text = content.strip()
                    elif isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                t = item["text"].strip()
                                if not t.startswith("<system-reminder>") and len(t) > 5:
                                    text = t
                                    break
                    if text and not text.startswith("<system-reminder>") and len(text) > 5:
                        first_msg = text[:140]
                        break
            except:
                pass

    print(f"{dt} | {size_h:>6} | {first_msg}")
```

### Exporting a Single Session

```python
import json

with open("session.jsonl") as f:
    for line in f:
        obj = json.loads(line)
        if obj["type"] == "user":
            content = obj["message"].get("content", "")
            if isinstance(content, str):
                print(f"\n## User\n{content}\n")
            elif isinstance(content, list):
                for item in content:
                    if item.get("type") == "text" and not item["text"].startswith("<system-reminder>"):
                        print(f"\n## User\n{item['text']}\n")
        elif obj["type"] == "assistant":
            content = obj["message"].get("content", "")
            if isinstance(content, str):
                print(f"\n## Assistant\n{content}\n")
            elif isinstance(content, list):
                for item in content:
                    if item.get("type") == "text":
                        print(item["text"])
                    elif item.get("type") == "tool_use":
                        print(f"\n[Tool: {item['name']}]\n")
```

## Output Naming

Format: `YYYY-MM-DD-HHMM-{first-query-summary}.md`

Example: `2026-02-01-1503-website-new-project-under-projectsasere.md`
