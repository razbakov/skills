---
name: review-all-prs
description: "Dispatch parallel agents to address review comments on all open PRs. Each agent fixes code, replies inline, resolves threads, and reports what needs human input. Use when user says '/review-all-prs', 'fix all PR reviews', 'address all reviews', or when /scrum shows PRs with pending reviews."
user_invocable: true
---

# Review All PRs — Parallel Review Response

Dispatch one agent per PR to address review comments. Agents fix what they can autonomously. Human gets a summary of what needs decisions.

## Process

### 1. Discover PRs with unresolved review threads

For each project in `~/Projects/` that has open PRs:

```bash
cd ~/Projects/PROJECT
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
gh pr list --state open --json number,title,url,headRefName
```

For each PR, check for unresolved threads:

```bash
gh api graphql -f query='
query {
  repository(owner: "OWNER", name: "REPO") {
    pullRequest(number: NUMBER) {
      reviewThreads(first: 50) {
        nodes { isResolved }
      }
    }
  }
}' --jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)] | length'
```

Skip PRs with 0 unresolved threads.

### 2. Dispatch one agent per PR via /inbox pattern

For each PR with unresolved threads, dispatch using the `/inbox` pattern:

- **PROJECT**: The project the PR belongs to
- **TASK**: `pr-review-${PR_NUMBER}`
- **WORKTREE**: `~/Tasks/${PROJECT}-pr-review-${PR_NUMBER}`
- **BRANCH**: Use the PR's existing branch (checkout, don't create new)

The worktree setup is different from normal `/inbox` — we need the PR branch, not a new branch:

```bash
TASK_DIR=~/Tasks/${PROJECT}-pr-review-${PR_NUMBER}
git -C ~/Projects/${PROJECT} worktree add ${TASK_DIR} ${PR_BRANCH}
```

### 3. Agent prompt template

Each agent gets this prompt:

```markdown
# Address PR review comments for PR #NUMBER

**Repo:** OWNER/REPO
**PR:** #NUMBER — TITLE
**Branch:** BRANCH
**URL:** PR_URL

## Instructions

You are addressing review comments on this PR. Follow the pr-review-responder workflow:

1. Fetch all inline review comments:
   `gh api repos/OWNER/REPO/pulls/NUMBER/comments --jq '.[] | {id, path, line, body}'`

2. Categorize each comment:
   - **Code fix needed** → Fix the code, commit with SHA reference
   - **Acknowledged (missing feature)** → Create a GitHub issue, reply with link
   - **Acknowledged (product decision)** → DO NOT fix or create issue. Write to NEEDS_INPUT file instead.
   - **By design** → Reply with reasoning
   - **Already fixed** → Reply noting the commit

3. Fix all code issues, then verify:
   ```bash
   bun run build 2>&1 || npm run build 2>&1 || true
   ```

4. Commit and push:
   ```bash
   git add -A && git commit -m "Address PR #NUMBER review feedback" && git push
   ```

5. Reply to each comment inline:
   ```bash
   gh api -X POST repos/OWNER/REPO/pulls/NUMBER/comments -f body="Fixed in SHA" -F in_reply_to=COMMENT_ID
   ```

6. Resolve threads via GraphQL (get thread IDs first, then resolveReviewThread mutation)

7. **For items needing human input**, append to `${TASK_DIR}/needs-input.md`:
   ```markdown
   ## PR #NUMBER — TITLE
   - [ ] Comment ID XXXX: <summary of what needs deciding>
   ```

### Delivery checklist
1. All fixable comments addressed with commits
2. All comments replied to inline
3. All auto-fixable threads resolved
4. Issues created for acknowledged missing features
5. needs-input.md written for anything requiring human decision
```

### 4. Launch all agents in parallel

Use the standard `/inbox` tmux launch pattern for each PR. Session name: `wf-pr-review-${PR_NUMBER}`.

### 5. Report dispatch summary

After dispatching all agents, output:

```
Dispatched N agents to address PR reviews:
- wf-pr-review-22 (PROJECT) — PR #22: Title (X unresolved threads)
- wf-pr-review-23 (PROJECT) — PR #23: Title (Y unresolved threads)

Run /scrum to check progress.
```

## Collecting Results

When agents finish (check via `/scrum`), collect results:

```bash
# Check for needs-input files across all review agents
for dir in ~/Tasks/*-pr-review-*/; do
  if [ -f "$dir/needs-input.md" ]; then
    echo "=== $(basename $dir) ==="
    cat "$dir/needs-input.md"
  fi
done
```

Present to user:
```
## Review Results

### Fully resolved (ready to test)
- PR #23: Add hero image — all 3 threads fixed and resolved
- PR #24: Wire useDinners — all 2 threads fixed and resolved

### Needs your input
- PR #26: Signup form
  - [ ] Should email validation use regex or API check?
  - [ ] Password requirements: min 8 chars or min 12?

### Failed (check logs)
- PR #27: Agent crashed — `tail ~/Tasks/project-pr-review-27/agent.log`
```
