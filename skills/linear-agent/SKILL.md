---
name: linear-agent
description: Turn Claude Code into a native Linear agent that teammates delegate issues to — it picks the issue up in seconds, does the work in the right repo, opens a PR, runs a merge gate and merges, then posts a short human-readable "✅ Done — Try it: 1. Open… 2. Click… 3. You should see…" message. Replaces hourly cron dispatch/merge routines with an event-driven pipeline (Linear agent webhooks + GitHub PR webhooks + a 15-min sweep). Use when someone says "set up a Linear agent", "delegate Linear issues to Claude", "issues don't get done / PRs don't get merged", "make Linear issues turn into merged PRs automatically", "replace the dispatch/merge cron", or wants a self-hosted alternative to Linear coding sessions, Cyrus, Codex or Devin in Linear.
compatibility: macOS or Linux with Python 3.10+, the `claude` CLI (Claude Code, logged in), `gh` (authenticated, admin on the repos), and `cloudflared` with a Cloudflare-managed domain (any tunnel that gives a public HTTPS URL works). Linear workspace admin. Works on Linear's Free plan — a custom actor=app agent needs no paid tier (Linear's own coding sessions do).
---

<role>
You are setting up an autonomous engineering teammate that lives inside Linear. The bar
is: a person delegates an issue and later sees it merged with clear "try it" steps —
nobody has to chase it, poll a cron, or read evidence dumps.
</role>

## What gets built

```
Linear  ──(delegate / @mention)──▶ AgentSessionEvent webhook ─┐
GitHub  ──(PR opened / pushed)───▶ pull_request webhook ──────┤
15-min sweep (open PRs not yet gated) ────────────────────────┤
                                                              ▼
                      scripts/linear-agent.py  (127.0.0.1:5055, behind a tunnel)
                        1. ack within 10 s (thought activity), issue → In Progress
                        2. `claude -p` in AGENT_WORKDIR does the work → PR
                        3. merge gate (`claude -p`, fresh context) → merge → Done
                           blocked → same session fixes the PR → re-gate (≤5 rounds)
                        4. one templated message on the issue
```

`scripts/linear.py` is the shell CLI the agent (and you) use: `issue`, `comment`,
`create`, `delegate`, `blocker`, `digest`, plus owner-only verbs `approve` / `drop` / `done`.

## Operating rules baked into the scripts (keep them when adapting)

1. **Delegation is the trigger.** Delegate → agent (or @mention) starts work instantly.
   Todo auto-delegates only **unassigned** issues — never grab an issue a teammate owns.
2. **Done = merged.** The gate blocks only on what would break `main` or make the merge
   meaningless: merge conflicts, red required CI/build, or a no-op/superseded PR (closed,
   issue → Done). Everything else (open review threads, partial requirements, missing
   preview evidence) merges, and each leftover becomes a follow-up issue.
3. **Blockers are tickets, never comments.** Only for what an agent truly can't do (GUI-only,
   physical, credentials only the human holds). `linear.py blocker` creates a Todo issue
   assigned to the owner, labelled `AGENT_HUMAN_LABEL` (default `commander`), linked as *blocks*, body = **Do this**
   (numbered one-action steps) → **Summary** → **Details** (only if needed). When the owner
   moves it to Done the receiver re-delegates the blocked issue automatically.
4. **Linear is for humans.** Models return a JSON result; the receiver renders one fixed
   template — `### ✅ Done — <plain-language headline>`, **Live**, **PR**, **Try it** (steps
   for a *user on the live product* — never GitHub, files or CI), **Follow-ups**. Internal
   changes say "Nothing to try — internal change (docs only)". Evidence goes in a GitHub PR
   comment, not Linear.
5. **Owner verbs are stamped `Owner ·`.** Every comment written with the owner's API key shows
   the owner as author, so the prefix is the only way to tell the human from an agent. Agents
   must never run `approve|drop|done` (the brief forbids it — an agent once closed its own
   test issue with `done` and impersonated the owner).

## Setup

Work top to bottom; verify each step before the next.

### 1. Config file

`~/.config/linear/agent.env` (chmod 600):

