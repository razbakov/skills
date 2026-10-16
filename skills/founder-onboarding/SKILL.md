---
name: founder-onboarding
description: "Guided first-run onboarding for a new founder, run as unhurried hospitality rather than a timed form — it paces to the person, never to a clock. Stage 1 is a coaching session that sets the person up as their own personal operating center: a person-as-organization 'ikigai' command-center founded via org-coach (their purpose, life areas, and a small team). Then a bounded hand-off menu: define an AI-first organization (org-coach), build a product (product-coach), or join someone else's org/project. Use this whenever someone is new to the Ikigai Team framework or being set up from scratch — phrases like 'onboard me', 'onboard founder <name>', 'set me up', 'I'm new here', 'get me started', 'help me set up my ikigai' — even when they don't say 'onboarding'. Do NOT use this for someone who already has their personal center and just wants to found one more org or project; point them to org-coach or product-coach directly instead."
user_invocable: true
---

# Founder Onboarding

Bring a new founder from nothing to a working personal operating center, then hand them a clear menu of what to do next. Two things make this work: it feels **controlled, not endless** (the founder always knows where they are and that they can pause), and it feels like being **hosted by someone who cares**, not processed by a wizard. Both matter equally. A founder's first experience of the system *is* their impression of the whole system.

## Where this runs (multi-tenant workspace layout)

Each founder gets their own namespaced workspace — a mirror of the framework's `~/Orgs` / `~/Projects` layout, under their name. This is what lets many founders coexist.

- **Workspace root:** `~/Workspaces/<Name>/` (the `<Name>` namespace is the whole point — it isolates this founder from every other).
- **Personal operating center:** `~/Workspaces/<Name>/Orgs/ikigai/` — always named `ikigai`. This is the person-as-organization. It `@`-imports the framework and adds their identity + life-area domains. (It is to the founder what `~/Orgs/ikigai` is to the person who runs the platform.)
- **Their organizations:** `~/Workspaces/<Name>/Orgs/<OrgName>/`
- **Their projects:** `~/Workspaces/<Name>/Projects/<project-name>/`

Everything this skill creates lives under that one `<Name>` root.

## How this skill is usually launched

Often an **onboarder agent** in a Telegram group named "**<Name>'s Ikigai**" runs this skill: the platform operator says "Onboard founder <Name>", which scaffolds the workspace and the group, the operator adds the real person and introduces them, and the agent takes over here. The skill also works when run directly by a founder in their own workspace. Either way, the founder is the "you" being onboarded.

## Trigger

User says "onboard me", "set me up", "I'm new", "get me started", "help me begin", or an operator says "onboard founder <name>", or `/founder-onboarding`.

## Two principles that govern every message

### 1. Predictable — the founder is never lost

- **Show the map up front, once.** Before anything else, show the three-stage map and that onboarding itself is only Stage 1. The founder sees the finish line before they start. Do **not** quote a duration you are guessing — see "Time is measured, not guessed" below.
- **Stamp every step with position by count, not by clock.** Begin each step with an honest counter: `Stage 1 of 3 · step 2 of ~5`. Counts are truthful; invented minutes ("~10 min left") are not — never use them.
- **Autopilot only.** Invoke the child coaches in their **autopilot** mode (max 4 discovery questions, then generate with sensible defaults). Do not let them switch to "guided" during onboarding — capture any strong opinion as a note for the one tweak pass and keep moving. Guided mode is for later, invoked deliberately.
- **One question at a time.** Ask, wait, move on. Never dump a list of questions in one message.
- **Checkpoint at every stage boundary.** End each stage with `✓ <what was created>` + a one-line preview + "continue, or pause here?" The founder can always stop.
- **Write to disk each step** so the flow is fully resumable (see Resume detection). Nothing lives only in chat.
- **Hard end.** Onboarding is Stage 1 only. It ends with an explicit "✓ you're set up" screen and the Stage 2 menu — never an automatic continuation that makes the flow feel infinite.

### 2. Caring — the founder is a guest, not a ticket

The person being onboarded may be nervous, new to this, or doing something quietly meaningful (Stage 1 asks them to articulate their purpose — that is not small talk). Host them accordingly:

- **Pace to the person, not to a timer.** Never rush a step to "stay on time." If their answers get short or flat, slow down, reflect back what you heard, and ask if they want a breather. A pause is a success, not a failure.
- **Mark the weight of the ikigai step.** After the purpose/driver dig in Stage 1 — the heaviest moment — pause and check in on *them* ("that's a real question — how did that land?") before moving on. Acknowledge what they said in their own words; don't just file it.
- **Celebrate the finish.** The ✓ at the end of Stage 1 is a genuine milestone (they now exist as an operating center). Name it warmly.
- **Adapt to the signal, not the script.** If they're clearly energized and fast, don't pad. If they're overwhelmed, one step and a rest is plenty for today — the resume logic will pick them up.

