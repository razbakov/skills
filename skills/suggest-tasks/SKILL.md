---
description: "Scan all projects, OKRs, open PRs, Notion board, and calendar to propose prioritized agent tasks. Creates 'Suggested' cards in Notion Control Center with S3 analysis and agent assignment (Viktor/Luna/Marco/Kai/Maya). Part of Maya's operational loop."
user_invocable: true
---

> **⚠️ Migration in progress (razbakov/ikigai#73):** Control Center has moved from Notion to GitHub Issues + Project v2. When this skill references creating/reading/updating Notion cards or pages, translate to GitHub equivalents:
> - **Create card** → `gh issue create --repo <project-repo> --title "<title>" --label agent:<name> --body "<S3 body>"` then `gh project item-add 5 --owner razbakov --url <issue-url>`
> - **Read cards** → `gh issue list --repo <repo> --label agent:<name> --state open` (or across repos via `gh search issues "org:razbakov label:agent:<name> state:open"`)
> - **Update card status** → move on board: `gh project item-edit` with the Status field, or close via `gh issue close`
> - **Board columns**: Inbox → To do → In progress → To review → Done
> - **Do not call any `notion-*` MCP tools** — the Notion MCP is disabled.



# Suggest Tasks — Maya's Task Proposal Engine

Reads the full project portfolio state and proposes what AI agents should work on next. Creates "Suggested" cards in the Notion Control Center for Alex to approve before dispatch.

## Trigger

User says `/suggest-tasks`, "suggest tasks", "what should agents work on", or auto-invoked as daily-review step 6.5.

## Context

- **Working directory:** `~/Projects/ikigai`
- **Notion Control Center:** database `32b9a1fd-a351-8064-9375-dc9a8f839d7a`, data source `collection://32b9a1fd-a351-809d-bd4d-000b0d579048`
- **OKRs:** `README.md` in ikigai workspace
- **Project inventory:** `PROJECTS.md` in ikigai workspace
- **Project Path Registry:** in `CLAUDE.md` (maps project names to git repo paths)
- **Agent Team spec:** `initiatives/agent-team.md` (PR #44) or Notion card `32c9a1fda3518134bf98c8cfa049d61c`

## Process

### Phase 1 — Gather (parallel, read-only)

Run all sub-steps in parallel. No side effects.

#### 1a. Notion Control Center — existing cards

Search the Control Center for all cards where Status is NOT "Done":

```
notion-search(query: "*", data_source_url: "collection://32b9a1fd-a351-809d-bd4d-000b0d579048", page_size: 25)
```

Build a dedup set: `{ title (lowercase) + project }` for every non-Done card. Also note cards with Status = "Suggested" (stale suggestions from previous runs).

#### 1b. PROJECTS.md — next actions per project

Read `~/Projects/ikigai/PROJECTS.md`. For each project section, extract all unchecked `- [ ]` items. These are the primary candidate pool.

#### 1c. README.md — OKRs, deadlines, Next Steps

Read `~/Projects/ikigai/README.md`. Extract:
- OKR key results with status (Not started / In progress / Done)
- Next Steps checklist (unchecked items)
- Any deadlines mentioned (dates, "overdue", "this week")

#### 1d. Open PRs across repos

For each project in the Project Path Registry (from CLAUDE.md), run:

```bash
cd <repo_path> && gh pr list --state open --json number,title,url,reviewDecision,isDraft 2>/dev/null
```

PRs needing review or with unresolved comments become task candidates.

#### 1e. Running agents (scrum state)

```bash
tmux list-sessions -F "#{session_name}" 2>/dev/null | grep "^wf-"
```

For each `wf-*` session, check if it's still running or done. Done agents may have follow-up work. Failed agents may need retry.

#### 1f. Calendar — next 7 days

```bash
gog cal ls --from today --to "$(date -v+7d +%Y-%m-%d)" 2>/dev/null
```

Flag events that create urgency (festivals, partner meetings, deadlines).

#### 1g. Uncommitted changes

For each project repo in the Project Path Registry:

```bash
cd <repo_path> && git status --short 2>/dev/null
```

Repos with uncommitted changes = potential "commit and PR" candidates.

### Phase 2 — Score & Prioritize

For each candidate task from Phase 1, assign a priority:

**Scoring factors:**
1. **Deadline proximity** — Overdue = High. Due this week = High. Due next week = Medium. No deadline = Low.
2. **OKR alignment** — Directly moves a KR = High. Supports an objective = Medium. No alignment = Low.
3. **Partner commitment** — Promise to a partner (Kirill/SDTV, Amado/DanceGods) = boost to High.
4. **Quick wins** — Effort S with Medium+ priority = boost (favor shipping over planning).
5. **PR review** — Open PR with no review = High (fast to ship, unblocks work).
6. **Agent follow-up** — Previous agent finished related work = boost (momentum).

**Priority mapping:**
- 🔴 High: deadline <=7 days, or OKR-critical, or partner commitment
- 🟡 Medium: OKR-aligned, no immediate deadline
- 🟢 Low: nice-to-have, no deadline, no OKR link

### Phase 3 — Assign Agent

Route each task to the right agent:

| Signal | Agent |
|--------|-------|
| Code changes, PR reviews, bug fixes, architecture, tests, deployments | **Viktor** |
| Blog posts, SEO audits, social media, content creation, marketing campaigns, YouTube | **Luna** |
| Strategy docs, OKR analysis, business models, market research, pitch materials | **Marco** |
| Contact enrichment, event follow-up, community outreach, partnership ops | **Kai** |
| Inbox processing, calendar sync, skill maintenance, project sync | **Maya** (self — not dispatched) |

When in doubt, check:
- GTD Type = "Content Idea" → Luna
- GTD Type = "Action" + project is a code project → Viktor
- Task mentions "strategy", "OKR", "business", "pricing" → Marco
- Task mentions a person's name, "event", "follow-up" → Kai

### Phase 4 — Deduplicate

For each candidate, before creating a Notion card:

1. **Title match**: Normalize both candidate and existing card titles (lowercase, strip "the/a/an/for/in/to"). If >60% of significant words overlap AND same project → skip.
2. **Active agent match**: If a `wf-*` tmux session is working on a related task for the same project → skip.
3. **Stale suggestion check**: If an existing "Suggested" card matches this task and is older than 7 days → flag in output as stale, don't recreate.

### Phase 5 — Create "Suggested" Cards

For each surviving candidate, create a Notion card:

```
notion-create-pages(
  parent: { data_source_id: "32b9a1fd-a351-809d-bd4d-000b0d579048" },
  pages: [{
    properties: {
      "Name": "<task title>",
      "Status": "Suggested",
      "Project": "<project name from dropdown>",
      "GTD Type": "Action",
      "Priority": "<🔴 High | 🟡 Medium | 🟢 Low>",
      "Source": "Daily Review",
      "Effort": "<S | M | L>",
      "Assigned Agent": "<Viktor | Luna | Marco | Kai | Maya>"
    },
    content: "## S3 Analysis\n\n### Tension\n<1-2 sentences: what gap exists between current state and desired state?>\n\n### Driver\n| Conditions | Effect | Relevance |\n|---|---|---|\n| <observable facts> | <consequences if unaddressed> | <connection to OKRs or mission> |\n\n### Requirement\n> <who> needs <what conditions> so that <desired outcomes>\n\n### Response Options\n- [ ] <the suggested action — what the agent will do>\n- [ ] <alternative approach>\n- [ ] Defer to next week\n\n---\n\n**Source:** <where this task came from — e.g., PROJECTS.md → sdtv → 'Fix Dropbox sync in prod'>\n**OKR Alignment:** <O1: KR3 | O2: KR1 | None>",
    icon: "💡"
  }]
)
```

**Batch creation:** Create up to 10 cards per run. If more candidates exist, pick the top 10 by priority and note the overflow in the summary.

### Phase 6 — Print Summary

Output to chat:

```
## Suggested Agent Tasks

| # | Task | Project | Agent | Priority | Effort | OKR |
|---|------|---------|-------|----------|--------|-----|
| 1 | ... | ... | Viktor | 🔴 High | S | O1:KR1 |
| 2 | ... | ... | Luna | 🟡 Medium | M | O2:KR1 |

Created N new "Suggested" cards in Notion Control Center.
Skipped M tasks (already tracked in Notion).
Stale suggestions (>7 days): K cards — consider archiving.

**Next:** Review in Notion → move approved cards to "To do" → run `/dispatch-approved`
```

## Dedup Edge Cases

- "Fix Dropbox sync" in PROJECTS.md and "Dropbox sync fails in prod" in Notion → same task, skip.
- "Review PR #23" and "Review PR #24" → different tasks, create both.
- A task from README.md "Next Steps" that already has a Notion card → skip.
- An agent that just finished creating a PR → if PR needs review, suggest "Review PR #N" as new task.

## Rules

- **Never auto-dispatch.** This skill only creates "Suggested" cards. Alex approves by moving to "To do".
- **Idempotent.** Running twice produces 0 new cards (all deduped).
- **Max 10 cards per run.** More than 10 overwhelms the approval queue.
- **S3 analysis required** on every card — no exceptions.
- **Assigned Agent required** on every card — this is how dispatch-approved knows who to route to.
- **Project must match** the Notion dropdown options exactly. If a project isn't in the dropdown, use the closest match or "ikigai" as fallback.
