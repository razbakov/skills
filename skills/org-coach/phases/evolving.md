# Evolving Organizations

These patterns support the ongoing evolution and adaptation of the organization.

## Design Adaptable Systems

Develop a coherent set of constraints that enable the organization to easily adapt and grow:

- Establish clear but flexible boundaries (domains, policies, roles)
- Provide enough structure for safe operation, but enough room for innovation
- Treat all constraints and policies as provisional — regularly evaluate and evolve them
- When the environment changes, the constraints should be easy to update

**For AI agent organizations:** The agent definitions, coordination rules, and work board policies are the "constraints" of the system. Design them to be:
- **Modular:** Changing one agent's definition shouldn't require updating all others
- **Minimal:** Only constrain what needs constraining — leave operational details to the agent
- **Versioned:** Use review dates so constraints don't become stale
- **Empirical:** Treat each sprint as an experiment in how the organization operates

## Align Flow

Move decision-making close to where value is created and align information flow to support it:

- People doing the work should influence decisions about that work
- Information needed for decisions should be readily available to decision-makers
- Create short feedback loops to amplify learning
- Reduce bottlenecks by decentralizing operational decisions

**For AI agent organizations:** This means:
- Agents should make operational decisions within their domain (not escalate everything)
- The Coordinator should surface information from one agent's domain that another agent needs
- Feedback loops: after each sprint, the Analyst reviews what happened and feeds insights back to other agents
- Avoid bottlenecks: don't require Alex to approve every PR if the change is within the agent's documented autonomy

## Open Systems

Intentionally communicate with and learn from others outside the organization:

- Invite external experts for specialized input
- Involve representatives of affected parties (customers, partners)
- Learn from competitors, industry practices, and research

**For AI agent organizations:** Covered in collaboration.md. The key addition for the evolving phase: when the organization grows, establish regular channels for external input (e.g., user interviews, competitor analysis, community feedback) and assign an agent to process this information.

## Manage the Whole System

Ensure the effectiveness and integrity of the whole organization is monitored:

- Someone must be accountable for the health of the overall system, not just individual domains
- Monitor cross-domain metrics, not just per-domain metrics
- Ensure the organization can sustainably fulfill its purpose

**For AI agent organizations:** The Coordinator role partially covers this. Additionally:
- The delegators (founders) should regularly review the overall system health, not just individual agent output
- Cross-cutting metrics (e.g., "time from idea to deployed feature") should be tracked alongside domain-specific metrics
- The Logbook Keeper (see below) maintains the health of the governance system itself

## Collaborate on Dependencies

For each dependency between domains or roles, work with all stakeholders to agree on how to handle it:

1. Identify the dependency (e.g., Engineer depends on Designer for wireframes)
2. Agree on the interface: what's delivered, in what format, by when
3. Document the dependency in both roles' descriptions
4. Monitor and evolve the handoff as needed

**For AI agent organizations:** Dependencies between agents should be:
- Documented in the Dependencies table of each Role Description
- Explicit in the work board (items blocked by another agent's work are marked)
- Managed by the Coordinator who tracks cross-agent dependencies

## Continuous Improvement of Work Process

Continuously improve and refine how work is done:

- Team members look out for impediments (via Navigate via Tension)
- Use retrospectives (see below) to surface and address process issues
- Initiate improvement through Kanban or regular reflection meetings
- Focus on eliminating waste — any activity that doesn't contribute to fulfilling a purpose
- If an improvement works, expand its scope; if not, revert

**For AI agent organizations:** After each sprint:
1. The Coordinator reviews what went well and what didn't across all agents
2. Identify process waste (e.g., merge conflicts from parallel work, agents duplicating effort)
3. Propose process changes (e.g., "never dispatch 3 Engineers on the same files")
4. Implement as a policy or update to agent definitions
5. Review in the next sprint — did it help?

## Retrospective

A dedicated meeting to reflect on past experience, learn, and decide how to improve:

1. **Set the stage** — what period are we reviewing? What's the context?
2. **Gather data** — what happened? What did each agent deliver? What went wrong?
3. **Generate insights** — why did things go well or poorly? What patterns do we see?
4. **Decide what to do** — specific changes to make (update policies, agent definitions, work process)
5. **Close** — commit to the changes and set the next retrospective date

Expected outputs: changes to work processes, new tasks, updated policies, new drivers or requirements identified.

**For AI agent organizations:** Run a retrospective after every 2-3 sprints:
1. Coordinator dispatches all agents to self-report: what went well, what blocked you, what would you change?
2. Coordinator synthesizes into a retrospective report
3. Delegators review and decide which changes to implement
4. Changes are applied to agent definitions, policies, or the work board

Schedule: after every significant milestone (e.g., after the Rovinj pilot, after the first organizer partnership).

## Time-box Activities

Set fixed time constraints to maintain focus:

1. **Define your goal** — what do you want to achieve?
2. **Set the duration** — agree on how long this should take
3. **Break down work** — for longer activities, use smaller time boxes
4. **Review frequently** — check progress against the time box
5. **Negotiate extensions** — if needed, agree before time runs out

**For AI agent organizations:** Time-boxing applies to:
- Sprint length (e.g., each sprint is 1 week)
- Agent dispatch: include a scope limit in the prompt ("deliver within this PR, don't scope-creep")
- Decision deadlines: "This decision must be made by [date] or we proceed with the default"
- Review cadence: "If no response from the delegator within 48 hours, the Coordinator escalates"

## Logbook Keeper

Select a specific person or agent to be accountable for keeping the logbook up to date:

- Record policies, domain descriptions, role selections, evaluation dates, meeting records
- Organize information and improve the logbook structure
- Keep records current as decisions are made
- Ensure accessibility for all team members

**For AI agent organizations:** The Coordinator is the natural Logbook Keeper. After each sprint:
1. Ensure all decisions are recorded in the coordination directory (per CLAUDE.md)
2. Ensure all backlog statuses are current
3. Ensure all governance documents reflect the latest state
4. Flag any governance documents past their review date

Alternatively, designate this as an explicit responsibility in the Coordinator's role description rather than creating a separate role.