## Time is measured, not guessed

Guessed durations are dishonest and make onboarding feel like a conveyor belt. Instead, **measure**:

1. At the start of Stage 0, record the clock. Create `~/Workspaces/<Name>/Orgs/ikigai/ops/onboarding/state.json` with `started_at` (ISO 8601, from `date`), and append a `{step, at}` entry each time a step completes. This is also the resume cursor.
2. **Present progress as counts** (`step 2 of ~5`), and only ever mention *elapsed* time when it's truthful and kind — read from `started_at`, e.g. "we've been at this about ten minutes, no rush." Never state time *remaining*.
3. If the founder asks "how long will this take?", answer honestly from data if the platform has it (past founders' recorded durations), otherwise: "it's paced to you, not a clock — most people do Stage 1 in one sitting, and you can stop any time."
4. At the hard end, write total and per-stage durations to `ops/onboarding/timing.json`. Across many founders these recorded durations are what turn "guessed" estimates into real, measured ones — so the platform can one day say a true number instead of inventing one.

## Prerequisites

This skill orchestrates companion skills; they should be installed in the environment:

- `org-coach` — founds an organization (used here for the person, and later for real orgs)
- `product-coach` — discovers and frames a product/project
- `project-start` — scaffolds a project's docs (README → journey → story map)
- `envoy-connect` — connects a Telegram chat to an agent (used by the "join" path)

If one is missing when its stage is reached, tell the founder which to install from the platform's skills repo (e.g. `claude install-skill <skills-repo>/skills/<name>`) and continue with what's available rather than failing the whole flow.

## Resume detection (run silently on start)

Decide where the founder is before showing anything, using their personal center at `~/Workspaces/<Name>/Orgs/ikigai/`:

- **No workspace yet** → start at **Stage 0**.
- **Workspace exists but unfounded** (no `logbook/` and no `## Structure` section in its `CLAUDE.md`) → resume at **Stage 1**, reading `ops/onboarding/state.json` for the last completed step.
- **Workspace exists and is founded** → onboarding is already done. Skip to the **Stage 2 menu** and say so ("you're already set up — here's what you can do next").

---

# Stage 0 — Welcome & map

**Step 0.1 — Start the clock and show the map.** Record `started_at` (above), then greet warmly and show the whole journey so the end is visible from the start:

```
Welcome — glad you're here. Here's the whole path, and you're in control the whole way:

  Stage 1 · Set yourself up            ← this is onboarding
           a coaching session that turns "you" into your own operating
           center: your purpose, your life areas, a small team to run it

  ✓ You're set up.

  Stage 2 · Then, when you're ready, pick one:
           • define an organization (its vision, mission, values)
           • build a product
           • join someone else's org or project

Stop after any step and pick up exactly where you left off. No clock — we go at your pace.
```

**Step 0.2 — Confirm their name.** Ask what to call them. This names their workspace (`~/Workspaces/<Name>/`). Confirm it back in one line, then: "Ready to start Stage 1 — or any questions first?"

---

# Stage 1 — Set yourself up (the person-as-organization session)

The heart of onboarding, and it mirrors how a mature command-center is built: **the founder is treated as their own organization** — both the Commander and the org the team serves. Run `org-coach` in autopilot, with the translation below so the questions land as a life, not a company.

**Step 1.1 — Set the frame (warmly, 1–2 lines).** "For the next little while I'll help you set yourself up the way a founder sets up their own operating center — your purpose, the areas of your life, and a small team to run it. A few questions, then I'll draft it and you tweak. There's no wrong answer here."

**Step 1.2 — Run the founding.** Invoke: `//org-coach` in **autopilot**, targeting `~/Workspaces/<Name>/Orgs/ikigai/`, applying this translation when reading its phases:

### Person-as-organization translation

| org-coach asks about… | For a founder, read it as… |
|---|---|
| Primary driver (conditions → effect → relevance) | Their life situation now and why they're organizing it — the tension or opportunity they get up for. Dig past "I want to be productive" to the real situation, as org-coach digs past "I want to build X". |
| Organization canvas | Their life context: what they're responsible for, their resources (time, skills, money), constraints, who they serve. |
| Domains | **Life areas**, the founder's own — e.g. health, relationships, work, money, learning, purpose. Let them name their own; impose no fixed wheel. These become `domains/`. |
| Roles | How they want to show up in each area. |
| Agents (`.claude/agents/`) | Their personal team. Keep it light: a **Coordinator** (always), plus the framework's core team by import. Do not over-generate bespoke agents during onboarding — they can grow the team later. |
| Workspace | `~/Workspaces/<Name>/Orgs/ikigai/` — a `CLAUDE.md` that `@`-imports the framework, then their identity as Commander + their life-area domains. |

Keep org-coach to its 4-questions-max autopilot discovery. Translate its templates into life terms. Write files as answers arrive.

**Step 1.3 — Check in, then the one tweak pass.** First, attend to the person (Principle 2): acknowledge the purpose they named, in their words, and ask how it landed. Then show a compact summary — driver in 2–3 sentences, life areas as a list, team (Coordinator + core team) — and ask once: "anything you'd change before we lock it in?" Apply edits; capture bigger reshapes as notes in their logbook rather than opening a second round.

**Step 1.4 — Checkpoint / hard end of onboarding.** Record the finish time to `timing.json`, then:

```
✓ You're set up. Your operating center lives at ~/Workspaces/<Name>/Orgs/ikigai/.
  • Purpose: <one line, their words>
  • Life areas: <list>
  • Team: a Coordinator + your core team

That's onboarding done — and that purpose is now something your team can actually serve.
Want to keep going and set up your work, or stop here and come back anytime?
```

If they stop: confirm they can return any time (it resumes at the Stage 2 menu). If they continue: Stage 2.

---

# Stage 2 — The hand-off menu (each option is one bounded action)

Onboarding is over. This is a **menu**, not a pipeline — present the options, let the founder pick one, run it, then return here (or exit). Each option ends in a concrete artifact, so nothing feels open-ended.

```
Pick one — or we're done for today:
  A) Define an organization    — vision, mission, values of something with people/partners/events
  B) Build a product           — software to build
  C) Join an org or project    — plug into something someone else already runs
  D) Done for now
```

If unsure between A and B, apply the framework's test: *"Do other people care about this beyond the code?"* No → product (B). Yes → organization (A).

### A) Define an organization

Invoke: `//org-coach` in autopilot, targeting a **new** `~/Workspaces/<Name>/Orgs/<OrgName>/` (not the founder's personal `ikigai`). This founds an AI-first organization — its vision, mission, values, domains, and fresh org-specific agents (never reuse the personal team). Checkpoint, then return to the menu.

### B) Build a product

1. Invoke: `//product-coach` in autopilot — discover the real problem, frame a testable hypothesis, scaffold `~/Workspaces/<Name>/Projects/<project-name>/`.
2. Then offer (don't force): `//project-start` to lay down the docs spine (README → user journey → story map → architecture).

Checkpoint with the created path(s), then return to the menu.

### C) Join an org or project

The collaborator path — joining something **someone else owns**. Access is granted by the owner, not self-served. Two moves:

1. **Get the repo on disk.** Help the founder clone the shared org/project repo into `~/Workspaces/<Name>/Orgs/<OrgName>/` or `~/Workspaces/<Name>/Projects/<project-name>/`. If they lack access, give them the exact ask to send the owner (repo read access + clone URL).
2. **Connect for live collaboration.** Invoke: `//envoy-connect` to wire the founder into the owner's Telegram group for that org/project. State clearly: the **owner** must add them and grant them an active voice (the owner runs the per-person allow step) — until then the founder is a read-only observer.

Checkpoint with what's connected, then return to the menu.

### D) Done for now

Close warmly: a one-line recap of what exists now (their personal `ikigai` + anything created this session) and how to come back (`/founder-onboarding` resumes at this menu; the coaches run directly any time, in guided mode if they now want full control).

---

## Design notes (for maintainers)

- **Why autopilot-only during onboarding:** the failure this skill prevents is an open-ended founding that wanders and surprises the founder. Guided mode is powerful but unbounded; it belongs *after* onboarding.
- **Why onboarding = personal `ikigai` only:** a founder needs a self before a company. Everything in Stage 2 is optional and bounded, so the required part stays short and humane.
- **Why measured, not guessed:** quoting invented durations erodes trust and makes a caring session feel mechanical. Recording real durations per founder is what lets the platform eventually state true estimates.
- **Multi-tenancy & its limit:** `~/Workspaces/<Name>/` namespaces founders on one host. That is enough to prove the experience, but true isolation (per-founder containers/cloud) is the seam a production platform must replace it with — each founder's agent still runs a shell, and one shared host is a blast-radius and privacy limit, not a scaling plan.
- **Config-free:** no hardcoded paths beyond the `~/Workspaces/<Name>/`, `~/Orgs`, `~/Projects` conventions, no chat IDs, no instance-specific agent names. Names are gathered at runtime.
