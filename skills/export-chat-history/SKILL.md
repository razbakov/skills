---
name: export-chat-history
description: Export Cursor chat history for the current project. Extracts full conversations including AI responses from agent-transcripts. Use when the user asks to export, backup, or save chat history.
---

# Export Chat History

## Storage Locations

Cursor stores chat data in multiple locations:

| Data             | Location                                                                        |
| ---------------- | ------------------------------------------------------------------------------- |
| Session metadata | `~/Library/Application Support/Cursor/User/workspaceStorage/{hash}/state.vscdb` |
| Full transcripts | `~/.cursor/projects/{project-name}/agent-transcripts/*.txt`                     |

## Export Workflow

1. **Find project folder** in `~/.cursor/projects/`
2. **Copy transcripts** to target directory with formatted names
3. **Add metadata** (date, source file) to each export

## Using the Export Script

```bash
python ~/.cursor/skills/export-chat-history/scripts/export.py <project-path> <output-dir>
```

Example:

```bash
python ~/.cursor/skills/export-chat-history/scripts/export.py /Users/me/Projects/myproject ./history/myproject
```

## Manual Export Steps

1. Find project folder:

   ```bash
   ls ~/.cursor/projects/ | grep "project-name"
   ```

2. Copy and format transcripts from `agent-transcripts/` folder

## File Format

Exported files contain:

- Session metadata header
- User queries (`<user_query>` blocks)
- AI thinking (`[Thinking]` blocks)
- Tool calls and results
- Full AI responses

## Output Naming

Format: `YYYY-MM-DD-HHMM-{first-query-summary}.md`

Example: `2026-02-01-1503-website-new-project-under-projectsasere.md`
