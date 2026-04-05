# GitHub Next Issue — Pick and Start

Pick the first Todo issue from a GitHub Project board, move it to In Progress, and dispatch an agent to implement it via `/inbox`.

## Trigger

Use when the user says `/github-next-issue`, "next issue", "pick next issue", "start next task", "what's next on the board", or wants to grab the next item from a GitHub project board.

## Process

### 1. Identify the GitHub Project

```bash
gh project list --owner $(gh repo view --json owner -q '.owner.login')
```

If multiple projects exist, pick the one most relevant to the current repo (by name match or most recent). If ambiguous, ask the user.

### 2. List Todo items

```bash
gh project item-list <PROJECT_NUMBER> --owner <OWNER> --format json
```

Filter items where `status == "Todo"`. Sort by position (first item in the list = highest priority).

### 3. Show the issue to the user

Display a one-line summary:
```
First Todo: #<NUMBER> — "<TITLE>" (<POINTS>, <EPIC>)
```

### 4. Move to In Progress

Get the project field IDs and option IDs:
```bash
gh project field-list <PROJECT_NUMBER> --owner <OWNER> --format json
```

Then update the item status:
```bash
gh project item-edit \
  --project-id <PROJECT_ID> \
  --id <ITEM_ID> \
  --field-id <STATUS_FIELD_ID> \
  --single-select-option-id <IN_PROGRESS_OPTION_ID>
```

### 5. Confirm

Tell the user:
```
Issue #<NUMBER> — "<TITLE>" is now In Progress.
```

### 6. Dispatch agent

Use the `/inbox` skill to dispatch an agent to implement the issue. Pass the issue number, title, and body as context so the agent has everything it needs.

**Critical:** The dispatch prompt MUST include instructions to push the branch and create a PR with `gh pr create` that references the issue number (`Closes #N`). Without this, the agent will only commit locally and the work won't be reviewable.

## Important

- Always pick the FIRST Todo item (highest priority by board order)
- Never skip items or reorder — the board order is the priority
- If there are no Todo items, tell the user the board is clear
- This skill works with any GitHub Project V2 board, not just a specific one
