---
name: export-chat-history
description: Export and share AI chat sessions from Claude Code, Cursor, or Conductor. Lists sessions across providers, exports to markdown, publishes as a GitHub Gist. Use when the user asks to export, share, backup, or review chat history.
---

# Export Chat History

Three-step workflow: **discover** sessions across providers, **select** one, **export** and share via GitHub Gist.

Prerequisites: `jq`, `gawk`, `gh` (GitHub CLI, authenticated).

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

JSONL line types: `user` (user messages), `assistant` (Claude responses with text/tool_use), `system` (turn duration stats), `attachment`, `permission-mode`, `file-history-snapshot`.

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

Present the numbered list from Step 1 to the user. Ask them to pick a number. Map the number back to the file path. **Save the absolute file path** — do not rely on `ls -t` order later, as file modification times shift between steps.

If the user provides a search term instead of a number:
```bash
# Search across sessions by keyword
grep -rl 'search-term' ~/.claude/projects/{project-dir}/*.jsonl
```

## Step 3: Export and Share

### Export Claude Code / Conductor Session to Markdown

Two-stage pipeline: jq extracts conversation, gawk collapses consecutive tool-only turns.

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
      ( [.[] | select(.type == "text") | .text] | join("\n") ) as $text |
      ( [.[] | select(.type == "tool_use") | .name] ) as $tools |
      ( $tools | group_by(.) | map(if length > 1 then "\(.[0]) ×\(length)" else .[0] end) | join(", ") ) as $toolsummary |
      if ($text | length) > 0 and ($toolsummary | length) > 0 then
        "\n## Assistant\n" + $text + "\n\n> " + ($tools | length | tostring) + " tools: " + $toolsummary + "\n"
      elif ($text | length) > 0 then
        "\n## Assistant\n" + $text + "\n"
      elif ($toolsummary | length) > 0 then
        "\n> " + ($tools | length | tostring) + " tools: " + $toolsummary + "\n"
      else empty end
    else empty end
  else empty end
' "$SESSION_FILE" | gawk '
  /^> [0-9]+ tools:/ {
    match($0, /^> [0-9]+ tools: (.+)/, m)
    n = split(m[1], arr, ", ")
    for (i = 1; i <= n; i++) {
      if (match(arr[i], /(.+) ×([0-9]+)/, p)) {
        tools[p[1]] += p[2]
      } else {
        tools[arr[i]] += 1
      }
    }
    pending = 1
    next
  }
  /^$/ && pending { next }
  {
    if (pending) {
      total = 0; summary = ""
      for (t in tools) total += tools[t]
      PROCINFO["sorted_in"] = "@val_num_desc"
      for (t in tools) {
        if (summary != "") summary = summary ", "
        summary = summary (tools[t] > 1 ? t " ×" tools[t] : t)
      }
      print "> " total " tools: " summary
      print ""
      delete tools
      pending = 0
    }
    print
  }
  END {
    if (pending) {
      total = 0; summary = ""
      for (t in tools) total += tools[t]
      PROCINFO["sorted_in"] = "@val_num_desc"
      for (t in tools) {
        if (summary != "") summary = summary ", "
        summary = summary (tools[t] > 1 ? t " ×" tools[t] : t)
      }
      print "> " total " tools: " summary
    }
  }
' > /tmp/session-export.md
```

### Export Cursor Session to Markdown

```bash
# Cursor transcripts are already readable text, just add a header
echo "# Cursor Session Export" > /tmp/session-export.md
echo "" >> /tmp/session-export.md
cat "$SESSION_FILE" >> /tmp/session-export.md
```

### Generate Title and Description

After exporting, read `/tmp/session-export.md` and generate:
- **Title** — short (under 60 chars), descriptive summary of what the session accomplished. Not the first message verbatim. Example: "Montuno Club schedule update + promo code field"
- **Description** — one sentence summarizing the outcome. Example: "Updated class times across 8 locale files and added optional promo code to the registration form."

Use these as `{title}` and `{description}` in the header and gist description below.

### Add Metadata Header

Extract metadata from the JSONL and prepend to the export. Available fields on assistant messages: `.message.model`, `.version`, `.entrypoint`, `.cwd`, `.gitBranch`, `.slug`, `.message.usage.output_tokens`. Duration from system messages with `.subtype == "turn_duration"`.

```bash
dt=$(stat -f '%Sm' -t '%Y-%m-%d %H:%M' "$SESSION_FILE" 2>/dev/null || date -r "$SESSION_FILE" '+%Y-%m-%d %H:%M')
msgs=$(jq -r 'select(.type == "user")' "$SESSION_FILE" 2>/dev/null | wc -l | tr -d ' ')
asst_msgs=$(jq -r 'select(.type == "assistant")' "$SESSION_FILE" 2>/dev/null | wc -l | tr -d ' ')
tools=$(jq -r 'select(.type == "assistant") | .message.content | arrays | .[] | select(.type == "tool_use") | .name' "$SESSION_FILE" 2>/dev/null | sort | uniq -c | sort -rn | head -5)
model=$(jq -r 'select(.type == "assistant") | .message.model // empty' "$SESSION_FILE" | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
version=$(jq -r 'select(.type == "assistant") | .version // empty' "$SESSION_FILE" | sort -u | tail -1)
entrypoint=$(jq -r 'select(.type == "assistant") | .entrypoint // empty' "$SESSION_FILE" | sort -u | head -1)
cwd=$(jq -r 'select(.type == "assistant") | .cwd // empty' "$SESSION_FILE" | sort -u | head -1)
branch=$(jq -r 'select(.type == "assistant") | .gitBranch // empty' "$SESSION_FILE" | sort -u | head -1)
output_tokens=$(jq -r 'select(.type == "assistant") | .message.usage.output_tokens // 0' "$SESSION_FILE" | paste -sd+ - | bc)
total_duration=$(jq -r 'select(.type == "system" and .subtype == "turn_duration") | .durationMs // 0' "$SESSION_FILE" | paste -sd+ - | bc 2>/dev/null || echo 0)
duration_min=$(echo "scale=1; ${total_duration:-0} / 60000" | bc 2>/dev/null || echo "?")

cat <<HEADER > /tmp/session-header.md
# {title}

> {description}

| | |
|---|---|
| **Date** | $dt |
| **Model** | $model |
| **Harness** | Claude Code $version ($entrypoint) |
| **OS** | $(uname -s) $(uname -m) |
| **Project** | $cwd ($branch) |
| **Turns** | $msgs user · $asst_msgs assistant |
| **Output** | $output_tokens tokens |
| **Duration** | ${duration_min}m |
| **Top tools** | $(echo "$tools" | awk '{printf "%s ×%s, ", $2, $1}' | sed 's/, $//') |

---
HEADER
cat /tmp/session-header.md /tmp/session-export.md > /tmp/session-final.md
mv /tmp/session-final.md /tmp/session-export.md
```

### Publish to GitHub Gist

Always create a private gist without asking. Share the URL with the user.

```bash
gh gist create /tmp/session-export.md --desc "{title}"
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
