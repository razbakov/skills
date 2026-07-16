---
name: handoff
description: Get an agent past a browser/UI wall it can't (or must not) cross on its own — a login-gated dashboard, a CAPTCHA, a 2FA prompt, an API that keeps rejecting the write, or an irreversible click that policy says a human must make. This skill is an ESCALATION LADDER, not a first move: it tells you to try the automated browser surfaces FIRST (Chrome-in-Claude, computer-use, an autonomous browser sub-agent) and only fall back to the Handoff app — a wrapper browser that hands the human a checklist beside the live page and reports a machine-readable "done" back — when those genuinely hit a wall. Reach for it on "I'm blocked and need a human to do X in the browser", "add this DNS record / approve this deploy / accept these terms and tell me when done", "the API 422'd, over to the human", "I can't get past this login/CAPTCHA/2FA", or any moment you'd otherwise paste a paragraph of manual steps and hope the human follows them. It auto-installs the Handoff app on first use.
compatibility: macOS with Node + npm. The fallback tool is the Handoff Electron app (github.com/razbakov/handoff), auto-installed on first use. The preferred tiers need their own surfaces available (claude-in-chrome MCP, computer-use MCP, or a browser sub-agent); the skill degrades gracefully — if no automated surface exists, go straight to Handoff.
---

<role>
You are an operator who gets a task done through the cheapest surface that can
actually do it, and escalates only when blocked. A human's attention is the most
expensive resource in the loop — you spend it last, and when you do, you spend it
well: a clear checklist beside the live page, not a wall of instructions in chat.
</role>

## The core rule

**Handoff is the backup, never the opening move.** Automated browser control is
faster, doesn't interrupt the human, and handles the overwhelming majority of UI
work. Only escalate to a human handoff when you hit a genuine wall. Walk the ladder
top-to-bottom and stop at the first tier that can do the job.

## The escalation ladder

### Tier 0 — Is it even a browser task? Try a direct API / CLI / MCP first.
Before any browser at all: is there a `gh`, `gog`, `netlify`, `vercel`, a dedicated
MCP (Linear, Slack, Gmail, Calendar…), or a REST endpoint? These are faster and
more reliable than any UI. Only when there is no programmatic path — or it fails
(auth, a 422 like the org.wedance.vip DNS case, a missing scope) — move to a browser.

### Tier 1 — Automated browser surfaces (PREFERRED — try these before Handoff)
Drive the UI yourself. In rough order of preference:
- **Chrome-in-Claude** (`mcp__claude-in-chrome__*`) — the human's real, already-
  authenticated Chrome. Best when they're already logged into the site. DOM-aware.
- **An autonomous browser sub-agent** — dispatch an agent to complete the flow in a
  browser context end-to-end when the steps are well-defined.
- **computer-use** (`mcp__computer-use__*`) — native desktop control, for native
  apps or when the Chrome surface can't reach it.

If one of these completes the task, **you are done — do not open Handoff.**

### Tier 2 — Handoff (BACKUP — only when Tier 1 hits a wall)
Escalate to a guided human handoff when, and only when, one of these is true:
- **The wall is a human-only gate the automated surface can't pass** — a login you
  can't complete, a CAPTCHA/bot-check, a 2FA/OTP prompt, an SSO consent screen.
- **Policy forbids the agent from doing it** — entering passwords/payment/credentials,
  creating accounts, changing permissions or security settings, accepting terms,
  granting OAuth, or clicking an irreversible Send/Delete/Publish/Pay. (See the
  action-boundary rules — these must be done by the human regardless of tool.)
- **Every automated path failed** — API errored AND the UI is unreachable or the
  automated surface can't drive it (element not found, headless-blocked, flaky).
- **It needs the human's eyes or judgment** — "does this look right before I ship it?"

If you'd otherwise type "please go to X, click Y, then Z and tell me when done" —
that is the signal. Send a Handoff instead: same instructions, but beside the live
page, with a Proceed button that reports back.

## Using Handoff (the backup)

### 1. Make sure it's installed (auto-install on first use)
```bash
DIR="${HANDOFF_DIR:-$HOME/Projects/handoff}"   # override with HANDOFF_DIR if you keep it elsewhere
if ! command -v handoff >/dev/null 2>&1; then
  [ -d "$DIR" ] || git clone https://github.com/razbakov/handoff "$DIR" || {
    echo "Handoff not installed and clone failed. Install it manually, then rerun." >&2
    exit 1
  }
  ( cd "$DIR" && npm install && npm link )
fi
command -v handoff >/dev/null 2>&1 || { echo "handoff still not on PATH after install" >&2; exit 1; }
```
Requires Node + npm. `npm link` puts the `handoff` command on PATH. Idempotent —
safe to run every time; it no-ops once installed. It fails **loudly** rather than
silently if neither a local checkout nor the repo is reachable, so you never think
a handoff was sent when the tool isn't there.

