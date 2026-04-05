# Org Coach

Design your organization's governance, roles, and coordination. Use when multiple people or AI agents need clear accountability and decision-making.

## Who is this for

- **Founders with AI agents** who need to delegate work to autonomous agents with clear boundaries, policies, and coordination rules.
- **Small teams** who want lightweight governance without bureaucracy — just enough structure to know who decides what.
- **Organizations adopting Sociocracy 3.0** who want a guided setup from primary driver through domains, roles, policies, and reviews.
- **Anyone scaling from solo to team** who needs to make implicit agreements explicit before things break.

## Why it matters

When one person does everything, governance is in their head. The moment you add a second person — or an AI agent — you need explicit answers to: Who decides what? What are the boundaries? How do we coordinate? How do we review?

Without governance, teams drift into confusion, duplicate work, or step on each other. With too much governance, they drown in process. This skill finds the balance: enough structure to be clear, minimal enough to stay fast.

## What it does

Four blocks: **Understand -> Map -> Govern -> Evolve.**

| Block | Phases | What you get |
|-------|--------|-------------|
| **Understand** | 0-2 | Primary driver, organization canvas, strategy, values |
| **Map** | 3-5b | Requirements mapping, domain descriptions, role descriptions, agent deployment |
| **Govern** | 6-11 | Policies, coordination, backlogs, work board, experiment design, review schedule |
| **Evolve** | ongoing | Decision-making, collaboration, retrospectives, structural adaptation |

Two modes:

- **Autopilot** (default) — you describe your situation, the coach asks 4 questions max, then generates governance artifacts with sensible defaults.
- **Guided** — you want control over each decision. The coach walks through S3 patterns and trade-offs, waiting for your input.

## Key concepts

- **Driver** — why the organization exists (observable conditions + their effect)
- **Domain** — an area of accountability delegated to a person or team
- **Role** — a domain held by one individual (human or AI agent)
- **Policy** — an explicit agreement that guides decisions within a domain
- **Delegation Canvas** — 11-field description of what a domain or role is accountable for

## Agent deployment

When creating AI agent roles (Phase 5b), the coach pulls domain knowledge from shared reusable agents:

| Agent | Domain knowledge |
|---|---|
| **product-lead** | JTBD, user journey, strategy, story map, backlog, BDD scenarios |
| **designer** | Brand guide, visual styles, design system mapping |
| **marketing-lead** | Campaign playbooks, content plans, channel strategy |
| **engineer** | Architecture, ADRs, BDD implementation |

Each agent gets S3 governance layered on top: pull system, tension-sensing, delivery via PR, evaluation against role metrics.

## Related

- **`/product-coach`** — Use when you need to discover what to build and validate it. Org-coach answers "how to organize", product-coach answers "what to build".
- **Shared agents** — Reusable agent definitions that org-coach wires into your organization with governance boundaries.

## How to install

```bash
claude install-skill https://github.com/razbakov/skills/tree/main/skills/org-coach
```

## How to use

Once installed, invoke in any supported AI IDE:

```
/org-coach
```

Then describe your organization or team.
