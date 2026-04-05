---
name: inbox
description: "Fire-and-forget agent dispatch. Use when user says '/inbox: <task>' or 'inbox <task>'. Spawns a Claude agent in a tmux session with git worktree isolation. Logs everything for retry. Does NOT wait or check on the agent."
user_invocable: true
argument: required
---

# Inbox — Fire-and-Forget Agent Dispatch

Dispatch a background Claude agent to handle a task autonomously. You start it and walk away.

## Process

### 1. Log raw input

Append to `~/Tasks/inbox.log` with timestamp. This is the retry source of truth.

```
echo "$(date -Iseconds) | DISPATCHED | SLUG | PROJECT | RAW_INPUT" >> ~/Tasks/inbox.log
```

Every field matters — if the agent fails, the user can grep this log and re-dispatch.

### 2. Parse the task

From the user's raw input, determine:

- **PROJECT**: Which project from `~/Projects/` this belongs to. Infer from keywords (e.g. "wedance" → WeDance, "blog" → razbakov.com, "contact" → ikigai). If ambiguous, pick the most likely. If truly unknown, use `ikigai`.
- **TASK**: A short kebab-case slug (3-5 words max). E.g. "fix-login-bug", "add-carousel-post", "update-readme".
- **PROMPT**: The full task description to give the agent. Include enough context for it to work autonomously. Reference the project's README/CLAUDE.md for conventions.

### 3. Create worktree

```bash
TASK_DIR=~/Tasks/${PROJECT}-${TASK}
git -C ~/Projects/${PROJECT} worktree add ${TASK_DIR} -b agent/${TASK} main
```

If the worktree already exists (same slug), append a number: `${TASK}-2`, `${TASK}-3`.

If the project has no git repo, just create a plain directory:
```bash
mkdir -p ${TASK_DIR}
cp -r ~/Projects/${PROJECT}/ ${TASK_DIR}/
```

### 4. Install dependencies (if applicable)

Check if the project has `package.json`, `bun.lockb`, or `node_modules`:

```bash
# Only if package.json exists in the worktree
cd ${TASK_DIR} && bun install --frozen-lockfile 2>/dev/null || npm ci 2>/dev/null || true
```

Skip this step for non-JS projects or projects without package.json.

### 5. Create Control Center card in Notion

Every agent must have a tracking card. Create one before launching:

```
notion-create-pages(
  parent: { data_source_id: "32b9a1fd-a351-809d-bd4d-000b0d579048" },
  pages: [{
    properties: {
      "Name": "<TASK title>",
      "Status": "To do",
      "Project": "<PROJECT>",
      "GTD Type": "Action",
      "Priority": "<inferred priority>",
      "Source": "Agent",
      "Effort": "<S|M|L>"
    },
    content: "## S3 Analysis\n\n### Tension\n<1-2 sentences>\n\n### Driver\n| Conditions | Effect | Relevance |\n|------------|--------|----------|\n| <facts> | <consequences> | <why it matters> |\n\n### Requirement\n> <who needs what so that what>\n\n### Response Options\n- [ ] <option A>\n- [ ] <option B>\n- [ ] <defer/skip>\n\n---\n\n**Agent:** tmux wf-${TASK}\n**Worktree:** ${TASK_DIR}",
    icon: "🤖"
  }]
)
```

Save the returned Notion page URL — it goes into the agent prompt file so the agent can update the card with results.

### 6. Write prompt file

Write the full prompt to `${TASK_DIR}/agent-prompt.md`. Include the Notion card URL so the agent can update it. This is the raw input log for this specific task.

```markdown
# Agent Task: ${TASK}

**Project:** ${PROJECT}
**Dispatched:** $(date -Iseconds)
**Notion card:** <NOTION_PAGE_URL>
**Raw input:** <exact user input, unedited>

## Instructions

<expanded prompt with context>

When done, update the Notion card:
1. Set Status to "To review": notion-update-page(page_id, command: "update_properties", properties: { "Status": "To review" })
2. Append a ## Result section with what was done, where to find it, and next steps.
```

The expanded prompt MUST always end with a delivery checklist. Agents that finish without a PR leave invisible work in worktrees.

**For tasks implementing a GitHub issue:**

```
### Delivery checklist
1. Run build/tests to verify no errors
2. Commit changes with a descriptive message referencing the issue (e.g. "Add hero image #11")
3. Push the branch: `git push -u origin agent/${TASK}`
4. Create a pull request: `gh pr create --title "<short title>" --body "<summary + Closes #N>"`
5. The PR body must include: a Summary section, a Test Plan section, and `Closes #<ISSUE_NUMBER>`
```

**For all other tasks (research, skill creation, config changes, etc.):**

```
### Delivery checklist
1. Commit all changes with a descriptive message
2. Push the branch: `git push -u origin agent/${TASK}`
3. Create a pull request: `gh pr create --title "<short title>" --body "<summary of what was done>"`
```

Every agent must deliver a reviewable PR, not just a local commit.

### 7. Launch in tmux

```bash
PROMPT=$(cat ${TASK_DIR}/agent-prompt.md)
SESSION_NAME="wf-${TASK}"

cat > /tmp/run-${TASK}.sh << SCRIPT
#!/bin/bash
cd ${TASK_DIR}
claude --permission-mode bypassPermissions --output-format stream-json --verbose -p "$(cat ${TASK_DIR}/agent-prompt.md)" \
  2>&1 | tee ${TASK_DIR}/agent.log
echo "EXIT_CODE=\$?" >> ${TASK_DIR}/agent.log
echo "AGENT_FINISHED=$(date -Iseconds)" >> ${TASK_DIR}/agent.log
bash
SCRIPT
chmod +x /tmp/run-${TASK}.sh

tmux new-session -d -s "${SESSION_NAME}" -c "${TASK_DIR}" "/tmp/run-${TASK}.sh"
```

### 8. Report and move on

Tell the user ONE line:

```
Agent dispatched: tmux attach -t ${SESSION_NAME}
```

Do NOT:
- Wait for the agent to finish
- Check if it started successfully
- Offer to monitor it
- Ask follow-up questions

Just dispatch and stop. The user will use `/scrum` to check later.

## Important

- **Never skip logging.** The `inbox.log` and `agent-prompt.md` are the retry mechanism.
- **Never wait.** This is fire-and-forget.
- **Never ask.** Infer the project. Pick a slug. Dispatch.
- **Always use tmux.** The agent must survive terminal closure.
- **Always log output.** The `agent.log` via `tee` is how `/scrum` checks status.

## Retry Pattern

If a task needs retry, the user will say `/inbox: retry wf-TASK`. In that case:
1. Read `~/Tasks/*/agent-prompt.md` for the matching task
2. Check `agent.log` for what went wrong
3. Re-dispatch with adjusted prompt (mention the previous failure)
4. Use a new slug: `${TASK}-retry` or `${TASK}-2`
