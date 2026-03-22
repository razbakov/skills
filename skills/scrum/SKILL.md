---
name: scrum
description: "Check status of all dispatched agents. Use when user says '/scrum'. Lists all wf-* tmux sessions with their status: running, done, failed, needs-input. Reads agent logs and git status."
user_invocable: true
---

# Scrum — Agent Status Dashboard

Check the status of all background agents dispatched via `/inbox`.

## Process

### 1. List all agent sessions

```bash
tmux list-sessions -F "#{session_name} #{session_created}" 2>/dev/null | grep "^wf-"
```

### 2. For each `wf-*` session, determine status

For each session, check these signals in order:

**a) Is the claude process still running?**
```bash
tmux list-panes -t SESSION -F "#{pane_pid}" | xargs -I{} pgrep -P {} claude 2>/dev/null
```
- If claude process exists → **RUNNING**

**b) Check agent.log for completion signals**
```bash
TASK_DIR=$(find ~/Tasks -maxdepth 1 -name "*$(echo SESSION | sed 's/wf-//')*" -type d | head -1)
tail -20 ${TASK_DIR}/agent.log 2>/dev/null
```

Look for:
- `AGENT_FINISHED` → agent completed
- `EXIT_CODE=0` → **DONE** (success)
- `EXIT_CODE=` (non-zero) → **FAILED**
- Error patterns (`Error:`, `fatal:`, `SIGTERM`, `panic`) → **FAILED**
- `permission denied`, `needs input`, `waiting for` → **NEEDS INPUT**

**c) For agents without task dirs, capture tmux pane output**
```bash
tmux capture-pane -t SESSION -p 2>/dev/null | tail -10
```
- Look for "Done" / completion markers → **DONE**
- This catches agents that run in-place (no worktree), like voice-assistant tasks

**d) Check git status in worktree**
```bash
cd ${TASK_DIR} && git status --short 2>/dev/null
git log --oneline main..HEAD 2>/dev/null
```
- Has commits on branch AND has PR → **DONE**
- Has commits on branch but NO PR → **NEEDS PR** (work done but not reviewable)
- Has uncommitted changes → work in progress or agent crashed mid-edit
- Clean → either not started or already merged

### 3. Enrich with real deliverables

Go beyond raw git status — check what was actually produced:

**a) For agents with commits: get commit messages**
```bash
cd ${TASK_DIR} && git log --oneline main..HEAD
```

**b) For agents that pushed branches: check for open PRs**
```bash
# ALWAYS use --json url to get real PR URLs — never construct URLs from directory names
cd ~/Projects/PROJECT && gh pr list --state open --json number,title,headRefName,state,url
```

**c) For PRs: check CI status and review state**
```bash
gh pr checks PR_NUMBER --json name,state
gh pr view PR_NUMBER --json reviewDecision --jq '.reviewDecision'
```

**d) For research/output agents: list produced files with sizes**
```bash
find ${TASK_DIR} -name "*.md" -not -name "agent-prompt.md" -not -name "agent.log"
wc -l < OUTPUT_FILE
```

### 4. Present the dashboard — grouped by project/purpose

DO NOT present a flat table of all sessions. Instead, group related agents and present them with their real deliverables.

**For PR-producing agents, show a PR table:**
```
### WeDance — N PRs open, CI status, review status

| PR | Title | CI | Review |
|----|-------|----|--------|
| #23 | Add hero image to festival page | 3/3 passed | Pending |
```

**For research/batch agents, show a summary table:**
```
### Platform Research (campaign name) — N/N complete

| Platform | Output | Size |
|----------|--------|------|
| LinkedIn | research-post-linkedin.md | 475 lines |
```

**For other agents, show a details table:**
```
### Other Agents

| Session | Project | Status | Details |
|---------|---------|--------|---------|
| wf-process-telegram-inbox | ikigai | DONE | Produced inbox/2026-03-21.md |
```

### 5. Summary block

End with a concise summary showing counts and key actions:

```
23 agents: 0 running, 22 done, 1 stale

 7 PRs ready to review (all CI green)
11 research reports ready to commit
 1 stale agent needs manual review
```

### 6. Check for PRs with unresolved review threads

For any open PRs found in step 3b, check for unresolved review threads:

```bash
gh api graphql -f query='query { repository(owner: "OWNER", name: "REPO") { pullRequest(number: N) { reviewThreads(first: 50) { nodes { isResolved } } } } }' \
  --jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)] | length'
```

If any PRs have unresolved threads, add to recommended actions:

```
N PRs have unresolved review threads — run /review-all-prs to address them
```

### 7. Recommended actions

Prioritized list of what to do next:

1. **Address PR reviews** — if unresolved threads exist, automatically run `/review-all-prs` to dispatch review agents
2. **Review & merge PRs** — PRs with all threads resolved and CI green
3. **Commit uncommitted work** — flag data at risk in worktrees
4. **Investigate stale agents** — with `git diff` commands
5. **Clean up** — which sessions are safe to kill

## Quick Mode

If the user says `/scrum quick`, skip enrichment (PRs, CI, file sizes) and just show the grouped status tables + summary.

## Cleanup Command

If the user says `/scrum clean`, kill all DONE and STALE sessions and remove their worktrees:

```bash
# For each DONE/STALE session:
tmux kill-session -t SESSION
git -C ~/Projects/PROJECT worktree remove ~/Tasks/TASK_DIR --force
```

Always confirm before cleaning: "Kill N sessions and remove N worktrees?"
