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

```bash
# List recent sessions with date, size, and first user message
for f in $(ls -t ~/.claude/projects/{project-dir}/*.jsonl | head -20); do
  date=$(stat -f '%Sm' -t '%Y-%m-%d %H:%M' "$f")
  size=$(du -h "$f" | cut -f1)
  msg=$(jq -r 'select(.type == "user") | .message.content | if type == "string" then . elif type == "array" then map(select(.type == "text") | .text | select(startswith("<system-reminder>") | not) | select(length > 5)) | first // empty else empty end' "$f" 2>/dev/null | head -1 | cut -c1-140)
  echo "$date | $size | ${msg:-(empty)}"
done
```

### Exporting a Single Session

```bash
# Export user/assistant turns as readable markdown
jq -r '
  if .type == "user" then
    .message.content |
    if type == "string" then "\n## User\n" + . + "\n"
    elif type == "array" then
      map(select(.type == "text") | .text | select(startswith("<system-reminder>") | not)) | join("\n") | if . != "" then "\n## User\n" + . + "\n" else empty end
    else empty end
  elif .type == "assistant" then
    .message.content |
    if type == "string" then "\n## Assistant\n" + . + "\n"
    elif type == "array" then
      map(if .type == "text" then .text elif .type == "tool_use" then "\n[Tool: " + .name + "]\n" else empty end) | join("\n") | "\n## Assistant\n" + . + "\n"
    else empty end
  else empty end
' session.jsonl
```

### Quick Searches

```bash
# Find sessions mentioning a topic
grep -l '"content":".*deploy' ~/.claude/projects/{project-dir}/*.jsonl

# Count user messages in a session
jq -r 'select(.type == "user")' session.jsonl | wc -l

# List all tool calls in a session
jq -r 'select(.type == "assistant") | .message.content | arrays | .[] | select(.type == "tool_use") | .name' session.jsonl | sort | uniq -c | sort -rn
```

## Output Naming

Format: `YYYY-MM-DD-HHMM-{first-query-summary}.md`

Example: `2026-02-01-1503-website-new-project-under-projectsasere.md`
