---
name: export-chat-history
description: Export and share AI chat sessions from Claude Code, Cursor, or Conductor. Lists sessions across providers, exports to markdown, publishes as a GitHub Gist. Use when the user asks to export, share, backup, or review chat history.
---

# Export Chat History

Three-step workflow: **discover** sessions across providers, **select** one, **export** and share via GitHub Gist.

Prerequisites: `jq`, `gh` (GitHub CLI, authenticated).

## Step 1: Discover Sessions

Detect which providers have session data on this machine, then list recent sessions from all of them.

### Provider Detection

```bash
# Check which providers exist
[ -d ~/.claude/projects ] && echo "claude-code"
[ -d ~/.cursor/projects ] && echo "cursor"
ls ~/.claude/projects/ 2>/dev/null | grep -q "conductor-workspaces" && echo "conductor"
```

### Claude Code Sessions

Stored as JSONL at `~/.claude/projects/{project-path-with-dashes}/*.jsonl`.
Path mapping: `/Users/me/Projects/foo` becomes `-Users-me-Projects-foo`.

```bash
# List all project directories
ls ~/.claude/projects/ | grep -v conductor

# List recent sessions for a project with summaries
i=1; for f in $(ls -t ~/.claude/projects/{project-dir}/*.jsonl | head -20); do
  dt=$(stat -f '%Sm' -t '%Y-%m-%d %H:%M' "$f" 2>/dev/null || date -r "$f" '+%Y-%m-%d %H:%M')
  size=$(du -h "$f" | cut -f1)
  msg=$(jq -r 'select(.type == "user") | .message.content | if type == "string" then . elif type == "array" then map(select(.type == "text") | .text | select(startswith("<system-reminder>") | not) | select(length > 5)) | first // empty else empty end' "$f" 2>/dev/null | head -1 | cut -c1-120)
  printf "%3d) %s | %5s | %s\n" "$i" "$dt" "$size" "${msg:-(automated/system)}"
  i=$((i + 1))
done
```

JSONL line types: `user` (user messages), `assistant` (Claude responses with text/tool_use), `system`, `attachment`, `permission-mode`, `file-history-snapshot`.

### Conductor Sessions

Same JSONL format, stored at `~/.claude/projects/-Users-{user}-conductor-workspaces-*/*.jsonl`. Use the same listing command with the conductor project directory.

### Cursor Sessions

Stored as plain text at `~/.cursor/projects/{project-name}/agent-transcripts/*.txt`.

```bash
# List recent Cursor transcripts
i=1; for f in $(ls -t ~/.cursor/projects/{project-name}/agent-transcripts/*.txt | head -20); do
  dt=$(stat -f '%Sm' -t '%Y-%m-%d %H:%M' "$f" 2>/dev/null || date -r "$f" '+%Y-%m-%d %H:%M')
  size=$(du -h "$f" | cut -f1)
  msg=$(grep -m1 '<user_query>' "$f" | sed 's/<[^>]*>//g' | cut -c1-120)
  printf "%3d) %s | %5s | %s\n" "$i" "$dt" "$size" "${msg:-(empty)}"
  i=$((i + 1))
done
```

## Step 2: Select Session

Present the numbered list from Step 1 to the user. Ask them to pick a number. Map the number back to the file path.

If the user provides a search term instead of a number:
```bash
# Search across sessions by keyword
grep -rl 'search-term' ~/.claude/projects/{project-dir}/*.jsonl
```

## Step 3: Export and Share

### Export Claude Code / Conductor Session to Markdown

```bash
jq -r '
  if .type == "user" then
    .message.content |
    if type == "string" then "\n## User\n" + . + "\n"
    elif type == "array" then
      map(select(.type == "text") | .text | select(startswith("<system-reminder>") | not)) | join("\n") |
      if . != "" then "\n## User\n" + . + "\n" else empty end
    else empty end
  elif .type == "assistant" then
    .message.content |
    if type == "string" then "\n## Assistant\n" + . + "\n"
    elif type == "array" then
      map(if .type == "text" then .text elif .type == "tool_use" then "\n[Tool: " + .name + "]\n" else empty end) |
      join("\n") | "\n## Assistant\n" + . + "\n"
    else empty end
  else empty end
' "$SESSION_FILE" > /tmp/session-export.md
```

### Export Cursor Session to Markdown

```bash
# Cursor transcripts are already readable text, just add a header
echo "# Cursor Session Export" > /tmp/session-export.md
echo "" >> /tmp/session-export.md
cat "$SESSION_FILE" >> /tmp/session-export.md
```

### Add Metadata Header

Prepend session metadata to the export:

```bash
dt=$(stat -f '%Sm' -t '%Y-%m-%d %H:%M' "$SESSION_FILE" 2>/dev/null || date -r "$SESSION_FILE" '+%Y-%m-%d %H:%M')
msgs=$(jq -r 'select(.type == "user")' "$SESSION_FILE" 2>/dev/null | wc -l | tr -d ' ')
tools=$(jq -r 'select(.type == "assistant") | .message.content | arrays | .[] | select(.type == "tool_use") | .name' "$SESSION_FILE" 2>/dev/null | sort | uniq -c | sort -rn | head -5)

header="# Session Export\n\n- **Date:** $dt\n- **Source:** {provider}\n- **Messages:** $msgs user turns\n- **Top tools:** \n\`\`\`\n$tools\n\`\`\`\n\n---\n"
echo -e "$header" | cat - /tmp/session-export.md > /tmp/session-final.md
mv /tmp/session-final.md /tmp/session-export.md
```

### Publish to GitHub Gist

```bash
gh gist create /tmp/session-export.md --desc "AI session export ($(date +%Y-%m-%d))" --public
```

The command outputs the gist URL. Share that URL.

For private gists (default):
```bash
gh gist create /tmp/session-export.md --desc "AI session export ($(date +%Y-%m-%d))"
```

## Quick Reference

```bash
# Count user messages in a session
jq -r 'select(.type == "user")' session.jsonl | wc -l

# List all tool calls in a session
jq -r 'select(.type == "assistant") | .message.content | arrays | .[] | select(.type == "tool_use") | .name' session.jsonl | sort | uniq -c | sort -rn

# Find sessions mentioning a topic
grep -rl 'deploy' ~/.claude/projects/{project-dir}/*.jsonl
```
