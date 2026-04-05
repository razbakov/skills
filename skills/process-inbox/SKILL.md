---
description: "Collect Telegram saved messages + process Notion 'To do' cards + process 'To share' cards. Full GTD + S3 pipeline: Telegram export → classify → S3 analysis → Notion cards → dispatch agents. Plus: draft social content for 'To share' cards → create posting tasks → move to Done."
user_invocable: true
---

# Process Inbox

Full GTD + S3 pipeline: collect from Telegram, classify, apply S3 Tension → Driver → Requirement analysis to Action items and clusters, create Notion cards, dispatch agents for "To do" items. Runs on any schedule — on demand, every 5 minutes, hourly, or as part of daily review.

## Trigger
- `/process-inbox`, "process inbox", "run inbox"
- Can be invoked from `/daily-review` as a child skill
- Can run on a loop via `/loop 5m /process-inbox`

## Inputs
- **Working directory:** `~/Projects/ikigai`
- **Control Center DB:** `32b9a1fd-a351-8064-9375-dc9a8f839d7a`
- **Control Center data source:** `collection://32b9a1fd-a351-809d-bd4d-000b0d579048`
- **Reading Inbox data source:** `40473b3d-377c-4ddf-b7c4-9407bfc65f72`

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

### Phase 1: Collect from Telegram

#### Step 1: Export new saved messages

```bash
tdl chat export --all --with-content -T time -i $(date -v-2d +%s),$(date +%s) -o /tmp/tdl-saved.json
```

#### Step 2: Filter out already-processed messages

Load state from `inbox/.telegram-reactions.json`. Skip any message IDs already in state (they have reactions = already processed).

#### Step 3: Parse and classify each new message

For each unprocessed message, determine:
- **GTD Type** — Action, Content Idea, Reference, Someday, Rule
- **Project** — infer from content keywords
- **Priority** — 🔴 High (deadline/blocking), 🟡 Medium (important), 🟢 Low (nice-to-have)
- **Effort** — S (<1h), M (1-4h), L (4h+)

**Important rules:**
- Voice notes and reflections are **Content Ideas**, never Reference
- A single message may contain **multiple tasks** — split into separate cards
- "I want you to..." is a direct Action for Claude, not a Content Idea

**S3 Deep Analysis (all Control Center cards):**

For **every** item that will become a Control Center card, apply S3 Tension → Driver → Requirement:

1. **Tension**: What dissonance do you feel? What's the gap between current state and desired state? (1-2 sentences, subjective)
2. **Driver** (3-part):
   - *Conditions* — observable facts about what's happening (no evaluation)
   - *Effect* — consequences of those conditions
   - *Relevance* — why it matters for the mission/OKRs
3. **Requirement**: "[who] needs [conditions] so that [outcomes]" (1 sentence, future-oriented)
4. **Response Options**: 2-3 concrete options as checkboxes, including at least one defer/skip option

#### Step 3.5: Detect Clusters

After classification, scan all items for shared tensions:
- Group items pointing to the same underlying concern (same problem area, not just same project)
- Cluster criteria: **2+ items sharing a common tension**
- For clusters of Reference items with a hidden tension: upgrade to Action-level
- Apply S3 analysis once per cluster (not per item)

#### Step 4: React 👀 to all exported messages

```bash
cd ~/.config/telegram && uvx --python python3 --from telethon python3 react.py --mark-seen "<timestamps>"
```

#### Step 5: Create Notion cards in Control Center

For each classified item, create a Notion page:

```
notion-create-pages(
  parent: { data_source_id: "32b9a1fd-a351-809d-bd4d-000b0d579048" },
  pages: [{
    properties: {
      "Name": "<title>",
      "Status": "To do",
      "Project": "<project>",
      "GTD Type": "<gtd_type>",
      "Priority": "<priority>",
      "Source": "Telegram",
      "Telegram ID": <message_id>,
      "Effort": "<effort>"
    },
    content: "<S3 content for Action items, plain source text for others — see below>",
    icon: "<emoji>"
  }]
)
```

**Multi-task messages:** If one message has multiple actions, create separate cards for each. All cards share the same Telegram ID.

**S3 content for all Control Center cards:** Every card gets S3 analysis as page content:

```
**Source:** Telegram Saved Message #<id> (<date>)

<message text>

---

## S3 Analysis

### Tension
[1-2 sentences — what dissonance prompted this]

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
```

**For clustered items:** Add a cluster callout at the top of each card in the cluster:
```
> **Cluster: [Name]** — related cards: [list sibling item names]
```

**For non-Action items:** Use plain content: `"**Source:** Telegram Saved Message #<id> (<date>)\n\n<message text>"`

#### Step 6: Add reading items to Notion Reading Inbox

For messages with URLs classified as Reference/Action-read/Content Idea:

```
notion-create-pages(
  parent: { data_source_id: "40473b3d-377c-4ddf-b7c4-9407bfc65f72" },
  pages: [{
    properties: {
      "Name": "<title>",
      "Status": "To Read",
      "Source": "Telegram",
      "Type": "<Tool|Article|Thread|Video|Reference|Repo>",
      "Summary": "<1-2 sentences>",
      "Why It Matters": "<Driver summary — 1 sentence connecting to mission/OKRs>",
      "Project": "<project names JSON array>",
      "Worth Reading": "<Yes|Skim|Maybe>",
      "userDefined:URL": "<url>",
      "date:Date Added:start": "<YYYY-MM-DD>",
      "date:Date Added:is_datetime": 0
    }
  }]
)
```

