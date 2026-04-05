# Execute Task from Notion Board

## Trigger
When the user points at a Notion board card and says "do it", "execute this", "work on this", or similar. Also when referencing a task by name from a known Notion database.

## Inputs
1. **Notion page/card** — the task to execute (required)
2. **Database** — the Notion database it belongs to (required, can be inferred from context)

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

### Step 1: Read the task
Fetch the Notion page to understand:
- What needs to be done (page content, linked references)
- Current status and all properties (Project, Priority, GTD Type, etc.)
- Any linked research or context pages (follow `<mention-page>` links)
- **S3 Analysis** — if the page contains a `## S3 Analysis` section, read the Tension, Driver, and Requirement. Use the Requirement to scope your work — it defines what "done" looks like. Use Response Options as guidance for which approach to take (pick the most appropriate one). **If S3 Analysis is missing, add it before starting work** (see Step 1.5).
- **Comments and discussions** — these contain review feedback from previous iterations

```
notion-fetch(page_id, include_discussions: true)
notion-get-comments(page_id, include_all_blocks: true)
```

If comments exist, treat them as additional requirements or corrections that must be addressed in this execution.

### Step 1.5: Add S3 Analysis if missing

If the page does NOT contain a `## S3 Analysis` section, generate and add one before proceeding:

```
notion-update-page(page_id, command: "update_content", content_updates: [{
  old_str: "<end of existing content>",
  new_str: "<existing content>\n\n---\n\n## S3 Analysis\n\n### Tension\n[1-2 sentences]\n\n### Driver\n| Conditions | Effect | Relevance |\n|------------|--------|----------|\n| [facts] | [consequences] | [why it matters] |\n\n### Requirement\n> [who] needs [conditions] so that [outcomes]\n\n### Response Options\n- [ ] [option A]\n- [ ] [option B]\n- [ ] [defer/skip]"
}])
```

Use the card title, content, project, and GTD type to infer appropriate Tension, Driver, and Requirement. Connect the Relevance to the mission/OKRs.

### Step 2: Set status to "In progress"
```
notion-update-page(page_id, command: "update_properties", properties: { "Status": "In progress" })
```

### Step 3: Fill missing properties
If any properties are empty, infer and set them:
- **Project** — infer from content keywords or file paths
- **GTD Type** — classify the task type
- **Priority** — assess urgency/importance
- **Effort** — estimate S/M/L
- **Source** — set if known (check for Telegram ID)

```
notion-update-page(page_id, command: "update_properties", properties: { ... })
```

### Step 4: Execute the work
Do whatever the card describes. This varies — could be:
- Scaffolding a project
- Writing code
- Running a research task
- Creating a document

Track progress with TaskCreate/TaskUpdate during execution.

**Autonomy-first principle:** Agents should be as autonomous as possible. Make decisions, pick reasonable defaults, and keep moving. Only use "Need input" when genuinely blocked — when the task requires a decision that could go fundamentally different directions and guessing wrong would waste significant effort.

**When to set "Need input":**
- The task requires choosing between mutually exclusive strategies (e.g., "rebrand vs keep name")
- Missing critical information that can't be inferred (e.g., pricing, legal constraints, credentials)
- The task explicitly asks for user preference on something subjective

**When NOT to set "Need input":**
- You can make a reasonable default choice and document it
- The question is about implementation details — just pick the better option
- You're unsure but can present options in the result for review

When setting "Need input", add a `## Questions` section to the Notion page listing specific, answerable questions. Don't ask vague questions — be concrete about what you need to proceed.

### Step 5: Upload markdown results to Notion
If the task produced markdown files (research, blog posts, plans, etc.):
1. For each markdown file created, upload it as a Notion page under the Control Center
2. Link the Notion page URLs back in the result section of the card
3. Set appropriate properties on the new pages (Project, GTD Type, Source: "Agent")

