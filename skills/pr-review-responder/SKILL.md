---
name: pr-review-responder
description: Use when a PR has review comments to address - fetches inline comments from GitHub, fixes code issues, replies to each comment, and resolves threads. Trigger on "address the review", "fix PR comments", "handle review feedback on PR #X", or when user shares a PR URL with unresolved review threads.
---

# PR Review Responder

## Overview

End-to-end workflow for addressing PR review comments: fetch, categorize, fix, reply inline, resolve threads.

**Core principle:** Fix code first, then reply with the commit reference. Never reply "fixed" without actually fixing.

## Workflow

```
Fetch comments → Categorize → Fix code → Run tests → Reply inline → Resolve threads
```

## Step 1: Fetch Inline Review Comments

```bash
# Get all inline review comments with essential fields
gh api repos/{owner}/{repo}/pulls/{number}/comments \
  --jq '.[] | {id: .id, path: .path, line: .line, body: (.body | split("\n") | first)}'
```

This returns review comments (inline code comments), not PR-level comments.

## Step 2: Categorize by Severity

Group comments by priority before fixing:

| Category | Action |
|----------|--------|
| **Code fix needed** | Fix in code, commit, reply with commit SHA |
| **Acknowledged (out of scope)** | Reply explaining why, with plan for future |
| **By design** | Reply with reasoning for the design choice |
| **Already fixed** | Reply noting which commit addressed it |

## Step 3: Fix Code and Verify

Fix all actionable items, then run tests before replying:

```bash
# Make fixes...
# Then verify
bun run test:e2e  # or project-specific test command
bun run build     # check for type errors
```

**Never reply "fixed" without passing tests.**

## Step 4: Commit and Push

Commit all fixes in one commit with a clear message referencing the review:

```bash
git commit -m "Address PR review feedback

- Fix A (P1)
- Fix B (P2)
..."
git push
```

Note the commit SHA — you'll reference it in replies.

## Step 5: Reply to Each Comment Inline

```bash
# Reply to a specific inline comment by its ID
gh api -X POST repos/{owner}/{repo}/pulls/{number}/comments \
  -f body="Fixed in abc1234 — added unique constraint." \
  -F in_reply_to={comment_id}
```

**Reply format:** Start with "Fixed in {sha}" or "Acknowledged" — be concise.

## Step 6: Resolve Review Threads

First, get thread IDs via GraphQL:

```bash
gh api graphql -f query='
query {
  repository(owner: "{owner}", name: "{repo}") {
    pullRequest(number: {number}) {
      reviewThreads(first: 50) {
        nodes {
          id
          isResolved
          comments(first: 1) {
            nodes { body }
          }
        }
      }
    }
  }
}' --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false) | .id'
```

Then resolve each thread:

```bash
gh api graphql -f query='mutation {
  resolveReviewThread(input: {threadId: "{thread_id}"}) {
    thread { isResolved }
  }
}'
```

Batch resolve in a loop:

```bash
threads=("PRRT_abc" "PRRT_def" "PRRT_ghi")
for t in "${threads[@]}"; do
  gh api graphql -f query="mutation { resolveReviewThread(input: {threadId: \"$t\"}) { thread { isResolved } } }" --silent 2>/dev/null
done
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Reply "fixed" without fixing | Fix code and verify tests pass first |
| Use `gh pr review` for inline replies | Use `gh api -X POST .../pulls/{n}/comments` with `in_reply_to` |
| Try to resolve with comment IDs | Thread IDs (PRRT_...) are different from comment IDs — use GraphQL query |
| Reply via general PR comment | Reply inline so each thread gets its own response |
| Resolve without replying | Reply first, then resolve — reviewer needs to see what was done |
| Use shell `function` keyword in zsh | Use array + for loop instead — zsh aliases conflict with `function` |

## Quick Reference

| Task | Command |
|------|---------|
| List inline comments | `gh api repos/{o}/{r}/pulls/{n}/comments --jq '.[] \| {id, path, body}'` |
| Reply to comment | `gh api -X POST repos/{o}/{r}/pulls/{n}/comments -f body="..." -F in_reply_to={id}` |
| Get thread IDs | GraphQL `reviewThreads` query (see Step 6) |
| Resolve thread | GraphQL `resolveReviewThread` mutation |
| Check resolution | `--jq '.data...reviewThreads.nodes[] \| select(.isResolved == false)'` |
