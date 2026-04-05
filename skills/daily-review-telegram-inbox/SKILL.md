---
description: Export Telegram saved messages via tdl, apply GTD + S3 clarify, update project docs with actionable items. Part of the daily review workflow.
user_invocable: true
---

# Daily Review — Telegram Inbox (GTD + S3 Collect + Clarify)

Telegram Saved Messages are the GTD inbox — voice notes, ideas, links, reminders captured throughout the day. This step collects, saves raw, and processes them into actionable items. Action items and clusters get deeper analysis using Sociocracy 3.0's Tension → Driver → Requirement pattern.

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

**S3 Deep Analysis (Action items and Clusters only):**

For each item classified as **Action**, apply S3 Tension → Driver → Requirement:

1. **Tension**: What dissonance do you feel? What's the gap between current state and desired state? (1-2 sentences, subjective)
2. **Driver** (3-part):
   - *Conditions* — observable facts about what's happening (no evaluation)
   - *Effect* — consequences of those conditions
   - *Relevance* — why it matters for the mission/OKRs
3. **Requirement**: "[who] needs [conditions] so that [outcomes]" (1 sentence, future-oriented)
4. **Response Options**: 2-3 concrete options as checkboxes, including at least one defer/skip option

For Reference, Trash, Someday, Content Ideas that are NOT part of a cluster: skip S3 analysis. GTD classification is sufficient.

### 4.5. Detect Clusters

After GTD classification, scan all items for shared tensions:

1. Group items that point to the same underlying concern:
   - Same problem area (not just same project tag)
   - Multiple tools/articles addressing the same gap
   - Related voice notes forming a single brainstorm
2. Cluster criteria: **2+ items sharing a common tension**
3. For each cluster:
   - Name the cluster (e.g., "Agent infrastructure evaluation")
   - List member items by their # from the message list
   - Apply S3 analysis once for the entire cluster (not per item)
4. For clusters of Reference items that share a hidden tension: upgrade the cluster to Action-level and apply S3 to the cluster as a whole.

### 5. Present summary table

```
| # | Time | Preview | GTD | Project | Task | Driver (1-line) | Cluster |
|---|------|---------|-----|---------|------|-----------------|---------|
| 1 | 08:05 | WeDance logo... | Action | WeDance | Integrate logo | No visual identity for festival MVP | — |
| 2 | 08:06 | OpenFang... | Reference | ikigai | — | — | Agent Infra |
| 3 | 08:07 | inference.sh... | Reference | ikigai | — | — | Agent Infra |
| 4 | 13:02 | Shape Up... | Action | WeDance | Read & extract | Ad-hoc planning risks MVP | — |
```

**Note:** The `Driver (1-line)` column is blank for non-Action items. The `Cluster` column is blank for non-clustered items. Omit both columns entirely when there are no Action items or clusters in the batch.

### 6. Update project docs (source of truth)

For each actionable item:
- Read the project's `README.md` (or `TODO.md`, `docs/backlog.yaml` if they exist)
- Add the task to the project's next steps / backlog
- This is where the task actually lives — not in the daily review file

### 7. Save to inbox file

Save to `inbox/YYYY-MM-DD-HH-MM.md` (timestamp of the first message in the batch):
- `## Summary` — counts with S3 note: "N actions (M with S3 analysis), N references, N clusters detected"
- `## Messages` — per-message blocks with GTD classification
  - **Action items** get an `#### S3 Analysis` sub-block:
    - **Tension:** 1-2 sentences
    - **Driver:** table with Conditions | Effect | Relevance
    - **Requirement:** blockquote with "[who] needs [conditions] so that [outcomes]"
    - **Response Options:** checkboxes (2-3 options)
  - **Reference/Someday/Trash items** — no S3 block, same as before
- `## Clusters` (when detected) — grouped S3 analysis:
  - Cluster name, member items by #, single S3 analysis for the group
- Note which project docs were updated (traceability)

The daily review file (`sessions/YYYY-MM-DD-daily-review.md`) should only contain a link to the inbox file, not the full content.

### 8. Add reading items to Notion Reading Inbox

For each processed message that has an external URL (articles, tools, repos, threads) and is classified as Reference, Action (read/evaluate), or Content Idea with a link — create a card on the **Reading Inbox** Notion board.

Use the Notion MCP `create-pages` tool with:
- **Parent data source:** `40473b3d-377c-4ddf-b7c4-9407bfc65f72`
- **Properties:**
  - `Name`: Short descriptive title
  - `Status`: "To Read" (for items marked Worth Reading: Yes) or "Unread" (for Maybe/Skim)
  - `Source`: "Telegram"
  - `Type`: One of Tool, Article, Thread, Video, Reference, Repo
  - `Summary`: 1-2 sentence summary
  - `Why It Matters`: Driver summary — 1 sentence connecting item to mission/OKRs (for Action items, sourced from S3 Driver analysis; for Reference items, a brief relevance note)
  - `Project`: JSON array of project names, e.g. `["ikigai", "WeDance"]`
  - `Worth Reading`: Yes / Skim / Maybe / No
  - `userDefined:URL`: The source URL
  - `date:Date Added:start`: ISO date (YYYY-MM-DD)
  - `date:Date Added:is_datetime`: 0

**For Action items, also include page `content` with S3 analysis:**

```
## S3 Analysis

### Tension
[1-2 sentences — what dissonance prompted this]

### Driver
<table header-row="true">
	<tr>
		<td>Conditions</td>
		<td>Effect</td>
		<td>Relevance</td>
	</tr>
	<tr>
		<td>[observable facts]</td>
		<td>[consequences]</td>
		<td>[why it matters for mission/OKRs]</td>
	</tr>
</table>

### Requirement
> [who] needs [conditions] so that [outcomes]

### Response Options
- [ ] [concrete action A]
- [ ] [alternative approach B]
- [ ] [defer/skip option]
```

**For clustered items:** Each card in the cluster gets the same cluster-level S3 content, plus a callout at the top:

```
<callout icon="🔗" color="purple_bg">
	**Cluster: [Name]** — related cards: [list sibling item names]
</callout>
```

**For Reference items (non-clustered):** Properties only, no page content. This is the current behavior.

**Skip items that:** have no URL, are purely task-oriented (no reading needed), are voice notes, or are already done/actioned.

### 9. React with GTD emojis in Telegram

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

### 10. Append PR links to messages (when available)

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

**Information flow:** Telegram -> 👀 (seen) -> GTD classify -> S3 analysis (Action/Cluster only) -> `inbox/` file (raw + processed + S3) -> Project README (source of truth) -> Notion Reading Inbox (properties + S3 page content for Actions) -> GTD emoji in Telegram -> PR link in Telegram -> PROJECTS.md (cache) -> Daily Review (link only).

## Output

The GTD + S3 summary table, S3 analysis blocks for Action items/clusters, and a list of project docs that were updated.