```
AGENT_NAME=Forge                          # display name used in prompts
AGENT_PUBLIC_URL=https://agent.example.com
AGENT_WORKDIR=~/work/control-center       # where `claude -p` runs; its CLAUDE.md must say where repos live
AGENT_REPOS=org/web-app,org/api           # repos whose PRs the app gates & merges
AGENT_OWNER_GITHUB=octocat                # owner's untracked PRs get a tracking issue; others are ignored
AGENT_RULES_FILE=~/work/agent-rules.md    # optional: extra standing rules appended to every brief
AGENT_HUMAN_LABEL=commander               # label for human-only work; auto-created by the first blocker
LINEAR_TEAM_KEY=ENG
LINEAR_API_KEY=lin_api_…                  # the OWNER's personal key (delegating as a user opens real sessions)
LINEAR_OWNER_ID=<owner's Linear user id>  # receives blocker tickets
LINEAR_AGENT_CLIENT_ID=                   # step 3
LINEAR_AGENT_CLIENT_SECRET=               # step 3
LINEAR_AGENT_WEBHOOK_SECRET=              # step 3
GITHUB_WEBHOOK_SECRET=<openssl rand -hex 32>
```

Copy `scripts/linear-agent.py` and `scripts/linear.py` side by side (they import each other).

### 2. Receiver + tunnel

```bash
cloudflared tunnel create linear-agent
cloudflared tunnel route dns --overwrite-dns <TUNNEL-UUID> agent.example.com
```

Route by **UUID**, not name: if a default `config.yml` names another tunnel, `route dns <name>`
silently points the CNAME at *that* tunnel. Fill in `assets/cloudflared.yml` (ingress →
`http://127.0.0.1:5055`). Run both the receiver and the tunnel under a supervisor —
`assets/linear-agent.plist` (macOS launchd) or `assets/linear-agent.service` (systemd user unit). Use a Python ≥3.10 explicitly — macOS `/usr/bin/python3` is 3.9 and dies
on `dict | None`. Check: `curl https://agent.example.com/health` → `not installed` (503) is correct.

### 3. Linear OAuth app (Settings → API → New OAuth application)

- Name = AGENT_NAME, redirect URI `<PUBLIC_URL>/oauth/callback`, Public off.
- Webhooks on → URL `<PUBLIC_URL>/webhook` → App events: **Agent session events**,
  **Inbox notifications**, **Permission changes**.
- Copy client id, client secret, webhook signing secret into agent.env via the copy buttons +
  `pbpaste` (never retype secrets from a screenshot). Restart the receiver.

### 4. Install

Open `<PUBLIC_URL>/install` as a workspace admin → Authorize. The callback stores the token
and the agent's app-user id (`agent-token.json`); the agent now appears under Team → Agents.

### 5. GitHub PR webhooks

```bash
gh api "repos/$R/hooks" -X POST -f name=web -F active=true -f 'events[]=pull_request' \
  -f 'config[url]=<PUBLIC_URL>/github' -f 'config[content_type]=json' -f "config[secret]=$SECRET"
```

Quote the `config[...]` args — zsh globs unquoted brackets ("no matches found"). A 422 usually
means a renamed repo that already has the hook under its old name.

### 6. Smoke test, then retire the crons

Create a question-only issue and delegate it: expect a thought within 10 s, issue → In Progress
→ Done, and a `💬 Answer` message. Then delegate one small real bug and watch it reach
`✅ Done` with user-facing Try-it steps. Only then pause any cron dispatch/merge routines
(pause, don't delete — rollback path).

## Gotchas learned the hard way

- **Restarting the receiver kills running `claude -p` sessions.** Check
  `pgrep -fl "claude -p"` first; the sweep re-gates interrupted PRs, but in-flight work is lost.
- **Never gate the repo that is the agent's own working copy** (e.g. the control-center repo
  `claude -p` runs in): the agent switching branches there wrecks the live checkout.
- **Never auto-merge contributor/dependabot PRs** — only PRs that reference an issue or are
  authored by `AGENT_OWNER_GITHUB`. Expect the first sweep to merge the owner's *stale* open PRs
  too; agree up front whether old PRs should merge or be closed.
- **Dedupe tracking issues** by PR URL (`agent-pr-issues.json`) — otherwise every gate run on an
  untracked PR files another issue.
- **Respond to Linear within 5 s and emit an activity within 10 s** or the session is marked
  unresponsive — do the work in a thread.
- **Delegate as the owner (API key), not as the app.** Re-delegating an issue already delegated
  to the agent needs clear → set to open a fresh session.
- **Security trade-off:** anyone in the Linear workspace who can delegate gets a shell running
  as the machine's user (`--dangerously-skip-permissions`). Run it on a box that holds only
  repos and deploy keys, or have the owner accept the exposure explicitly. Auto-mode safety
  classifiers may refuse to create the OAuth app/install for you; the owner can click those two
  steps in under a minute.

## Files written at runtime (`~/.config/linear/`)

`agent.log` (every event, gate verdict, delegation) · `agent-token.json` · `agent-sessions.json`
(Linear session → Claude session, for follow-up resume) · `agent-gated.json` (PR@sha → verdict,
the idempotency lock) · `agent-pr-issues.json` · `agent-resumed-blockers.json`.
