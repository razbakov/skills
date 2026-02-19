---
name: atlassian
description: Interact with Atlassian Jira and Confluence from the terminal. Search, create, and update Jira tickets; read, search, create, and update Confluence pages. Use when the user mentions Jira tickets, issues, work items, sprints, Confluence pages, documentation, or Atlassian in general.
---

# Atlassian — Jira & Confluence CLI

Two CLI tools are used:

| Service    | Tool             | Commands prefix        |
|------------|------------------|------------------------|
| Jira       | `acli` (official)| `acli jira workitem …` |
| Confluence | `confluence-cli` (npm) | `confluence …`   |

## Installation

### Jira — `acli` (Atlassian CLI)

```bash
# macOS via Homebrew
brew tap atlassian/homebrew-acli
brew install acli

# Verify
acli --version
```

### Confluence — `confluence-cli` (NPM)

```bash
# Global install
npm install -g confluence-cli

# Verify
confluence --version
```

## Authentication

### Jira

```bash
# API token auth (run in terminal — replace placeholders)
echo "YOUR_API_TOKEN" | acli jira auth login \
  --site "yoursite.atlassian.net" \
  --email "you@example.com" \
  --token

# Check status
acli jira auth status
```

### Confluence

Add to `~/.zshrc` (or `~/.bashrc`):

```bash
export CONFLUENCE_DOMAIN="yoursite.atlassian.net"
export CONFLUENCE_EMAIL="you@example.com"       # or CONFLUENCE_USERNAME
export CONFLUENCE_API_TOKEN="your-api-token"
export CONFLUENCE_API_PATH="/wiki/rest/api"
export CONFLUENCE_AUTH_TYPE="basic"
```

Or run the interactive setup:

```bash
confluence init
```

Get API tokens at: https://id.atlassian.com/manage-profile/security/api-tokens

## Jira (`acli`)

### Search tickets

```bash
# My open tickets
acli jira workitem search --jql "assignee = currentUser() AND status != Done"

# With specific fields
acli jira workitem search \
  --jql "assignee = currentUser() AND status != Done" \
  --fields "key,summary,status,priority"

# Project-specific
acli jira workitem search --jql "project = PROJ AND status != Done"

# Count only
acli jira workitem search --jql "project = PROJ" --count

# Export CSV
acli jira workitem search \
  --jql "project = PROJ" \
  --fields "key,summary,status,assignee" \
  --csv
```

### View ticket

```bash
acli jira workitem view PROJ-123
acli jira workitem view PROJ-123 --json
acli jira workitem view PROJ-123 --web   # open in browser
```

### Create ticket

```bash
acli jira workitem create \
  --project "PROJ" \
  --type "Task" \
  --summary "Short description" \
  --assignee "@me"
```

### Edit ticket

```bash
acli jira workitem edit --key "PROJ-123" --summary "Updated title"
acli jira workitem edit --key "PROJ-123" --assignee "@me"

# Bulk edit via JQL
acli jira workitem edit \
  --jql "project = PROJ AND status = 'To Do'" \
  --assignee "@me"
```

### Transition (change status)

```bash
acli jira workitem transition --key "PROJ-123" --status "In Progress"
acli jira workitem transition --key "PROJ-123" --status "Done"
```

### Assign

```bash
acli jira workitem assign --key "PROJ-123" --assignee "@me"
acli jira workitem assign --key "PROJ-123" --assignee ""  # unassign
```

### Comments

```bash
acli jira workitem comment create --key "PROJ-123" --body "Plain text comment"
acli jira workitem comment list --key "PROJ-123"
```

### Common JQL patterns

| Pattern                            | Meaning                    |
|------------------------------------|----------------------------|
| `project = PROJ`                   | All tickets in project     |
| `assignee = currentUser()`         | Assigned to me             |
| `status = 'In Progress'`           | Specific status            |
| `status != Done`                   | Not done                   |
| `created >= -7d`                   | Created in last 7 days     |
| `priority = High`                  | High priority              |
| `labels = backend`                 | With label                 |
| `sprint in openSprints()`          | In active sprint           |

### Output formats

- Default: human-readable table
- `--json`: structured JSON (best for scripting)
- `--csv`: CSV export

---

## Confluence (`confluence-cli`)

### List spaces

```bash
confluence spaces
```

### Search pages

```bash
# Text search
confluence search "coupon generation"

# CQL search
confluence search "type=page AND space=SPACE AND title~'API'"

# With limit
confluence search "meeting notes" --limit 10
```

### Read page

```bash
# By page ID
confluence read 123456789

# As markdown (best for AI workflows)
confluence read 123456789 --format markdown

# As HTML
confluence read 123456789 --format html

# By URL
confluence read "https://yoursite.atlassian.net/wiki/spaces/SPACE/pages/123456789"
```

### Page info

```bash
confluence info 123456789
```

### Find page by title

```bash
confluence find "Project Documentation"
confluence find "API Guide" --space SPACE
```

### Create page

```bash
# Inline content
confluence create "Page Title" SPACE --content "Hello World"

# From markdown file
confluence create "Page Title" SPACE --file ./content.md --format markdown

# Child page
confluence create-child "Subsection" 123456789 --content "Content"
```

### Update page

```bash
# Update content from file
confluence update 123456789 --file ./updated.md --format markdown

# Update title
confluence update 123456789 --title "New Title"
```

### Export page for editing

```bash
# Export → edit locally → update
confluence edit 123456789 --output ./page.xml
# ... edit page.xml ...
confluence update 123456789 --file ./page.xml --format storage
```

### Copy page tree

```bash
# Preview first
confluence copy-tree SOURCE_ID TARGET_ID --dry-run

# Copy with exclusions
confluence copy-tree SOURCE_ID TARGET_ID --exclude "*draft*,*temp*" --delay-ms 500
```

### Content formats

| Format     | Flag                | When to use                     |
|------------|---------------------|---------------------------------|
| `storage`  | `--format storage`  | Confluence-native XML (default) |
| `markdown` | `--format markdown` | Developer docs, AI workflows    |
| `html`     | `--format html`     | Standard HTML                   |

---

## Workflow Patterns

### Daily standup — check my work

```bash
acli jira workitem search \
  --jql "assignee = currentUser() AND status = 'In Progress'" \
  --fields "key,summary,status"
```

### Start working on a ticket

```bash
acli jira workitem transition --key "PROJ-123" --status "In Progress"
acli jira workitem comment create --key "PROJ-123" --body "Started working on this"
```

### Close a ticket

```bash
acli jira workitem transition --key "PROJ-123" --status "Done"
```

### Read Confluence docs into context

```bash
# Find a page
confluence find "Project Documentation" --space SPACE

# Read as markdown for AI processing
confluence read PAGE_ID --format markdown
```

### Update docs from code changes

```bash
# Export existing page
confluence read PAGE_ID --format markdown > docs/page.md

# Edit locally, then push back
confluence update PAGE_ID --file docs/page.md --format markdown
```

### Link Jira ticket to Confluence context

```bash
# Get ticket details
acli jira workitem view PROJ-123 --json

# Find related docs
confluence search "type=page AND space=SPACE AND text~'search term'"
```

---

## Troubleshooting

### Check auth status

```bash
# Jira
acli jira auth status

# Confluence
confluence spaces
```

### Known issues

- `acli confluence` has a cloudId null bug — use `confluence-cli` (npm) instead.
