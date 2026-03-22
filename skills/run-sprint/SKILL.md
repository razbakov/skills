# Run Sprint — Dispatch All Todo Issues in Parallel

Take all Todo issues from a GitHub Project board, move them to In Progress, and dispatch a parallel agent for each one via the `/inbox` pattern.

## Trigger

Use when the user says `/run-sprint`, "run sprint", "dispatch all issues", "start all todos", or wants to blast through an entire sprint backlog with parallel agents.

## Process

### 1. Identify the GitHub Project

```bash
gh project list --owner $(gh repo view --json owner -q '.owner.login')
```

If multiple projects exist, pick the one most relevant to the current repo. If ambiguous, ask the user.

### 2. Get all Todo items

```bash
gh project item-list <PROJECT_NUMBER> --owner <OWNER> --format json
```

Filter items where `status == "Todo"`. Also include items with no status set (they belong to the backlog but weren't categorized).

If there are no Todo items, tell the user the board is clear and stop.

### 3. Get project field IDs

```bash
gh project field-list <PROJECT_NUMBER> --owner <OWNER> --format json
```

Extract the Status field ID and the "In Progress" option ID.

### 4. Move all items to In Progress

Run all `gh project item-edit` calls in parallel:

```bash
gh project item-edit \
  --project-id <PROJECT_ID> \
  --id <ITEM_ID> \
  --field-id <STATUS_FIELD_ID> \
  --single-select-option-id <IN_PROGRESS_OPTION_ID>
```

### 5. Fetch issue bodies

For each issue, fetch the full body to build agent prompts:

```bash
gh issue view <NUMBER> --repo <OWNER>/<REPO> --json title,body -q '.body'
```

### 6. For each issue, follow the `/inbox` dispatch pattern

For every issue, do all of these steps:

**a. Log to inbox.log**
```bash
echo "$(date -Iseconds) | DISPATCHED | <TASK_SLUG> | <PROJECT> | Issue #<N>: <TITLE>" >> ~/Tasks/inbox.log
```

**b. Create git worktree**
```bash
git -C ~/Projects/<PROJECT> worktree add ~/Tasks/<PROJECT>-<TASK_SLUG> -b agent/<TASK_SLUG> main
```

**c. Install dependencies** (if `package.json` exists)
```bash
cd ~/Tasks/<PROJECT>-<TASK_SLUG>/<app-path> && bun install --frozen-lockfile
```

Run all installs in parallel with `&` and `wait`.

**d. Write agent-prompt.md** with:
- Issue number, title, user story
- Context from the issue body (what exists, what needs to change)
- Concrete steps for the agent
- Constraints (story points, patterns to follow, stack info)

**e. Launch in tmux**
```bash
SESSION_NAME="wf-<TASK_SLUG>"
cat > /tmp/run-<TASK_SLUG>.sh << SCRIPT
#!/bin/bash
cd ~/Tasks/<PROJECT>-<TASK_SLUG>
claude --permission-mode bypassPermissions --output-format stream-json --verbose -p "\$(cat ~/Tasks/<PROJECT>-<TASK_SLUG>/agent-prompt.md)" \
  2>&1 | tee ~/Tasks/<PROJECT>-<TASK_SLUG>/agent.log
echo "EXIT_CODE=\$?" >> ~/Tasks/<PROJECT>-<TASK_SLUG>/agent.log
echo "AGENT_FINISHED=\$(date -Iseconds)" >> ~/Tasks/<PROJECT>-<TASK_SLUG>/agent.log
bash
SCRIPT
chmod +x /tmp/run-<TASK_SLUG>.sh
tmux new-session -d -s "${SESSION_NAME}" -c "~/Tasks/<PROJECT>-<TASK_SLUG>" "/tmp/run-<TASK_SLUG>.sh"
```

### 7. Report summary table

Print a table with all dispatched agents:

```
| Session | Issue | Title | Pts |
|---------|-------|-------|-----|
| wf-<slug> | #N | <title> | Xpt |
```

End with: `Use /scrum to check status.`

## Task slug convention

Derive from issue title: `implement-<story-number>-<2-3-keyword-slug>`

Examples:
- "1.2 See activity cards..." → `implement-1-2-activity-cards`
- "2.1 Sign up with name..." → `implement-2-1-signup`
- "5.1 Sign up for a group dinner..." → `implement-5-1-dinner-signup`

## Important

- Dispatch ALL Todo items, not just one
- Each agent gets its own worktree and tmux session — full isolation
- Never wait for agents to finish — this is fire-and-forget
- If two issues touch the same schema (e.g., both add columns), note this in both agent prompts so they handle conflicts gracefully
- Log everything to `~/Tasks/inbox.log` — this is the retry source of truth
- Use `/scrum` skill afterward to monitor progress
