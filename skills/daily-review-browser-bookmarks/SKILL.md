---
description: Process Chrome bookmarks as GTD inbox — export recent/unprocessed bookmarks, classify (action/reference/trash), update project docs, save to inbox file. Part of the daily review workflow.
user_invocable: true
---

# Daily Review — Browser Bookmarks (GTD Collect + Clarify)

Chrome bookmarks are a GTD inbox — links saved throughout the day for later processing. This step collects unprocessed bookmarks, classifies them, and routes actionable items to project docs.

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

### 3. Present summary table

```
| # | Date | Title | URL (domain) | GTD | Project | Action |
|---|------|-------|--------------|-----|---------|--------|
| 1 | 03-21 | Shape Up | basecamp.com | Action | ikigai | Read and evaluate for sprint planning |
| 2 | 03-20 | QVAC by Tether | qvac.tether.io | Reference | — | AI tools reference |
| 3 | 03-18 | Old Vue template | github.com | Trash | — | Remove bookmark |
```

### 4. Update project docs (source of truth)

For each actionable item:
- Read the project's `README.md` (or `TODO.md`, `docs/backlog.yaml` if they exist)
- Add the task to the project's next steps / backlog
- This is where the task actually lives — not in the daily review file

### 5. Save to inbox file

Save to `inbox/YYYY-MM-DD-HH-MM-bookmarks.md`:
- `## Raw` — list of all unprocessed bookmarks (name + URL + date)
- `## Processed` — the GTD summary table
- Note which project docs were updated (traceability)

The daily review file (`sessions/YYYY-MM-DD-daily-review.md`) should only contain a link to the inbox file, not the full content.

### 6. Update processed tracking

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

**Information flow:** Chrome Bookmarks -> `inbox/` file (raw + processed) -> Project README (source of truth) -> PROJECTS.md (cache, synced later) -> Daily Review (link only).

## Output

The GTD summary table and a list of project docs that were updated.
