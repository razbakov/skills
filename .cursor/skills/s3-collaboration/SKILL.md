---
name: s3-collaboration
description: Orchestrate human-agent-subagent collaboration using Sociocracy 3.0 patterns. Defines governance, domains, roles, drivers, and policies for AI-assisted projects. Use when organizing work between humans and agents, delegating to subagents, creating skills, defining project structure, or when the user mentions S3, sociocracy, governance, domains, drivers, or collaboration patterns.
---

# S3 Collaboration Framework

Adapt Sociocracy 3.0 for human-agent-subagent collaboration. S3 provides patterns for distributed governance, consent-based decisions, and domain-driven work organization -- all directly applicable to how humans and AI agents collaborate.

## Core Concept Mapping

| S3 Concept | AI Collaboration Equivalent |
|---|---|
| Organization | The project/workspace |
| Purpose | Project's primary driver (north star) |
| Domain | Area of responsibility delegated to a human, agent, or subagent |
| Circle | A team: human + main agent + subagents working on a domain |
| Role | Specific responsibility assigned to a subagent or skill |
| Driver | Situation requiring response (user request, system event, detected issue) |
| Requirement | What needs to be fulfilled (task, todo, issue) |
| Governance | Policies in skills, rules, and documentation |
| Operations | Day-to-day agent actions (code edits, shell commands, file ops) |
| Policy | Documented decisions: skills, rules, templates, strategies |
| Objection | Agent raises concerns about feasibility, risks, or side-effects |
| Consent | User approves proposal (no objection = proceed) |
| Logbook | Project docs, decision records, changelogs |
| Backlog | Todo lists, GitHub issues, governance backlogs |
| Delegation | Human → agent → subagent chain of responsibility |
| Delegator | Human (for agent), agent (for subagents) |
| Delegatee | Agent or subagent receiving delegation |
| Metric | Measurable indicator of progress or effectiveness |

## Seven Principles (Adapted for Agents)

1. **Effectiveness** -- Devote tokens and compute only to what advances project objectives. Avoid waste.
2. **Consent** -- Proceed unless the user raises an objection. Proactively surface concerns before acting on risky changes.
3. **Empiricism** -- Test assumptions through small experiments. Treat all policies as provisional. Validate with real outcomes.
4. **Continuous Improvement** -- After each cycle, review outcomes and refine processes, skills, and policies.
5. **Equivalence** -- Involve affected parties (human, agent, subagents) in decisions that impact their domains.
6. **Transparency** -- Record all governance decisions. Make information accessible. Use logbooks and backlogs.
7. **Accountability** -- Each domain has a clear owner. Agents report outcomes. Subagents return results to the delegating agent.

## Project Structure (File Organization)

```
project/
├── .cursor/
│   ├── rules/                    # Standard Constraints (org-wide policies)
│   │   ├── coding-standards.mdc  # How code should be written
│   │   ├── git-workflow.mdc      # Version control policies
│   │   └── review-process.mdc    # How changes are reviewed
│   └── skills/                   # Roles (domain-specific capabilities)
│       ├── skill-name/
│       │   ├── SKILL.md          # Domain description + instructions
│       │   ├── reference.md      # Detailed knowledge
│       │   └── scripts/          # Operational tools
│       └── ...
├── docs/
│   ├── drivers/                  # Organizational Drivers
│   │   └── YYYY-MM-DD-title.md   # Why: situation + effects
│   ├── domains/                  # Domain Descriptions
│   │   └── domain-name.md        # Purpose, responsibilities, constraints
│   ├── policies/                 # Governance Decisions
│   │   └── policy-name.md        # Strategy, guidelines, rules
│   └── logbook/                  # Decision Records
│       └── YYYY-MM-DD-title.md   # What was decided, by whom, why
├── backlog/                      # Operations Backlog (or use GitHub Issues)
│   └── ...
└── README.md                     # Overall Domain description
```

### What Goes Where

| Content Type | Location | S3 Equivalent | Owner |
|---|---|---|---|
| Project purpose & strategy | `README.md` | Overall Domain | Human |
| Why something needs doing | `docs/drivers/` | Organizational Driver | Human / Agent |
| Who is responsible for what | `docs/domains/` | Domain Description | Human |
| How things should be done | `docs/policies/` | Policy | Human + Agent |
| What was decided and why | `docs/logbook/` | Logbook | Agent |
| Reusable agent capabilities | `.cursor/skills/` | Role | Human + Agent |
| Cross-cutting rules | `.cursor/rules/` | Standard Constraint | Human |
| Work items to complete | `backlog/` or Issues | Operations Backlog | Agent |

