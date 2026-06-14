---
description: "Daily Digest — Chief-of-Staff role consolidates the six top-managers into one Telegram message to the Commander, instead of six. Implements the protocol from agent-proactivity.md."
user_invocable: true
---

# Daily Digest

Chief-of-Staff orchestrates the daily digest: collects review-ready slots from the
top-manager agents, consolidates into one message, sends to the Commander via Telegram,
saves to sessions.

Implements `~/Projects/ikigai-team/rules/agent-proactivity.md`. Read that for the
philosophy (cadence triggers, review-ready threshold, focus signal, digest discipline).
This skill is the executable contract.

## Trigger

- Cron / launchd fires this skill at the configured cadence (typically weekday 06:30).
- User says "run daily digest", "send digest", or invokes `/daily-digest`.

## Inputs from project context

Read these from the project's `CLAUDE.md` and agent files:

- **Manager roster** — agents in `.claude/agents/<name>.md`. The Chief-of-Staff role is
  whichever agent has "Daily Digest Protocol" in their file.
- **Each manager's Cadence section** — answers when they participate (some daily, some
  weekly, some opted-out).
- **Telegram bot token** — for sending. Look up via the project's documented sender
  (commonly `.bin/telegram-send.py --agent <chief>`).
- **Focus signal file** — typically `ops/focus.md`. Read most-recent entry.
- **Sessions directory** — typically `ops/sessions/`. Save digest there.

If any of these are missing, halt and tell the user what's needed — do not guess.

## Execution

### Phase 1 — Read context

1. Read the focus signal file. Most-recent line is current. If `open` / `clear` / absent,
   treat as no-focus.
2. Determine today's day-of-week. Some managers participate only on certain days
   (e.g., a Strategy role may only submit Mondays, a Personal-Coach role may opt out
   entirely).
3. List participating managers for this run by reading each manager's Cadence section.
   - "submits to daily digest" + day matches → in
   - "out-of-cycle" / opted out → skip
   - "weekly on <day>" + day matches → in this run only

### Phase 2 — Collect slots

For each participating manager:

1. Dispatch a slot-request to that manager's tmux session. Format:

```
Daily digest slot — <date> (<dow>)
Focus: <current focus or "open">

Per your Cadence section, scan your domain and reply with ONE of:
- A review-ready slot (≤ 5 lines) in the format from agent-protocols.md:
    Why: <KR>
    What: <one or two lines>
    Media: <link · screenshot · doc>
    Asking: <decision>. Default: <action> by <time> unless objection.
- "nothing to surface" if no decision/outcome/drift to report

Reply by <deadline, typically T-15 min before send>.
```

2. Track replies. After deadline, any silent manager → record "nothing to surface (no reply)".

### Phase 3 — Assemble + send

**Suppression gate — check this FIRST.** If every collected slot is "nothing to surface"
(including "no reply") — i.e. no manager reported a pending decision, a delivered outcome,
or a drift — then there is nothing review-ready. Do **NOT** send anything to Telegram.
Skip straight to Phase 4, record the silent cycle, and exit. A digest that is only
"nothing to surface" lines is exactly the noise this protocol exists to prevent
(`agent-proactivity.md`: "a daily silent cycle is a healthy cycle"). Only proceed to
formatting and sending when **at least one** slot carries real review-ready content.

Format the digest:

```
Daily digest — <date> · focus: <current focus or "open">

<Chief role> (<role-tag>): <slot>
<Manager 1> (<role-tag>): <slot>
<Manager 2> (<role-tag>): <slot>
...
```

- Each slot is what the manager replied with — do not paraphrase, do not edit beyond
  trimming whitespace.
- The Chief writes their own slot first, before assembling.

Send via the project's documented sender (e.g., `.bin/telegram-send.py --agent <chief>
--file <digest-file>`).

### Phase 4 — Save

Save to `<sessions-dir>/<date>-daily-digest.md`. Include:

- The sent message verbatim — or, if the Phase 3 suppression gate fired, a one-line
  "silent cycle — nothing to surface, no message sent" note instead
- A list of who participated and who was silent
- The current focus signal at send time

The cycle is always logged, even when nothing is sent — silence is recorded, not invisible.

### Phase 5 — Track replies (async)

After send, watch for Commander replies. Parse per `agent-proactivity.md`:

- `ok` / `ship it` / `yes` → consent now, route to originating manager
- `no` / `change X` / `do Y instead` → revise request, route to originating manager
- `pause` / `hold` → mark the open ask paused, log to sessions
- `focus: <theme>` → append to `ops/focus.md` with timestamp

If the Commander replies to a specific slot only, route that decision to that manager
without disturbing other open asks (their time-boxes age normally).

## Out-of-cycle bypass

This skill handles the routine daily flow only. Out-of-cycle event triggers (urgent
items: prod incident, festival contact mid-day, partnership emergency) bypass the digest
— the originating manager sends directly. Do NOT include those in the digest after the
fact; they had their own thread.

## Failure modes

- **Tmux session for a manager not running** — log and treat as "nothing to surface (no reply)". Do not block the digest.
- **Telegram send fails** — retry once. If still failing, save the digest to sessions and log the failure; do not silently drop.
- **No managers participating today** (e.g. weekend) — skip the run. Log "no participants today, skipping" to sessions and exit.

## Why a skill, not prose

Putting the protocol in a skill (instead of inline prose in the Chief's agent file)
makes the flow:

- **Deterministic** — the same steps fire every day, same shape every day
- **Testable** — manual `/daily-digest` invocation runs the same path as cron
- **Portable** — any project that imports the framework can adopt the skill
- **Revisable** — protocol updates land in this skill, not in N agent files
