# Process Notion Inbox

Fetch all "To do" cards from the Notion Control Center board and dispatch a parallel `/inbox` agent for each one. Each agent runs `/notion-execute-task` which handles execution and status updates autonomously.

## Trigger
- User says `/process-inbox-notion`, "process notion inbox", "run notion tasks", or "do all notion todos"

## Inputs
- **Database:** Control Center (ID: `32b9a1fd-a351-8064-9375-dc9a8f839d7a`, data source: `collection://32b9a1fd-a351-809d-bd4d-000b0d579048`)
- **Working directory:** `~/Projects/ikigai`

## Control Center Schema
| Property | Type | Values |
|----------|------|--------|
| Name | title | — |
| Status | status | To do, Need input, In progress, To review, To share, Done |
| Project | select | WeDance, ikigai, razbakov.com, sdtv, smm-manager, facts-collector, montuno-club, dancegods, dancegodscompany, brievcase, voice-assistant, tasks-dashboard, call-agent, skill-mix, cv, web100, ai-study-group |
| Priority | select | 🔴 High, 🟡 Medium, 🟢 Low |
| GTD Type | select | Action, Content Idea, Reference, Someday, Rule |
| Source | select | Telegram, Manual, Daily Review, Agent, Bookmark |
| Telegram ID | number | message ID |
| Due Date | date | any |
| Effort | select | S, M, L |

## Process

### Step 1: Fetch all pages from the Control Center
```
notion-search(query: " ", data_source_url: "collection://32b9a1fd-a351-809d-bd4d-000b0d579048", page_size: 25)
```

### Step 2: Filter for "To do" status
For each result, fetch the page to check its Status property:
```
notion-fetch(id: "<page_id>")
```
Collect only pages where `Status` equals "To do".

### Step 3: Dispatch agents (priority order)
Sort "To do" cards by Priority (🔴 High first, then 🟡 Medium, then 🟢 Low).

For each "To do" page, invoke the Skill tool:
```
Skill(name: "inbox", prompt: "/notion-execute-task: Execute Notion card '<page_title>' (page_id: <page_id>, url: <page_url>). Read the card content, do the work described, document results back on the page, and set status to 'To review'. If the task produces markdown files, upload them to Notion as pages and link the URLs in the results.")
```

**Telegram reaction instructions:** If the card has a Telegram ID, include in the dispatch prompt:
```
After completing, react to Telegram message <telegram_id> with the GTD emoji:
- Action → 👍, Content Idea → ✍, Reference → 👌, Someday → 🤔, Rule → 🫡, Done → 🏆
Use: cd ~/.config/telegram && uvx --python python3 --from telethon python3 -c "<reaction script>"
Also update ~/Projects/ikigai/inbox/.telegram-reactions.json
```

Dispatch ALL cards in parallel — each `/inbox` call is independent.

### Step 4: Report
List all dispatched tasks:
```
| Card | Project | Priority | GTD Type | Telegram ID | tmux Session |
|------|---------|----------|----------|-------------|-------------|
| <title> | <project> | <priority> | <type> | <id> | wf-<slug> |
```

## Key Rules
- **Always fetch and filter** — don't assume which cards are "To do", verify via API
- **One agent per card** — each card gets its own `/inbox` dispatch
- **Agents are autonomous** — each runs `/notion-execute-task` which sets "In progress" → does work → sets "To review"
- **Working directory** is always `~/Projects/ikigai` for dispatched agents
- **Markdown results → Notion** — agents must upload markdown output files to Notion and link them
- **Set all properties** — when creating cards, always set Project, GTD Type, Priority, Source, Effort
- **Telegram reactions** — if card has Telegram ID, agent must react with GTD emoji after completing
- If no "To do" cards found, report that and stop
