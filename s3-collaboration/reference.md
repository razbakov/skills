# S3 Collaboration Reference

Detailed patterns and glossary for human-agent-subagent collaboration, adapted from Sociocracy 3.0.

## Pattern Catalog (Agent-Adapted)

### Sense-Making & Decision-Making

| Pattern | Agent Application |
|---|---|
| **Navigate via Tension** | Agent monitors for issues (linter errors, test failures, inconsistencies) and surfaces them to the human. Human brings tensions via requests. |
| **Describe Organizational Drivers** | Document *why* before *what*. Format: "Given [current conditions], this leads to [effects], which matters because [relevance to purpose]." Save significant drivers to `docs/drivers/`. |
| **Determine Requirements** | Before proposing code/changes, clarify: What outcome is needed? What conditions must be met? Express as intended outcome + enabling conditions. |
| **Consent Decision-Making** | Default decision method. Agent proposes → human checks for objections → no objection = proceed. Not consensus (don't need agreement, just absence of reasoned objections). |
| **Test Arguments Qualify as Objections** | Is the concern about effectiveness, undesirable side-effects, or missed improvements? If yes = objection (must resolve). If no = concern (note it, proceed). |
| **Resolve Objections** | Amend the proposal to address the objection. Options: modify, add constraint, split into smaller experiment, add evaluation criteria. |
| **Proposal Forming** | For complex proposals: (1) collect input from affected parties, (2) use subagents to explore options in parallel, (3) synthesize into a coherent proposal, (4) present for consent. |
| **Evaluate and Evolve Policies** | Schedule reviews for skills, rules, and documented policies. Check: Is it still needed? Is it effective? Can it be improved? |

### Organizing Work

| Pattern | Agent Application |
|---|---|
| **Backlog** | Maintain todo lists (TodoWrite tool). Prioritize by driver significance. |
| **Prioritize Backlogs** | Order by: (1) urgency, (2) impact on purpose, (3) dependencies, (4) effort. Pull from top. |
| **Visualize Work** | Use todo lists with clear statuses: pending, in_progress, completed, cancelled. |
| **Pull System for Work** | Agent pulls next task when current one completes. Don't pile up work. |
| **Deliver Value Incrementally** | Make small, reviewable changes. Commit frequently. Show progress early. |
| **Limit Work in Progress** | One task in_progress at a time. Complete before starting new. Max 4 parallel subagents. |
| **Time-box Activities** | Set clear scope boundaries. If a task expands, stop and re-evaluate the requirement. |

### Building Organization Structure

| Pattern | Agent Application |
|---|---|
| **Role** | = Skill. A domain delegated to an agent capability. SKILL.md is the domain description. |
| **Circle** | = Human + agent + subagents working on a shared domain. The human sets governance, the agent handles operations. |
| **Helping Team** | = Subagents. They execute specific tasks but governance decisions stay with the main agent and human. |
| **Delegate Circle** | When multiple skills/domains need coordination, create a higher-level skill or workflow that coordinates between them. |
| **Double Linking** | Information flows both ways: agent reports results up to human, human provides context and constraints down to agent. |
| **Service Circle** | = Shared skills used across multiple projects (stored in `~/.cursor/skills/`). |
| **Open Team** | = Optional skills that agents can invoke when relevant but aren't required. |

### Defining Agreements

| Pattern | Agent Application |
|---|---|
| **Record Governance Decisions** | Save to `docs/logbook/YYYY-MM-DD-title.md`. Include: driver, requirement, decision, rationale, review date. |
| **Logbook** | The project's documentation system. All significant information accessible to all agents. |
| **Describe Deliverables** | Clearly state expected outputs with acceptance criteria before starting work. |
| **Define and Monitor Metrics** | Track: task completion rate, error introduction rate, review cycle time, skill reuse frequency. |

### Meeting Formats (Interaction Patterns)

| Pattern | Agent Application |
|---|---|
| **Governance Meeting** | = Conversation where human and agent discuss policies, skills, domain structure. Triggered by human or accumulated governance backlog items. |
| **Daily Standup** | = Start of session: agent reviews current state, pending items, blockers. |
| **Retrospective** | = End of major task: what worked, what didn't, what to change. Update skills and policies accordingly. |
| **Planning Meeting** | = Scoping session: break down a large request into prioritized backlog items. |

### Evolving the Organization

| Pattern | Agent Application |
|---|---|
| **Clarify and Develop Domains** | Regularly review and update skill descriptions. Are responsibilities clear? Are constraints appropriate? |
| **Enable Autonomy** | Give subagents maximum freedom within clear constraints. Avoid micro-managing prompts. |
| **Collaborate on Dependencies** | When skills depend on each other, document the dependency and coordinate through the main agent. |
| **Align Flow** | Move decisions close to where value is created. Subagents decide within their domain; escalate only when needed. |
| **Design Adaptable Systems** | Structure skills and rules so they can evolve without breaking existing workflows. |
| **Open Systems** | Use web search, external APIs, and community resources. Don't operate in isolation. |

### Peer Development

| Pattern | Agent Application |
|---|---|
| **Peer Review** | Agent reviews its own output against acceptance criteria. Use linter, tests, and validation. |
| **Development Plan** | Plan for improving a skill: what's working, what needs refinement, next experiments. |

### Enablers of Co-Creation

| Pattern | Agent Application |
|---|---|
| **Artful Participation** | Agent adapts its approach based on context. Formal for governance, concise for operations. |
| **Transparency** | Make all reasoning visible. Explain why, not just what. |
| **Invest in Ongoing Learning** | Capture learnings in skills and policies. What worked becomes a pattern. |

## Glossary (Key Terms)

| Term | Definition in Agent Context |
|---|---|
| **Driver** | A situation requiring response. User request, detected bug, linter error, or strategic need. |
| **Requirement** | Intended outcome + enabling conditions needed to address a driver. |
| **Domain** | A distinct area of responsibility. Defined by purpose, constraints, and deliverables. |
| **Policy** | A documented governance decision: skill, rule, strategy, or guideline. |
| **Objection** | A reasoned argument that proceeding would cause harm or miss an important improvement. |
| **Concern** | An assumption that can't yet be backed by evidence. Note it but don't block on it. |
| **Consent** | No objections remain. Not the same as agreement or enthusiasm. |
| **Governance** | Setting objectives and making policies. Skills, rules, domain definitions, strategies. |
| **Operations** | Day-to-day work within governance constraints. Code changes, file edits, commands. |
| **Delegation** | Granting authority for a domain. Human→agent, agent→subagent. Delegator retains accountability. |
| **Logbook** | System for recording all governance-relevant information. |
| **Backlog** | Prioritized list of work items (drivers, requirements, tasks). |
| **Circle** | Self-governing team attending to a domain. Human + agent + subagents. |
| **Role** | Domain delegated to an individual agent capability (= skill). |
| **Standard Constraint** | Rule affecting multiple domains. Stored in `.cursor/rules/`. |
| **Metric** | Quantifiable measure for tracking progress and evaluating effectiveness. |
| **Tension** | A felt sense that something needs attention. The starting point for all improvements. |
| **Waste** | Any activity that doesn't contribute to fulfilling purpose. Avoid. |

## Organizational Structures for Agent Systems

### Flat (Single Agent)
```
Human
  └── Agent (handles all domains)
```
Best for: Small projects, simple tasks, single-domain work.

### Hierarchical (Agent + Subagents)
```
Human
  └── Agent (governance + coordination)
        ├── Subagent: explore (sense-making)
        ├── Subagent: generalPurpose (implementation)
        └── Subagent: generalPurpose (testing)
```
Best for: Complex tasks with independent subtasks.

### Double-Linked (Agent + Skills)
```
Human ←→ Agent
             ├── Skill: code-review (domain: quality)
             ├── Skill: research (domain: knowledge)
             └── Skill: deployment (domain: delivery)
```
Best for: Recurring work across multiple domains. Skills provide institutional memory.

### Fractal (Multi-Project)
```
Human
  ├── Project A: Agent + Skills
  ├── Project B: Agent + Skills
  └── Shared Skills (~/.cursor/skills/)
        ├── analyze
        ├── research
        └── workflow
```
Best for: Multiple projects sharing common patterns and capabilities.

## Document Templates

### Driver Template (`docs/drivers/YYYY-MM-DD-title.md`)
```markdown
# [Title]

## Current Conditions
What is happening now that requires attention.

## Effects
What consequences this has (or will have) for the project.

## Relevance
Why this matters for fulfilling the project's purpose.

## Priority
High / Medium / Low

## Status
Open / Addressed / Resolved
```

### Domain Description Template (`docs/domains/domain-name.md`)
```markdown
# [Domain Name]

## Purpose (Primary Driver)
Why this domain exists.

## Key Responsibilities
- Responsibility 1
- Responsibility 2

## Deliverables
- What outputs are expected

## Constraints
- Boundaries and limitations

## Dependencies
- What this domain relies on

## Delegatee
Human / Agent / Skill name

## Metrics
How effectiveness is measured.

## Review Schedule
When to evaluate this domain.
```

### Policy Template (`docs/policies/policy-name.md`)
```markdown
# [Policy Name]

## Driver
Link to the driver this addresses.

## Requirement
Intended outcome + enabling conditions.

## Policy Description
What is decided. How things should be done.

## Rationale
Why this approach was chosen.

## Responsible
Who implements and monitors this policy.

## Review Date
When to evaluate this policy.

## Metrics
How to measure if this policy is effective.
```

### Logbook Entry Template (`docs/logbook/YYYY-MM-DD-title.md`)
```markdown
# [Decision Title]

**Date**: YYYY-MM-DD
**Participants**: Human, Agent

## Driver
What situation prompted this decision.

## Requirement
What outcome was needed.

## Decision
What was decided.

## Rationale
Why this was chosen over alternatives.

## Review Date
When to re-evaluate.
```
