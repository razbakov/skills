---
name: linear-todo
description: 'Implement every Linear issue in the "Todo" column by starting one sub-session (a Claude desktop session the user can open and steer) per issue, each in its own git worktree, each ending in a merged PR and a short "try it" comment on the issue. Falls back to background sub-agents where sessions are unavailable (CLI, headless runs). Use when the user says "/linear-todo", "work the Todo column", "implement the Linear todos", "dispatch the Todo issues", "run the sprint from Linear", or a scheduled routine runs it. Not for filing issues (use linear-issue) and not for the webhook-driven Linear agent (use linear-agent).'
argument-hint: '[team] [--max N] [--only RAZ-1,RAZ-2] [--dry-run] [--no-merge] [--subagents]'
---

# Linear Todo → sub-sessions

`Todo` is the consent gate: an issue in `Todo` is approved work. This skill turns each one into its own
sub-session that implements it end to end, while you (the dispatcher) stay short and only route.

```
list Todo ─▶ triage (agent can do it?) ─▶ lock (In Progress, read back)
          ─▶ worktree ~/Streams/<repo>_<ID>_<branch> ─▶ one sub-session per issue ─▶ report table
```

The dispatcher never writes code itself. Each sub-session owns exactly one issue.

## Defaults

| Setting | Default | Override |
|---|---|---|
| Team | `Alösha AI` (key `RAZ`) | first argument |
| Issues per run | 5 | `--max N` |
| Merge | merge when CI is green and there are no conflicts | `--no-merge` stops at the PR |
| Runner | desktop sub-sessions | `--subagents`, or automatic when sessions can't start |
| Repo lookup | Project Path Registry in `~/Orgs/ikigai/CLAUDE.md` | — |

## 1. Collect

1. Check that Linear answers: `whoami` (also tells you who "the user" is for the assignee rule below).
   If it fails, stop and say Linear needs re-auth — a dispatcher that silently sees nothing is worse than none.
2. `list_issues` with `team`, `state: "Todo"`, `limit: 100`, fields
   `id, title, description, url, priority, estimate, labels, assignee, delegate, project, gitBranchName, createdAt`.
   Follow `cursor` while `hasNextPage`.
3. With `--only`, keep just those IDs.

## 2. Triage — who can do it

Skip (leave in `Todo`, list in the report with the reason) when the issue:

- has the label `commander` or `agent:commander` (human-only work, by definition);
- has the label `in-chat` (a chat the user is working in holds it; its link is attached as "Chat: …");
- is delegated to an agent already (`delegate` set — that agent owns it);
- is assigned to someone **other than the user** (never take a teammate's issue; the user's own
  assignment does not block — it usually just means "mine to get done");
- is **human-only by content**: a physical action, a phone call or message to a real person, a GUI-only
  step behind the user's own login (Xcode signing, App Store submit, BotFather), a payment, or a
  decision only the user can make. Read the description, not just the title;
- has no repo you can map with confidence (see 3).

**Mixed issues are dispatched**: the sub-session does the agent part and files the human part as a
blocker issue (step 5). Rank the rest by priority (Urgent → Low, none last), then oldest first, and take
the first `--max`.

**Overlap check.** If two picked issues clearly touch the same files (same component, same migration
number, same router), take only the higher-ranked one this run and say why; the other stays in `Todo`.
Two writers on the same files is how PRs end up conflicting.

With `--dry-run`, print the triage table and stop here.

## 3. Map issue → repo

Use, in order: a repo or path named in the issue or its Linear project description → the Linear project
name matched to the Project Path Registry (`~/Orgs/ikigai/CLAUDE.md`, table "Project Path Registry") →
the current working directory if it is a repo and the issue plainly belongs to it. If still unsure,
skip the issue ("repo unclear") rather than guess.

## 4. Lock and prepare

For each picked issue, in this order:

1. **Lock:** `save_issue` → `state: "In Progress"`, `assignee: "me"` (the user from `whoami`). Then **read it back** (`get_issue`) — `save_issue`
   can return success without writing. Retry once; if it still didn't land, skip the issue and report it.
   The lock is what makes a re-run (or a parallel run) safe: later runs only look at `Todo`.