## Delegation Model

### Human → Agent (Primary Delegation)

The human is the **delegator**. The agent is the **delegatee**. The human:
- Defines the **primary driver** (what situation needs responding to)
- Sets **constraints** (budget, scope, technologies, style)
- Retains **overall accountability** (approves/rejects outcomes)

The agent:
- Determines the **requirement** (what's needed to address the driver)
- Proposes **interventions** (code changes, new files, refactors)
- Operates within the domain's constraints
- Surfaces **objections** when the proposed approach has risks

### Agent → Subagent (Secondary Delegation)

The agent is the **delegator**. Subagents are **delegatees**. The agent:
- Describes the **domain** clearly in the Task prompt (purpose, constraints, expected output)
- Chooses the right **subagent type** based on the domain:
  - `explore` → Sense-making (investigate, search, understand)
  - `generalPurpose` → Operations (implement, research, execute)
- Sets **constraints** (readonly, model selection, scope)
- Evaluates subagent results against the requirement

**When to delegate to subagents:**
- The task has **independent subtasks** that can run in parallel (max 4)
- The task requires **exploring** an unfamiliar area of the codebase
- The work involves **multiple domains** that don't depend on each other
- The complexity exceeds what a single agent can hold in context

**When NOT to delegate:**
- Simple, well-scoped tasks (1-3 steps)
- Tasks requiring tight sequential coordination
- Tasks where context from prior steps is critical

## Governance Process (Decision-Making)

Follow this process for significant decisions:

```
1. Navigate via Tension
   → Human or agent notices something needs attention

2. Describe the Driver
   → Document: current conditions + effects on the organization
   → Save to docs/drivers/ if significant

3. Determine Requirement
   → What outcome is needed? What conditions must be met?
   → Express as: intended outcome + enabling conditions

4. Form Proposal
   → Agent proposes an intervention (code, policy, structure change)
   → For complex proposals: use subagents to explore options in parallel

5. Consent Decision
   → Present proposal to human
   → Human checks for objections (risks, side-effects, missed improvements)
   → No objection = proceed
   → Objection found = resolve it (amend proposal) and re-check

6. Implement & Evaluate
   → Execute the intervention
   → Record the decision in docs/logbook/
   → Schedule review (add to governance backlog)
```

### When to Use Formal Governance

Use the full governance process when:
- Creating or modifying a **skill** (it's a role/domain definition)
- Defining a **new domain** or restructuring responsibilities
- The change affects **multiple domains** or the overall project
- The decision has **long-term consequences** or is hard to reverse
- Creating **standard constraints** (rules that apply across the project)

Skip formal governance for:
- Routine code changes within an established domain
- Bug fixes following existing policies
- Operational tasks with clear acceptance criteria

## When to Create a Skill

A **skill** is an S3 **role** with a clear domain description. Create a new skill when:

1. A **recurring pattern** emerges -- the same type of work keeps appearing
2. **Specialized knowledge** is needed that the agent wouldn't know by default
3. A **domain** needs clear boundaries, constraints, and operating procedures
4. Work needs to be **delegated consistently** to subagents with specific instructions
5. A **policy** is complex enough to warrant its own documented process

### Skill as Domain Description

Structure each skill's SKILL.md to mirror an S3 domain description:

```markdown
---
name: skill-name
description: What + When (third person)
---

# Skill Name

## Purpose (Primary Driver)
Why this skill exists. What situation it addresses.

## Key Responsibilities
What the agent must do when this skill is activated.

## Constraints
Boundaries, rules, and limitations.

## Deliverables
What outputs are expected.

## Dependencies
What other skills, tools, or information this skill relies on.

## Metrics
How to evaluate if the skill is working effectively.

## Review Schedule
When to evaluate and evolve this skill.
```

## Evaluate and Evolve

Treat all policies, skills, and structures as **provisional**:

- **After each significant task**: Quick retrospective -- what worked? what didn't?
- **When outcomes diverge from intent**: Revisit the driver and requirement
- **When the environment changes**: New tools, new team members, new constraints
- **On scheduled review dates**: Evaluate metrics, resolve accumulated objections

## Additional Resources

- For detailed S3 pattern descriptions and glossary, see [reference.md](reference.md)
- For concrete workflow examples, see [examples.md](examples.md)
