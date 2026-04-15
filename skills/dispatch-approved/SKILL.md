---
description: "Dispatch all approved agent tasks from Notion Control Center. Picks up cards where Status='To do' and Assigned Agent is set, then launches each via the /inbox pattern (worktree + tmux). Always manual — never auto-runs."
user_invocable: true
---

> **⚠️ Migration in progress (razbakov/ikigai#73):** Control Center has moved from Notion to GitHub Issues + Project v2. When this skill references creating/reading/updating Notion cards or pages, translate to GitHub equivalents:
> - **Create card** → `gh issue create --repo <project-repo> --title "<title>" --label agent:<name> --body "<S3 body>"` then `gh project item-add 5 --owner razbakov --url <issue-url>`
> - **Read cards** → `gh issue list --repo <repo> --label agent:<name> --state open` (or across repos via `gh search issues "org:razbakov label:agent:<name> state:open"`)
> - **Update card status** → move on board: `gh project item-edit` with the Status field, or close via `gh issue close`
> - **Board columns**: Inbox → To do → In progress → To review → Done
> - **Do not call any `notion-*` MCP tools** — the Notion MCP is disabled.



# Dispatch Approved — Launch Agents for Approved Tasks

Picks up Notion Control Center cards that Alex has approved (moved from "Suggested" to "To do") and dispatches an AI agent for each one using the standard `/inbox` pattern.

## Trigger

User says `/dispatch-approved`, "dispatch approved tasks", "launch approved agents", or "run approved".

## Context

- **Working directory:** `~/Projects/ikigai`
- **Notion Control Center:** data source `collection://32b9a1fd-a351-809d-bd4d-000b0d579048`
- **Agent dispatch pattern:** follows `/inbox` skill exactly (worktree, tmux, Notion update)
- **Project Path Registry:** in `CLAUDE.md` (maps project names to git repo paths)
- **Agent Team spec:** `initiatives/agent-team.md` (personas for Viktor/Luna/Marco/Kai)

## Process

### 1. Query Notion for approved tasks

Search the Control Center for cards where:
- Status = "To do"
- Assigned Agent is set (Viktor, Luna, Marco, Kai, or Maya)

```
notion-search(query: "To do", data_source_url: "collection://32b9a1fd-a351-809d-bd4d-000b0d579048", page_size: 25)
```

For each result, fetch the full card to read:
- Name (task title)
- Project
- Assigned Agent
- Priority
- Effort
- Page content (S3 analysis, source, OKR alignment)

Filter to only cards that have "Assigned Agent" set — cards without an agent assignment were created by other skills (process-inbox, manual) and should be dispatched via `/inbox` directly.

### 2. Skip Maya-assigned tasks

If Assigned Agent = "Maya", these are operational tasks Maya handles directly (inbox processing, calendar sync, etc.). Skip them — they don't need agent dispatch.

### 3. Build agent persona context

For each agent, include their persona in the dispatch prompt:

**Viktor (CTO):** "You are Viktor, the CTO. Direct, technical, quality-focused. You own all engineering: write/review/ship code, tests, CI, deployments. Must create PRs for changes. Does not decide product direction or handle marketing."

**Luna (Head of Content):** "You are Luna, Head of Content & Growth. Creative, energetic, trend-aware. Turn ideas into published content: blog posts, social posts, SEO audits, visual assets, campaigns. Must reflect Alex's authentic voice. All content reviewed by Alex before publishing."

**Marco (Head of Strategy):** "You are Marco, Head of Strategy & Business. Analytical, structured, results-focused. OKRs, portfolio prioritization, business development, hypothesis validation, competitor analysis. Makes recommendations — Alex decides."

**Kai (Community Manager):** "You are Kai, Community & Partnerships Manager. Social, connector-minded, organized about people. Event prep, contact enrichment, partnership management, community channels, networking. Alex is the face — Kai never represents Alex externally."

### 4. Dispatch each task via /inbox pattern

For each approved card, follow the `/inbox` skill process exactly:

#### a. Log raw input

```bash
echo "$(date -Iseconds) | DISPATCHED | ${TASK_SLUG} | ${PROJECT} | [dispatch-approved] ${CARD_TITLE}" >> ~/Tasks/inbox.log
```

#### b. Resolve project path

Look up the project in the Project Path Registry (CLAUDE.md). Use that path for the git worktree.

#### c. Create worktree

```bash
TASK_SLUG=$(echo "${CARD_TITLE}" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-' | head -c 40)
TASK_DIR=~/Tasks/${PROJECT}-${TASK_SLUG}
git -C <repo_path> worktree add ${TASK_DIR} -b agent/${TASK_SLUG} main
```

#### d. Install dependencies (if applicable)

```bash
cd ${TASK_DIR} && bun install --frozen-lockfile 2>/dev/null || npm ci 2>/dev/null || true
```

#### e. Write prompt file

Write `${TASK_DIR}/agent-prompt.md` with:
- Agent persona context (from step 3)
- Task title and description from the Notion card
- S3 analysis from the card content
- The Notion card URL so the agent can update it when done
- Delivery checklist (commit, push, create PR, update Notion to "To review")

#### f. Launch tmux session

```bash
SESSION_NAME="wf-${TASK_SLUG}"
tmux new-session -d -s "${SESSION_NAME}" -c "${TASK_DIR}" "/tmp/run-${TASK_SLUG}.sh"
```

#### g. Update Notion card

```
notion-update-page(
  page_id: "<card_id>",
  command: "update_properties",
  properties: { "Status": "In progress" }
)
```

### 5. Report dispatched agents

Print to chat:

```
## Dispatched Agents

| # | Task | Project | Agent | tmux session |
|---|------|---------|-------|-------------|
| 1 | Fix Dropbox sync | sdtv | Viktor | wf-fix-dropbox-sync |
| 2 | Write blog post | razbakov.com | Luna | wf-write-blog-post |

Dispatched N agents. Use `/scrum` to check status.
Skipped M Maya-assigned tasks (operational, not dispatchable).
```

## Rules

- **Never auto-run.** Alex must explicitly invoke `/dispatch-approved`.
- **Only dispatch cards with Assigned Agent.** Cards without an agent were created by other workflows.
- **Skip Maya tasks.** Maya tasks are operational, not agent-dispatchable.
- **Follow /inbox pattern exactly.** Worktree, tmux, agent-prompt.md, inbox.log — all required.
- **Update Notion to "In progress".** Never leave a dispatched card as "To do".
- **One tmux session per task.** Don't batch multiple tasks into one agent.
- **Include agent persona.** The agent should behave according to their role definition.
- **Include delivery checklist.** Every agent must end with a PR, not just local commits.
