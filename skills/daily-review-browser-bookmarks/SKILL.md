---
description: Process Chrome bookmarks as GTD + S3 inbox — export recent/unprocessed bookmarks, classify (action/reference/trash), apply S3 analysis to actions and clusters, update project docs, save to inbox file. Part of the daily review workflow.
user_invocable: true
---

> **⚠️ Migration in progress (razbakov/ikigai#73):** Control Center has moved from Notion to GitHub Issues + Project v2. When this skill references creating/reading/updating Notion cards or pages, translate to GitHub equivalents:
> - **Create card** → `gh issue create --repo <project-repo> --title "<title>" --label agent:<name> --body "<S3 body>"` then `gh project item-add 5 --owner razbakov --url <issue-url>`
> - **Read cards** → `gh issue list --repo <repo> --label agent:<name> --state open` (or across repos via `gh search issues "org:razbakov label:agent:<name> state:open"`)
> - **Update card status** → move on board: `gh project item-edit` with the Status field, or close via `gh issue close`
> - **Board columns**: Inbox → To do → In progress → To review → Done
> - **Do not call any `notion-*` MCP tools** — the Notion MCP is disabled.



# Daily Review — Browser Bookmarks (GTD + S3 Collect + Clarify)

Chrome bookmarks are a GTD inbox — links saved throughout the day for later processing. This step collects unprocessed bookmarks, classifies them, and routes actionable items to project docs. Action items and clusters get deeper analysis using Sociocracy 3.0's Tension → Driver → Requirement pattern.

## Trigger

Invoked as part of `/daily-review` or independently via `/daily-review-browser-bookmarks`.

## Context

- **Working directory:** `~/Projects/ikigai`
- **Session storage:** `sessions/`
- **Projects directory:** `~/Projects/`
- **Bookmarks file:** `~/Library/Application Support/Google/Chrome/Default/Bookmarks` (JSON)
- **Processed tracking:** `inbox/.bookmarks-processed.json` (list of already-processed bookmark URLs)
- **Date:** Use yesterday's date as the default export range

## Process

### 1. Export unprocessed bookmarks

Read the Chrome Bookmarks JSON file and extract bookmarks. Chrome stores `date_added` as microseconds since 1601-01-01 UTC (Chrome epoch).

```bash
python3 -c "
import json, datetime, os

CHROME_EPOCH = datetime.datetime(1601, 1, 1)
BOOKMARKS_PATH = os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Bookmarks')
PROCESSED_PATH = os.path.expanduser('~/Projects/ikigai/inbox/.bookmarks-processed.json')

# Load processed URLs
processed = set()
if os.path.exists(PROCESSED_PATH):
    with open(PROCESSED_PATH) as f:
        processed = set(json.load(f))

# Load bookmarks
with open(BOOKMARKS_PATH) as f:
    data = json.load(f)

# Collect all bookmarks
all_bookmarks = []
def collect(node, folder=''):
    if node.get('type') == 'url':
        url = node.get('url', '')
        if url not in processed:
            dt = CHROME_EPOCH + datetime.timedelta(microseconds=int(node.get('date_added', '0')))
            all_bookmarks.append({
                'name': node.get('name', ''),
                'url': url,
                'date_added': dt.strftime('%Y-%m-%d %H:%M'),
                'folder': folder,
            })
    for child in node.get('children', []):
        collect(child, node.get('name', folder))

for key in data.get('roots', {}):
    root = data['roots'][key]
    if isinstance(root, dict):
        collect(root)

# Sort by date descending
all_bookmarks.sort(key=lambda x: x['date_added'], reverse=True)

print(f'Total unprocessed: {len(all_bookmarks)}')
for b in all_bookmarks:
    print(f'--- {b[\"date_added\"]} [{b[\"folder\"]}] ---')
    print(f'{b[\"name\"]}')
    print(f'{b[\"url\"]}')
    print()
"
```

**First run:** All 1700+ bookmarks will be unprocessed. Handle this by focusing on recent bookmarks first (last 7 days), then ask the user if they want to process older ones in batches.

**Filter strategy for daily review:** By default, only process bookmarks added since the last daily review (yesterday). For the first run or catch-up, process the last 7 days.

### 2. Apply GTD Clarify to each bookmark

For each unprocessed bookmark:

- **Is it actionable?** (tool to try, article to read and act on, resource for a project) -> extract a task with project assignment
- **Is it reference material?** (documentation, interesting article, saved for later reading) -> note which project/topic it relates to
- **Is it trash?** (outdated, duplicate, already consumed, no longer relevant) -> mark for deletion
- **Is it someday/maybe?** (interesting but no immediate action) -> note it

**Hint:** Use the bookmark name, URL domain, and folder to infer classification. Fetch the page title/description if the bookmark name is unclear.

**S3 Deep Analysis (Action items and Clusters only):**

For each item classified as **Action**, apply S3 Tension → Driver → Requirement:

1. **Tension**: What dissonance do you feel? What's the gap between current state and desired state? (1-2 sentences, subjective)
2. **Driver** (3-part):
   - *Conditions* — observable facts about what's happening (no evaluation)
   - *Effect* — consequences of those conditions
   - *Relevance* — why it matters for the mission/OKRs
3. **Requirement**: "[who] needs [conditions] so that [outcomes]" (1 sentence, future-oriented)
4. **Response Options**: 2-3 concrete options as checkboxes, including at least one defer/skip option

For Reference, Trash, Someday items that are NOT part of a cluster: skip S3 analysis. GTD classification is sufficient.

### 2.5. Detect Clusters

After GTD classification, scan all items for shared tensions:

1. Group items that point to the same underlying concern:
   - Same problem area (not just same project tag)
   - Multiple tools/articles addressing the same gap
2. Cluster criteria: **2+ items sharing a common tension**
3. For each cluster:
   - Name the cluster (e.g., "Agent infrastructure evaluation")
   - List member items by their # from the bookmark list
   - Apply S3 analysis once for the entire cluster (not per item)
4. For clusters of Reference items that share a hidden tension: upgrade the cluster to Action-level and apply S3 to the cluster as a whole.

### 3. Present summary table

```
| # | Date | Title | URL (domain) | GTD | Project | Action | Driver (1-line) | Cluster |
|---|------|-------|--------------|-----|---------|--------|-----------------|---------|
| 1 | 03-21 | Shape Up | basecamp.com | Action | ikigai | Read & extract | Ad-hoc planning risks MVP | — |
| 2 | 03-20 | OpenFang | openfang.sh | Reference | ikigai | — | — | Agent Infra |
| 3 | 03-20 | inference.sh | inference.sh | Reference | ikigai | — | — | Agent Infra |
| 4 | 03-18 | Old Vue template | github.com | Trash | — | Remove bookmark | — | — |
```

**Note:** The `Driver (1-line)` column is blank for non-Action items. The `Cluster` column is blank for non-clustered items. Omit both columns entirely when there are no Action items or clusters in the batch.

### 4. Update project docs (source of truth)

For each actionable item:
- Read the project's `README.md` (or `TODO.md`, `docs/backlog.yaml` if they exist)
- Add the task to the project's next steps / backlog
- This is where the task actually lives — not in the daily review file

### 5. Save to inbox file

Save to `inbox/YYYY-MM-DD-HH-MM-bookmarks.md`:
- `## Summary` — counts with S3 note: "N actions (M with S3 analysis), N references, N clusters detected"
- `## Bookmarks` — per-bookmark blocks with GTD classification
  - **Action items** get an `#### S3 Analysis` sub-block:
    - **Tension:** 1-2 sentences
    - **Driver:** table with Conditions | Effect | Relevance
    - **Requirement:** blockquote with "[who] needs [conditions] so that [outcomes]"
    - **Response Options:** checkboxes (2-3 options)
  - **Reference/Trash items** — no S3 block, same as before
- `## Clusters` (when detected) — grouped S3 analysis:
  - Cluster name, member items by #, single S3 analysis for the group
- Note which project docs were updated (traceability)

The daily review file (`sessions/YYYY-MM-DD-daily-review.md`) should only contain a link to the inbox file, not the full content.

### 6. Add reading items to Notion Reading Inbox

For each processed bookmark classified as Reference or Action (read/evaluate) — create a card on the **Reading Inbox** Notion board.

Use the Notion MCP `create-pages` tool with:
- **Parent data source:** `40473b3d-377c-4ddf-b7c4-9407bfc65f72`
- **Properties:**
  - `Name`: Short descriptive title
  - `Status`: "To Read" (for items marked Worth Reading: Yes) or "Unread" (for Maybe/Skim)
  - `Source`: "Chrome Bookmark"
  - `Type`: One of Tool, Article, Thread, Video, Reference, Repo
  - `Summary`: 1-2 sentence summary
  - `Why It Matters`: Driver summary — 1 sentence connecting item to mission/OKRs (for Action items, sourced from S3 Driver analysis; for Reference items, a brief relevance note)
  - `Project`: JSON array of project names, e.g. `["ikigai", "WeDance"]`
  - `Worth Reading`: Yes / Skim / Maybe / No
  - `userDefined:URL`: The bookmark URL
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

**Skip items that:** are classified as Trash, are purely task-oriented, or have no reading value.

### 7. Update processed tracking

After processing, add all processed bookmark URLs to `inbox/.bookmarks-processed.json`:

```bash
python3 -c "
import json, os

PROCESSED_PATH = os.path.expanduser('~/Projects/ikigai/inbox/.bookmarks-processed.json')
processed = []
if os.path.exists(PROCESSED_PATH):
    with open(PROCESSED_PATH) as f:
        processed = json.load(f)

# Add newly processed URLs (passed as argument or read from the inbox file)
new_urls = [...]  # URLs that were just processed
processed.extend(new_urls)
processed = list(set(processed))  # dedupe

with open(PROCESSED_PATH, 'w') as f:
    json.dump(processed, f, indent=2)
"
```

**Information flow:** Chrome Bookmarks -> GTD classify -> S3 analysis (Action/Cluster only) -> `inbox/` file (raw + processed + S3) -> Project README (source of truth) -> Notion Reading Inbox (properties + S3 page content for Actions) -> PROJECTS.md (cache, synced later) -> Daily Review (link only).

## Output

The GTD + S3 summary table, S3 analysis blocks for Action items/clusters, and a list of project docs that were updated.