#### Step 7: Save inbox file

Save to `inbox/YYYY-MM-DD-HH-MM.md`:
- `## Raw` — exact messages with `--- YYYY-MM-DD HH:MM (ID: XXXXX) ---` markers
- `## Processed` — GTD summary with section headers (Actions, Content Ideas, References, etc.)
- Each item must include `- **IDs:** <message_id>` for reaction matching

#### Step 8: React with GTD emojis

```bash
cd ~/.config/telegram && uvx --python python3 --from telethon python3 react.py --file ~/Projects/ikigai/inbox/YYYY-MM-DD-HH-MM.md
```

### Phase 2: Process Notion "To do" cards

#### Step 9: Fetch all "To do" cards from Control Center

```
notion-search(query: " ", data_source_url: "collection://32b9a1fd-a351-809d-bd4d-000b0d579048", page_size: 25)
```

Fetch each page, filter for `Status == "To do"`.

#### Step 10: Dispatch agents (priority order)

Sort by Priority (🔴 first). For each "To do" card:

```
Skill(name: "inbox", prompt: "/notion-execute-task: Execute Notion card '<title>' (page_id: <id>, url: <url>). Read the card content, do the work described, document results back on the page, and set status to 'To review'. If the task produces markdown files, upload them to Notion and link the URLs in the results. After completing, react to Telegram message <telegram_id> with GTD emoji <emoji>.")
```

Include Telegram reaction instructions if the card has a Telegram ID.

#### Step 11: Report

```
## Telegram Inbox
- Exported: <N> new messages
- Created: <N> Notion cards
- Reading items: <N> added to Reading Inbox

## Notion Processing
| Card | Project | Priority | GTD Type | Status |
|------|---------|----------|----------|--------|
| <title> | <project> | <priority> | <type> | dispatched / no new items |
```

### Phase 3: Process "To share" cards

Alex manually moves cards from "To review" → "To share" when he decides they have shareable output. This phase picks up those cards, creates posting tasks, and moves the original card to "Done".

#### Step 12: Fetch all "To share" cards

```
notion-search(query: " ", data_source_url: "collection://32b9a1fd-a351-809d-bd4d-000b0d579048", page_size: 25)
```

Filter for `Status == "To share"`. Fetch each page to read content.

#### Step 13: For each "To share" card, draft social content

Check existing materials before drafting:
- `marketing/` folder for existing campaign plans
- `engineering/razbakov.com/content/blog/` for published posts
- GitHub repos for live URLs (via `gh pr view`)

If the card doesn't already have a `## To Share` section, append one with:

**What:** One paragraph — what was built/written/created. Include live URLs.

**Why:** Why worth sharing — how it positions Alex, which content pillar it supports (AI-Augmented Dev 40%, Building in Public 30%, Fullstack 20%, Life Design 10%).

**How:** Checklist of sharing actions.

Then draft ready-to-post content directly in the card:

**X Thread:** 4-7 tweets. Hook tweet (personal/surprising/contrarian) → story → CTA with link + engagement question.

**LinkedIn:** 150-250 words. Personal story format, end with question.

#### Step 14: Create posting tasks

For each "To share" card, create separate "To do" cards:

```
notion-create-pages(
  parent: { data_source_id: "32b9a1fd-a351-809d-bd4d-000b0d579048" },
  pages: [{
    properties: {
      "Name": "Post \"<card name>\" on X + LinkedIn",
      "Status": "To do",
      "GTD Type": "Action",
      "Priority": "🟡 Medium",
      "Project": "razbakov.com",
      "Effort": "S",
      "Source": "Manual"
    },
    content: "<instructions with link to drafts in parent card>"
  }]
)
```

If video/GIF recording is needed, create a separate task for that.

#### Step 15: Move processed cards to "Done"

After posting tasks are created, move the original "To share" card to "Done":

```
notion-update-page(page_id: "<id>", command: "update_properties", properties: {"Status": "Done"})
```

## Key Rules
- **Idempotent** — safe to run multiple times. State file prevents double-processing.
- **Phase 1 can run alone** — if no new Telegram messages, skip to Phase 2.
- **Phase 2 can run alone** — processes any "To do" cards regardless of source.
- **Multi-task splitting** — one Telegram message can produce multiple Notion cards.
- **Always set all properties** — Project, GTD Type, Priority, Source, Effort, Telegram ID.
- **Voice notes = Content Ideas** — never classify as Reference.
- **"Need input" is last resort** — agents should be autonomous, only ask when genuinely blocked.
- **Markdown results → Notion** — agent output files must be uploaded to Notion and linked.
- **React on Telegram** — 👀 on export, GTD emoji after classification, PR link after work completes.

## Information Flow
```
Telegram Saved Messages
  → 👀 (seen/exported)
  → GTD classify → S3 analysis (Action/Cluster only)
  → inbox/YYYY-MM-DD-HH-MM.md (raw + processed + S3)
  → Notion Control Center card (To do, with S3 page content for Actions)
  → Notion Reading Inbox card (with S3 page content for Actions)
  → Agent dispatched via /inbox
  → Agent sets "In progress" → does work → sets "To review"
  → GTD emoji on Telegram (replaces 👀)
  → PR link appended to Telegram message
  → Markdown results uploaded to Notion

"To share" cards (manually set by Alex from "To review")
  → Draft social content (X thread + LinkedIn) on the card
  → Create "Post on X + LinkedIn" task cards (To do, S effort)
  → Move original card to Done
```