### Step 6: Document results on the Notion page
Append a `## Result` section to the card with:
- What was built/done
- Where to find it (repo path, URL, file path)
- **Notion page links** for any uploaded markdown files
- How to run/use it (commands, instructions)
- Architecture overview (if code)
- Next steps (checklist of what remains)

```
notion-update-page(page_id, command: "update_content", content_updates: [{
  old_str: "<end of existing content>",
  new_str: "<existing content>\n\n---\n\n## Result\n\n..."
}])
```

### Step 7: React to Telegram message (if applicable)
If the card has a Telegram ID, react with the GTD emoji:
- Action → 👍, Content Idea → ✍, Reference → 👌, Someday → 🤔, Rule → 🫡, Done → 🏆

```bash
cd ~/.config/telegram && uvx --python python3 --from telethon python3 -c "
import asyncio,json,os;from pathlib import Path;from telethon import TelegramClient;from telethon.tl.functions.messages import SendReactionRequest;from telethon.tl.types import ReactionEmoji
async def m():
    c=TelegramClient(str(Path.home()/'.config/telegram/session'),int(os.environ['TELEGRAM_API_ID']),os.environ['TELEGRAM_API_HASH']);await c.start();me=await c.get_me()
    await c(SendReactionRequest(peer=me.id,msg_id=<TELEGRAM_ID>,reaction=[ReactionEmoji(emoticon='<EMOJI>')]))
    s=json.loads((Path.home()/'Projects/ikigai/inbox/.telegram-reactions.json').read_text());s['<TELEGRAM_ID>']='<EMOJI>'
    (Path.home()/'Projects/ikigai/inbox/.telegram-reactions.json').write_text(json.dumps(s,indent=2)+chr(10));await c.disconnect()
asyncio.run(m())
"
```

### Step 8: Check for unresolved discussions (Notion + GitHub)
Before moving to "To review", verify there are no unresolved threads — on Notion OR GitHub:

**8a. Check Notion discussions:**
```
notion-get-comments(page_id, include_all_blocks: true)
```

**8b. Check GitHub PR reviews (if work produced a PR):**
```bash
gh pr view <PR_NUMBER> --json reviewThreads --jq '.reviewThreads[] | select(.isResolved == false)'
```

If there are **unresolved threads** on either platform:
1. Read each unresolved thread carefully
2. Address the feedback in your work (fix code, update content, etc.)
3. Reply to each thread explaining what was done
4. Resolve the thread (on GitHub: push fix + reply; on Notion: reply to discussion)
5. Only proceed to set "To review" after ALL threads on ALL platforms are resolved

**Do NOT set "To review" if any discussion thread remains unresolved — Notion or GitHub.** The user should never receive a "To review" task with open feedback — that means the agent didn't finish the job.

### Step 9: Set status to "To review"
The work is done and all discussions are resolved. Needs human review before marking complete. Never set to "Done" — that's the user's call after review.

```
notion-update-page(page_id, command: "update_properties", properties: { "Status": "To review" })
```

## Key Rules
- **Never mark "Done"** — always "To review". The user decides when it's done.
- **"Need input" is a last resort** — be autonomous. Make reasonable decisions and document them. Only set "Need input" when genuinely blocked by a decision that requires human judgment. When you do, write specific questions in a `## Questions` section on the page.
- **Always document results** on the Notion page itself, not just locally.
- **Always read comments** — comments contain review feedback that must be addressed.
- **Use S3 context** — if the card has an S3 Analysis section, the Requirement defines scope and the Driver explains why it matters. Pick from Response Options when available.
- **Follow linked pages** — if the card references research or specs, read them first.
- **Commit work** — if code was written, commit it with a descriptive message.
- **Upload markdown to Notion** — any markdown files produced must be uploaded as Notion pages and linked in results.
- **Set all properties** — fill in any missing Project, GTD Type, Priority, Effort, Source.
- **React on Telegram** — if card has a Telegram ID, react with the appropriate GTD emoji.
- **Split multi-task cards** — if a card contains multiple distinct tasks, create separate child cards for each.
