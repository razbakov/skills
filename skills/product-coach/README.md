# Product Coach

Discover the right problem, validate the solution, then build with confidence. Use when starting something new, unsure what to build, or onboarding to an existing workspace.

## Who is this for

- **Founders and solopreneurs** starting a new product or side project and need structured thinking before writing code.
- **People doing personal development** who want a "life OS" — mission, vision, OKRs, and portfolio management across multiple projects.
- **Product managers and designers** who want enterprise-grade documentation (strategy, JTBD, user journey, story map, backlog, BDD scenarios) generated with sensible defaults.
- **Anyone onboarding to an existing workspace** who needs to understand what's done, what's missing, and what to do next.

## Why it matters

Most projects fail not because the code is bad, but because the team built the wrong thing. This skill applies design sprint methodology (Jake Knapp / Google Ventures) to validate ideas before committing. AI makes this nearly free — what used to take a team 5 days now takes hours.

Without structure, side projects drift. With structure but no coach, you spend more time on process than progress. This skill balances both: it brings the rigor while you bring the intent.

## What it does

Three blocks: **Understand -> Validate -> Commit.**

| Block | Phases | What you get |
|-------|--------|-------------|
| **Understand** | 0-4 | Mission, vision, hypothesis, product strategy, JTBD research, user journey |
| **Validate** | 5-7 | 3 sketched approaches, clickable prototype, real user feedback |
| **Commit** | 8-15 | Dispatches specialized agents (product-lead, designer, marketing-lead, engineer) |

Two modes:

- **Autopilot** (default) — you say "I want X", the coach asks 4 questions max, then generates everything with sensible defaults.
- **Guided** — you want control over each decision. The coach presents trade-offs and waits for input.

## Related

- **`/org-coach`** — Use when you need governance, roles, and coordination for multiple people or AI agents. Product-coach answers "what to build", org-coach answers "how to organize".
- **Shared agents** — The Commit block dispatches to reusable agents (`product-lead`, `designer`, `marketing-lead`, `engineer`) that carry domain knowledge and templates.

## How to install

```bash
claude install-skill https://github.com/razbakov/skills/tree/main/skills/product-coach
```

## How to use

Once installed, invoke in any supported AI IDE:

```
/product-coach
```

Then describe your idea.
