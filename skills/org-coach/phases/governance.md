# Phase 6: Org-Wide Policies

Ask the user:
1. Are there any organization-wide policies needed from day one? (e.g., data security, AI agent boundaries, decision-making process, financial transparency)
2. What constraints apply to all domains?

**In autopilot:** Suggest 1-2 essential policies based on the organization's context (e.g., if AI agents are involved, suggest a policy on AI agent boundaries). Ask user to confirm.
**In guided:** Discuss each potential policy area, use consent decision-making to finalize.

Each policy must include (per S3):
- Summary of the overall purpose
- Intended outcome
- Description of the agreed intervention
- Who is responsible for what
- Review date, relevant metrics, and how they will be monitored

Create policies using → `templates/policy.md`. Place them in the policies directory per CLAUDE.md structure section.

# Phase 7: Coordination

Ask the user:
1. How will domains coordinate? (regular sync meetings, async updates, delegate circles)
2. How often?
3. Are there dependencies between domains that need explicit management?

Create:
- Domain map using → `templates/domain-map.md`, placed in the logbook's structure directory per CLAUDE.md
- Coordination directory for future meeting records per CLAUDE.md structure section

The Domain Map should show:
- All domains and their relationships
- All roles and which domains they belong to
- Coordination mechanisms (meetings, async channels)
- Dependencies between domains

# Phase 8: Backlogs

For each domain, help the user seed their initial backlogs:

**Governance Backlog** — items that need significant decisions or policies:
- Proposals needing consent
- Policies due for review
- New drivers requiring response
- Domain descriptions needing update

**Operations Backlog** — day-to-day work items:
- Tasks that can be acted on
- Deliverables in progress
- Impediments

**In autopilot:** Suggest 2-3 initial items per backlog based on what was discussed in earlier phases.
**In guided:** Walk through each domain and ask what governance decisions and operational tasks are pending.

Create backlog items as individual files in the appropriate `Backlog/` directories, or as a single backlog file per domain — match the user's preference.

# Phase 9: Organizing Work (Visualize, Pull, Limit)

S3 provides several patterns for managing operational work. For AI agent organizations, these need explicit setup because agents can't self-organize a kanban board.

## Visualize Work

S3 says: "Maintain a system that allows all stakeholders to review the state of all work items currently pending, in progress, or complete."

Ask the user: "Where will work be visualized? Options: GitHub Projects board, Notion board, or a simple markdown kanban file in the repo."

Set up the chosen system with columns:
- **Backlog** — prioritized work items not yet started
- **Ready** — items with all dependencies met, ready for an agent to pull
- **In Progress** — actively being worked on (limit: 1 per agent)
- **In Review** — PR created, waiting for delegator review
- **Done** — merged and deployed

Every backlog item must be on the board. The board is the single source of truth for work status — not individual file headers.

## Pull System

S3 says: "People pull in new work items when they have capacity, instead of having work pushed or assigned to them."

For AI agents, adapt this:
- The **Coordinator** maintains the board and moves items to "Ready" when dependencies are met
- **Delegators** (not the Coordinator) approve which items are ready to pull
- When dispatching agents, reference the board item — don't write ad-hoc task descriptions that bypass the backlog
- Each agent's dispatch prompt should say: "Pull the top item from Ready in your domain"

## Limit Work in Progress

S3 says: "Limit the number of concurrent work items in any stage of the process."

Rules for AI agent organizations:
- **One agent, one work item at a time.** Don't dispatch the same agent type on multiple tasks simultaneously.
- **Never dispatch multiple agents to modify the same files.** Split work by file/directory ownership, not by priority level.
- If you need to parallelize, use different agent types working in different directories.
- The Coordinator tracks WIP and flags overload.

## Deliver Value Incrementally

S3 says: "Slice work into smaller pieces to deliver value fast."

For AI agents, this means:
- Stories should be small enough for one PR
- Each PR should be deployable independently
- Don't batch multiple stories into one dispatch — one story per agent dispatch

**In autopilot:** Set up a markdown kanban file in the logbook directory (per CLAUDE.md structure section) and populate it from existing backlog items.
**In guided:** Ask the user which tool they prefer and set it up together.

# Phase 10: Experiment Design

S3's empiricism principle says: "Test all assumptions you rely on through experiments and continuous revision." Requirements describe *what* needs to change — experiments describe *how to test* whether an intervention works.

For each requirement that involves uncertainty (most of them in early-stage organizations), create an experiment card:

**Experiment card structure:**
1. **Requirement reference** — which requirement this tests
2. **Hypothesis** — "We believe that [intervention] will result in [outcome] for [actor]"
3. **Method** — step-by-step what will be done, by whom, and in what timeframe
4. **Success metrics** — specific, measurable thresholds (e.g., "20% of attendees open the schedule")
5. **Pivot triggers** — specific thresholds that signal the hypothesis is wrong (e.g., "<10% adoption")
6. **Persevere criteria** — all conditions that must be met to continue on this path
7. **Timeline** — when evaluation happens (not just a deadline, but checkpoints)
8. **Risks and mitigations** — what could go wrong and how to reduce the risk

**In autopilot:** For each requirement with uncertainty, draft an experiment card and ask user to confirm the thresholds.
**In guided:** Walk through hypothesis formation, help the user set realistic thresholds, discuss what "pivot" means concretely.

Create experiment cards using → `templates/experiment-card.md`. Place them in the domain's governance directory per CLAUDE.md structure section.

**The key S3 insight:** Separate the *purpose* (driver + requirement) from the *intervention* (experiment). If an experiment fails, the driver is still valid — you try a different intervention. This prevents organizations from abandoning a valid need because one approach didn't work.

# Phase 10: Review and Evaluation

S3 requires regular review of all governance artifacts. Set up the review cadence:

**What to review and when:**

| Artifact | Review frequency | Who reviews |
|----------|-----------------|-------------|
| Primary driver | Quarterly | Partnership |
| Strategy | Quarterly | Partnership |
| Domain descriptions | Quarterly | Domain delegator + role keepers |
| Role descriptions | Quarterly | Delegator + role keeper |
| Policies | Per review date on each policy | Responsible party |
| Experiment results | Per experiment timeline | Analyst + delegator |
| Agent performance | Quarterly (per Delegation Canvas) | Delegator using role metrics |

**Agent evaluation protocol:**
For each AI agent role, the delegator reviews:
1. Output quality — against the role's key metrics
2. Boundary compliance — any escalation failures or policy violations?
3. Tension sensing — did the agent raise useful tensions, or execute silently?
4. Driver alignment — did the agent's work serve the organizational driver?

**In autopilot:** Set all review dates to quarterly from the creation date, add them to the logbook.
**In guided:** Discuss appropriate cadences for each artifact with the user.