### 2. Hand off in one blocking call
Build the spec inline from flags — you never author JSON:
```bash
result=$(handoff do \
  --title "<short spoken title>" \
  --url   "<the page the human should land on>" \
  --intro "<one line: why this matters / why it's manual>" \
  --note  "<the exact values or the one thing that's easy to get wrong>" \
  --step  "<step 1>" --step "<step 2>" --step "<step 3>" \
  --timeout 1800)
code=$?   # 0 = done, 2 = blocked, 3 = timeout
```
`handoff do` delivers the task, blocks until the human resolves it, then prints the
result JSON — `{status, notes, steps, completedAt}` — and exits with the code above.

**Delivery surface (default: Telegram).** The human should do the step in their OWN
browser — real cookies, 1Password/Bitwarden, passkeys, and it works on their phone —
not an isolated embedded one. So by default the handoff arrives as a **Telegram
message** with an "Open the page ↗" link button and **✓ Done / ⚠ Blocked** buttons;
they tap the link, do it where they're already logged in, and tap a button. Replying
to the message adds a note back to the agent (so "Blocked" can say *why*). Requires
`~/.config/telegram/.env` (`ENVOY_BOT_TOKEN` + the human's chat id) and the bot's
`ho:` handler — see the repo's `telegram/` dir. Use `--via app` to force the
self-contained Electron window instead (embedded browser + checklist queue, but a
session isolated from the real browser, desktop-only).

### 3. Act on the result
- `0` **done** → verify the effect programmatically if you can (e.g. re-check DNS,
  re-hit the API), then continue.
- `2` **blocked** → read `.notes` (the human's message back), fix what they flagged,
  and either retry an automated tier or send a corrected handoff.
- `3` **timeout** → the human hasn't gotten to it; ping them (Telegram) or leave it
  queued and move on to other work.

### Queue several at once
Multiple `handoff open` calls stack in the **same** window (single-instance FIFO
queue, `+N waiting` badge); the human clears them one by one and the app auto-advances.
Use `open` + `wait` to fan out and collect:
```bash
handoff open a.json; handoff open b.json      # both queue in one window
handoff wait a.json; handoff wait b.json      # block on each in turn
```
`handoff list` shows what's pending vs. resolved. `handoff new …` writes a spec file
without opening it.

## What makes a good handoff spec

- **Title = a short spoken handle** ("Add the DNS record", "Approve the deploy"), not
  a sentence.
- **`--url` lands them exactly where the work is** — the specific dashboard/zone/page,
  not the site root.
- **`--note` carries the one thing that's easy to fumble** — the exact record values,
  the field that must match, the toggle that's non-obvious.
- **Steps are checkable and literal** — "Type = `A`, Name = `org`, Value = `76.76.21.21`",
  not "configure the record". Backtick inline code renders.
- **Say why it's manual** in `--intro` so the human trusts the ask ("the API kept
  returning 422, so this is a 60-second manual step").

## Pitfalls

- **Don't open Handoff first.** If you reach for it before trying Tier 0/1, you've
  spent the human's attention on something an MCP could have done silently. Walk the
  ladder.
- **Don't use Handoff to launder a prohibited action into "the agent did it."** The
  human performs the gated action in the app; you never enter their password/payment
  yourself. Handoff is the *right* way to route those — it just doesn't change who acts.
- **Don't paste manual steps into chat as the fallback.** That's exactly what Handoff
  replaces — chat instructions get lost; a checklist beside the page with a Proceed
  button doesn't.
- **Verify after done.** `status: done` is the human's claim; confirm the effect
  programmatically when a check exists (the DNS resolves, the domain is Valid, the API
  now succeeds) before reporting the task complete.
- **Timeout on unattended runs.** In cron/headless contexts a human may never click;
  always pass `--timeout` and handle exit code `3` rather than blocking forever.

## Integration points

- **Fallback tool:** the Handoff app (`handoff` CLI) — github.com/razbakov/handoff.
- **Preferred surfaces:** claude-in-chrome MCP, computer-use MCP, browser sub-agents.
- **Notify:** on timeout or when a handoff is queued for later, ping the human on their
  realtime channel (e.g. Telegram) with the task title so the queued window isn't missed.
