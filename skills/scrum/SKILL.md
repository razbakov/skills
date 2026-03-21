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

**c) Check git status in worktree**
```bash
cd ${TASK_DIR} && git status --short 2>/dev/null
git log --oneline main..HEAD 2>/dev/null
```
- Has commits on branch → work was done
- Has uncommitted changes → work in progress or agent crashed mid-edit
- Clean → either not started or already merged

### 3. Present the dashboard

Output a table:

```
## Agent Status — $(date)

| Session | Project | Status | Branch | Changes | Age |
|---------|---------|--------|--------|---------|-----|
| wf-fix-login | wedance | RUNNING | agent/fix-login | 2 commits, 1 uncommitted | 15m |
| wf-add-tests | sdtv | DONE | agent/add-tests | 3 commits | 1h |
| wf-update-readme | ikigai | FAILED | agent/update-readme | 0 commits, 2 uncommitted | 30m |
```

Status values:
- **RUNNING** — claude process alive, agent working
- **DONE** — agent finished successfully (exit 0, has commits)
- **FAILED** — agent crashed or errored (non-zero exit, error in log)
- **NEEDS INPUT** — agent is waiting for something (permission, clarification)
- **STALE** — tmux session exists but no claude process and no completion signal
- **EMPTY** — no work done (no commits, no changes)

### 4. Show actionable items

After the table, list actions for non-running agents:

**For DONE agents:**
```
wf-add-tests (sdtv): DONE — 3 commits on agent/add-tests
  Review: cd ~/Tasks/sdtv-add-tests && git log --oneline main..HEAD
  Merge:  cd ~/Projects/sdtv && git merge agent/add-tests
  Clean:  tmux kill-session -t wf-add-tests && git -C ~/Projects/sdtv worktree remove ~/Tasks/sdtv-add-tests
```

**For FAILED agents:**
```
wf-update-readme (ikigai): FAILED
  Error: <last error line from agent.log>
  Log:   tail -50 ~/Tasks/ikigai-update-readme/agent.log
  Retry: /inbox: retry wf-update-readme
```

**For STALE agents:**
```
wf-old-task: STALE (created 3 days ago, no activity)
  Kill: tmux kill-session -t wf-old-task
```

### 5. Summary line

End with a one-liner:

```
5 agents: 2 running, 1 done (ready to merge), 1 failed, 1 stale
```

## Quick Mode

If the user says `/scrum quick`, skip the detailed actions and just show the table + summary.

## Cleanup Command

If the user says `/scrum clean`, kill all DONE and STALE sessions and remove their worktrees:

```bash
# For each DONE/STALE session:
tmux kill-session -t SESSION
git -C ~/Projects/PROJECT worktree remove ~/Tasks/TASK_DIR --force
```

Always confirm before cleaning: "Kill N sessions and remove N worktrees?"
