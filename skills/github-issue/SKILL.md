---
name: github-issue
description: Use when the user provides a GitHub issue URL, says "implement issue #N", or types "/issue <number>". Covers any request to work on, develop, or implement a GitHub issue end-to-end.
---

# Implement GitHub Issue

End-to-end workflow: fetch issue, plan, implement on feature branch, test, PR, handle reviews until clean.

## Step 1: Fetch Issue

```bash
gh issue view <number> --repo <owner>/<repo> --json title,body,labels,state
```

Extract: goal, acceptance criteria, scope.

## Step 2: Plan

Enter plan mode. Launch Explore agents to understand the codebase, then design the approach.

- Identify existing patterns to follow
- List files to create/modify
- Check what's already implemented vs what's needed
- Get user approval before coding

## Step 3: Feature Branch

```bash
git checkout -b feat/<short-description>
```

## Step 4: Implement

- Create tasks to track progress
- Work through each task, marking complete as you go
- Follow existing codebase patterns
- Run tests after each significant change

## Step 5: Verify

All three must pass before committing:

```bash
bun run build    # TypeScript / build errors
bun run test     # Vitest unit tests (tRPC routers, business logic)
bun run test:e2e # Playwright BDD tests (UI scenarios from .feature files)
```

- Fix any failing tests — don't skip or ignore them
- If existing tests break due to your changes, update the tests to match new behavior
- If you added new backend logic, add unit tests for it
- Report pass counts to the user (e.g. "15 unit + 17 e2e = 32 passing")

## Step 6: Commit and Push

```bash
git add <specific-files>
git commit -m "Description of change

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
git push -u origin feat/<short-description>
```

## Step 7: Create PR

```bash
gh pr create --title "Short title" --body "$(cat <<'EOF'
## Summary
- bullet points

## Test plan
- [x] what was verified

Closes #<issue-number>

Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## Step 8: Handle Reviews

When reviews come in, use the **pr-review-responder** skill:

1. Fetch unresolved threads
2. Fix code issues
3. Run tests
4. Commit and push
5. Reply inline to each comment
6. Resolve threads

Repeat until zero unresolved threads.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Start coding without reading existing code | Always explore codebase first in plan mode |
| Skip plan mode for "simple" issues | Even small issues benefit from understanding context |
| Commit without running tests | Always verify build + tests before commit |
| Reply "fixed" without fixing | Fix code and pass tests first, then reply |
| Forget `Closes #N` in PR body | Include it so the issue auto-closes on merge |
| Push to main directly | Always use a feature branch |
