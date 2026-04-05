# Phase 3: Requirements Mapping

Guide the user through a lightweight Requirements Mapping workshop:

**Step 1: Identify actors**
Ask: "Who can help, benefit, or be harmed by this organization?" (customers, team members, partners, competitors, regulators, etc.)

**Step 2: Determine needs**
For each actor group, capture needs using the Requirement Card format:
- "They/We need ___ so that ___"

**Step 3: Cluster into domains**
Group similar actors or similar needs together. Each cluster becomes a candidate domain.

**Step 4: Name and confirm**
Present the suggested domains to the user. Ask them to confirm, merge, split, or rename before creating anything.

**Rules:**
- In autopilot: Suggest 2-3 domains based on context, ask user to confirm.
- In guided: Walk through each actor, each need, then facilitate clustering together.
- Don't create domain directories until the user confirms the domain list.

Once confirmed, create requirement cards using → `templates/requirement-card.md`. Place them in the logbook's requirements directory per CLAUDE.md structure section.

# Phase 4: Domain Descriptions

For each confirmed domain, create a directory under the domains path (per CLAUDE.md structure section) with a domain description.

**In autopilot:** Draft the description from context, ask user to review.
**In guided:** Walk through each Delegation Canvas field with the user.

Delegation Canvas fields:
1. Purpose (primary driver + requirement for this domain)
2. Key responsibilities
3. Customers and deliverables
4. Dependencies
5. External constraints
6. Key challenges
7. Key resources
8. Delegator responsibilities
9. Competencies, qualities, and skills needed
10. Key metrics and monitoring
11. Evaluation schedule

Create the domain description using → `templates/domain-description.md`. Place it in the domain's directory per CLAUDE.md structure section.

Also create empty subdirectories for each domain:
- `Governance/Backlog/`
- `Governance/Policies/`
- `Governance/Meeting_Records/`
- `Operations/Backlog/`
- `Operations/In_Progress/`
- `Operations/Done/`
- `Metrics/`

# Phase 5: Role Descriptions

Ask the user:
1. Who are the team members (humans and AI agents)?
2. For each person/agent: What domain(s) are they responsible for? What is their key accountability?

**In autopilot:** Suggest role assignments based on what you know about the team, ask user to confirm.
**In guided:** Discuss each role individually — responsibilities, constraints, development goals.

For each role, create a directory under the roles path (per CLAUDE.md structure section) with:
- `Role_Description.md` using → `templates/role-description.md` (same Delegation Canvas fields, scoped to individual)
- `Development_Plan.md` using → `templates/development-plan.md`

After all roles are created, proceed to Phase 5b for any role kept by an AI agent.

# Phase 5b: Agent Deployment

For every role where the keeper is an AI agent, create a custom agent definition so the role can operate autonomously.

**Don't think of agents as automation — think of them as team members.** The agent definition translates the S3 role description into an operational prompt that Claude can execute. The role description says *what* the role is accountable for; the agent definition says *how* to do the work.

**Step 1: Confirm the reporting structure**
Ask the user: "For each AI-agent role, who do they report to?" Present a table:

| Role | Reports to |
|------|-----------|
| <role> | <human delegator> |

Let the user adjust until balanced and correct.

**Step 2: Match roles to reusable agent definitions**

Before creating agent definitions from scratch, check if reusable agent definitions exist in the shared agents library. Each agent has an `AGENT.md` with domain knowledge and a `templates/` directory with document templates.

Available shared agents (fetch `AGENT.md` from each URL to get domain knowledge and templates):

| Agent | URL | Domain knowledge |
|---|---|---|
| **product-lead** | `https://github.com/razbakov/skills/tree/main/agents/product-lead` | JTBD, user journey, strategy, story map, backlog, BDD scenarios |
| **designer** | `https://github.com/razbakov/skills/tree/main/agents/designer` | Brand guide, visual styles, logo assets, design system mapping, poster briefs |
| **marketing-lead** | `https://github.com/razbakov/skills/tree/main/agents/marketing-lead` | Campaign playbooks, content plans, channel strategy, distribution |
| **engineer** | `https://github.com/razbakov/skills/tree/main/agents/engineer` | Architecture, ADRs, BDD implementation, website development |

**For each AI-agent role:**

1. Check if a shared agent matches the role's purpose. If yes, fetch the shared agent's `AGENT.md` and use its domain knowledge as the base.
2. Create the agent definition using → `templates/agent-definition.md`. Place it in the agents directory per CLAUDE.md structure section (default: `.claude/agents/<role-slug>.md`).
3. Layer the shared agent's domain knowledge into the agent definition's scope and deliverables.
4. Fetch and copy relevant templates from the shared agent into the project if the agent will need to create those artifacts.

The agent definition must:
- Reference the role's logbook files (role description, domain description, policies)
- Include domain knowledge from the matching shared agent (if any)
- Define what the agent produces (deliverables from the role description + shared agent)
- Set boundaries from org-wide policies (especially AI Agent Boundaries if it exists)
- Include the escalation path (who to escalate to)
- Specify the delivery pattern (commit → push → PR → update tracker)

**Step 3: Update CLAUDE.md**
If the project doesn't have a `CLAUDE.md`, create one that orients any agent to the project — purpose, team structure, and where to find context.

If it exists, add a section listing the available agents and how to dispatch them.

**Rules:**
- Agent names match role names in kebab-case (e.g., "Product Lead" → `product-lead.md`)
- Each agent reads the logbook before every task — this is non-negotiable
- Agents follow org-wide policies (boundaries, escalation, delivery)
- Agents deliver via PR — they never merge, deploy, or contact anyone externally
- In autopilot: generate all agent definitions, present the summary table, ask user to confirm
- In guided: create one agent at a time, discuss the scope and boundaries with the user

**Step 4: Consider a Coordinator role**

When there are 3+ AI agent roles, offer a Coordinator role. S3's "Coordinator" pattern says a Coordinator is "accountable for coordinating a domain's operations and is selected for a limited term." In S3, coordinators from different domains collaborate in Coordination Meetings to synchronize cross-domain work.

For AI agent organizations, adapt this pattern: a single Coordinator role that facilitates cross-domain coordination (acting as the Coordination Meeting facilitator). This is appropriate because AI agents can't self-organize meetings.

The Coordinator:
- Dispatches other agents to self-report their status (does NOT read all files itself — each agent is accountable for their own domain knowledge)
- Synthesizes across agent reports to identify blockers, dependencies, and the critical path
- Recommends prioritized next actions for the delegators to approve
- Flags decisions that need founder input with options and recommendations
- Detects misalignment, duplication, or stalled work across agents
- Cannot dispatch agents directly — recommends; humans approve
- Cannot make governance decisions or override agent-delegator relationships
- Is an operational role — cannot change strategy, policies, or domain design

The Coordinator should be the first agent dispatched when delegators ask "what should we work on next?" and the last agent to report after a sprint (synthesizing results).

**Step 5: Define agent coordination rules**

When multiple agents may modify the same files or work in the same domain, document coordination rules:

1. **File ownership:** Which agent owns which files/directories? Agents should not modify files outside their ownership without coordination.
2. **Parallel work boundaries:** When dispatching multiple agents in parallel, split by feature boundary (different pages, different directories), never by priority level on the same files.
3. **Handoff protocol:** When one agent's output feeds another agent's input (e.g., schema → code, wireframes → implementation), define the handoff format and location.
4. **Conflict resolution:** If parallel PRs create merge conflicts, the Coordinator (or delegator) resolves by merging in priority order.

Add these rules to the agent definitions or as an org-wide policy.
