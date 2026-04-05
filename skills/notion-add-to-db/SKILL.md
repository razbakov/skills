# Add File to Notion Database

## Trigger
When the user asks to add a local file (markdown, text, etc.) to a Notion database, e.g.:
- "add X to Notion Control Center"
- "send this file to Notion DB"
- "create a Notion page from this file in [database name]"

## Inputs
1. **File path** — local file to add (required)
2. **Database name** — Notion database to add to (default: "Control Center")
3. **Status** — property value like "To do", "To review", etc. (optional)
4. **Title override** — custom page title; defaults to file's H1 heading or filename (optional)
5. **Properties** — any additional properties to set (optional)

## Control Center Schema (Quick Reference)
Database ID: `32b9a1fd-a351-8064-9375-dc9a8f839d7a`
Data source: `collection://32b9a1fd-a351-809d-bd4d-000b0d579048`

| Property | Type | Values |
|----------|------|--------|
| Name | title | — |
| Status | status | To do, Need input, In progress, To review, Done |
| Project | select | WeDance, ikigai, razbakov.com, sdtv, smm-manager, facts-collector, montuno-club, dancegods, dancegodscompany, brievcase, voice-assistant, tasks-dashboard, call-agent, skill-mix, cv, web100, ai-study-group |
| Priority | select | 🔴 High, 🟡 Medium, 🟢 Low |
| GTD Type | select | Action, Content Idea, Reference, Someday, Rule |
| Source | select | Telegram, Manual, Daily Review, Agent, Bookmark |
| Telegram ID | number | message ID |
| Due Date | date | any |
| Effort | select | S, M, L |

## Process

### Step 1: Read the local file
Read the file to get its content. Extract the H1 heading as the default title.

### Step 2: Infer properties from content
Analyze the file content and any user-provided context to set:
- **Project** — infer from keywords, file path, or content (e.g. "dance" → WeDance, "blog" → razbakov.com, "recipe" → ikigai). Always set this.
- **GTD Type** — classify: is it an Action (something to do), Content Idea (something to write/create), Reference (info to file), Someday (nice-to-have), or Rule (behavioral rule)?
- **Priority** — 🔴 High if deadline-driven or blocking, 🟡 Medium for important but not urgent, 🟢 Low for nice-to-have
- **Source** — set based on where it came from (Telegram, Daily Review, Bookmark, Manual, Agent)
- **Effort** — S (<1h), M (1-4h), L (4h+)
- **Telegram ID** — if source is Telegram and message ID is known

### Step 3: Search Notion for the database (if not Control Center)
```
notion-search(query: "<database name>", page_size: 5, max_highlight_length: 0)
```
Find the database by name. Confirm it's `type: "database"`.
For Control Center, skip search — use the known IDs above.

### Step 4: Fetch database schema (if not Control Center)
```
notion-fetch(id: "<database_id>")
```
From the response, extract:
- **Data source ID** from `<data-source url="collection://<data_source_id>">`
- **Schema** — property names, types, and allowed values

### Step 5: Create the page
```
notion-create-pages(
  parent: { data_source_id: "<data_source_id>" },
  pages: [{
    properties: {
      "Name": "<title>",
      "Status": "<status>",
      "Project": "<project>",
      "GTD Type": "<gtd_type>",
      "Priority": "<priority>",
      "Source": "<source>",
      "Effort": "<effort>",
      "Telegram ID": <telegram_id_or_null>
    },
    content: "<file content adapted to Notion markdown>",
    icon: "<emoji>"
  }]
)
```

**Content adaptation rules:**
- Remove the H1 heading from content (it becomes the page title)
- Keep tables, bold, links, lists — Notion markdown supports them
- For very long files, include a summary version with a reference to the local file path at the bottom
- Add an icon emoji that matches the content topic

**S3 Analysis (required for Control Center):**
When adding to the Control Center database, prepend S3 analysis before the file content:

```
## S3 Analysis

### Tension
[1-2 sentences — what gap or dissonance prompted this]

### Driver
| Conditions | Effect | Relevance |
|------------|--------|-----------|
| [observable facts] | [consequences] | [why it matters for mission/OKRs] |

### Requirement
> [who] needs [conditions] so that [outcomes]

### Response Options
- [ ] [concrete action A]
- [ ] [alternative approach B]
- [ ] [defer/skip option]

---

[file content below]
```

### Step 6: Confirm
Return the Notion page URL to the user.

## Multi-task messages
A single Telegram message may contain multiple actions. When processing:
- Split into separate Notion cards — one per actionable item
- Each card references the same Telegram ID
- Each card gets its own GTD Type, Priority, and Effort

## Output
- Notion page URL(s)
- Confirmation of title, database, project, and all properties set