2. **Worktree** (the user's convention: `~/Projects/<repo>` stays on `main`, branch work lives in `~/Streams`):

   ```bash
   REPO=~/Projects/<repo>            # from the registry
   BRANCH=<gitBranchName from Linear> # keeps Linear's GitHub link automatic
   DIR=~/Streams/<repo>_<ID>_$(echo "$BRANCH" | tr '/' '-')
   git -C "$REPO" fetch origin main
   git -C "$REPO" worktree add "$DIR" -b "$BRANCH" origin/main \
     || git -C "$REPO" worktree add "$DIR" "$BRANCH"   # branch already exists: reuse it
   ```

   If the branch exists only on the remote (an open PR started elsewhere), use
   `git -C "$REPO" fetch origin "$BRANCH" && git -C "$REPO" worktree add "$DIR" -B "$BRANCH" "origin/$BRANCH"`.
   If an open PR already exists for that branch (`gh pr list --head "$BRANCH"`), the sub-session
   continues that PR instead of opening a new one.
   Untracked files such as `.env` are not in a new worktree. Copy `.env` from `$REPO` only when the
   build or tests need it, and say in the brief that it may point at **production** (no writes).
   Install dependencies only if the project needs them to run tests (`bun install` when `bun.lock` exists),
   in the background, in parallel across worktrees.
3. **Comments:** `list_comments` for the issue — they often hold the latest ask or a correction, and the
   brief quotes them.

## 5. Start one sub-session per issue

**Desktop app (default).** Call `mcp__ccd_session__start_session` once per issue (load it with ToolSearch
if deferred):

- `initiation: "user_asked"` — invoking this skill is the user asking for these sessions;
- `context: "fresh"`, `cwd: <DIR>`, `use_worktree: false` (the worktree is already prepared);
- `title: "<ID> <issue title>"` (under 60 chars), `name: <id lowercased, e.g. raz-881>`;
- `prompt`: the brief below; `background`: one paragraph on the project and these rules.

A `cwd` outside the current project may make the app ask the user to trust the folder once; that is
expected, carry on with the other issues.

If the app refuses a start (an automated run, no desktop app, `--subagents`), use the **sub-agent
fallback**: `Agent` with `subagent_type: "engineer"` when it exists (else `general-purpose`),
`run_in_background: true`, the same brief, and "work only inside `<DIR>`" at the top. Never mix both
runners for one issue.

### The brief (one per issue, self-contained)

```
Implement Linear issue <ID>: <title>
<url>

## The issue
<full description, verbatim>
<comments from list_comments, newest last, verbatim — a comment starting "Owner ·" or "Commander ·" is the user speaking>

## Where
Work only in <DIR> (git worktree of <repo>, branch <BRANCH>, based on origin/main).
Read the repo's CLAUDE.md first and follow its conventions.
<If an open PR exists: "Continue PR <url> — push to the same branch, no new PR.">
<If overlap noted: "Another session is on <ID2> in <area>; stay out of those files.">

## Done means
1. The change works: run the project's full checks (for Bun/Nuxt repos: `bun run test` and
   `bun run build`; add or update tests for new logic). Report the commands and exit codes.
2. Commit, push, open a PR. Title = what changed. Body = short summary + `Fixes <ID>`.
   No "Test plan" section, and no mention of Claude or Claude Code in the PR or its comments.
3. <merge> Wait for CI. If it is green and the PR has no conflicts, squash-merge it
   (`gh pr merge --squash --delete-branch`) and set the Linear issue to **In Review** (read it back).
   Never set Done: only the user moves an issue to Done, after checking what's deployed.
   Red CI or conflicts: fix on the same branch and try again (at most 3 rounds), then stop and say why.
   Review comments, partial requirements or nice-to-haves do not block the merge: file each leftover
   as a follow-up issue in the same Linear project instead.
   <no-merge> Stop at the green PR; leave the issue In Progress.
4. Comment on the Linear issue, for a person, max ~6 lines:
   "✅ <what changed, plain words> — <PR link>"
   "Try it: 1. Open <live URL> 2. Click … 3. You should see …"
   Internal change → "Nothing to try — internal change (<what>)."
5. Anything only the user can do (GUI login, signing, a real-world action, a credential you don't
   have, a product decision): create ONE new Linear issue in the same team, assigned to the user,
   label `commander`, title = the action, body = numbered one-action steps, marked as blocking <ID>.
   Do not stop there — finish everything else. If the issue cannot progress at all, or you are
   stopped before finishing, leave a "⏸ Handover" comment (where the work is: branch, PR, worktree,
   uncommitted files; what's next) and move it back to Todo.
6. Never touch other issues' state, never merge other PRs, never push to main.
   When finished, remove nothing — the dispatcher cleans worktrees after merge.

Reply at the end with: PR URL, merged yes/no, Linear state, follow-up and blocker issue IDs.
```

Fill `<merge>` / `<no-merge>` with the one that applies and delete the other.

## 6. Report

One table in chat — the sub-sessions run on their own:

| Issue | Title | Runner | Session / agent | Worktree |
|---|---|---|---|---|
| RAZ-881 | Block merging to main unless tests pass | session | [RAZ-881 …](#local_<id>) | `~/Streams/…` |

Then **Skipped:** one line each, `RAZ-860 · human-only (Telegram bot via BotFather)`.
Then **Left in Todo:** issues beyond `--max` or held back for overlap.

Don't wait or poll. When a sub-session reports back (a side-sessions note), check its claim — the PR's
state with `gh pr view`, the issue state with `get_issue` — before telling the user it's done, and
remove merged worktrees: `git -C ~/Projects/<repo> worktree remove <DIR>`.

If a sub-session or agent is stopped from outside (killed, paused by the user), it can't write its own
handover — the dispatcher does: read the worktree (`git status`, `git log origin/main..HEAD`, open PR),
post the "⏸ Handover" comment, move the issue back to Todo, and keep the worktree.

## Scheduling

Run it from a Claude desktop scheduled task (`mcp__scheduled-tasks__create_scheduled_task`, e.g. hourly
on weekdays) with the prompt "Run the linear-todo skill for team Alösha AI, --max 1." A frequent
schedule must also gate on work already in flight (a lock file, or "skip if a run's issue is still In
Progress"): every run adds agents, and overlapping runs once had 6 agents and 5+ builds fighting for
one machine, none finishing. Desktop
scheduled runs may not be allowed to start sessions; the skill then falls back to sub-agents on its
own. A run that finds nothing to do says nothing.

## Rules

- Only `Todo`. Never act on `Triage`/`Backlog`; never move anything *into* `Todo` except an issue
  handed back with a "⏸ Handover" comment (could not start, or stopped before finishing).
- Never set Done — merged work goes to In Review; the user closes it after checking the deploy.
- One issue → one sub-session → one branch → one PR.
- Lock before starting; verify every Linear write by reading it back.
- Never claim a result you didn't read back.
