# Meeting Formats and Practices

S3 provides patterns for structuring and running meetings. In AI agent organizations, "meetings" happen when the Coordinator dispatches agents for synchronized input, when humans review agent output, or when agents facilitate human workshops.

## Meeting Formats

### Governance Meeting

A regular meeting (every 2-4 weeks) to make and evolve decisions about how to do the work:

1. Opening round (Check In)
2. Review governance backlog — which items need attention?
3. For each item: present driver, co-create proposal, consent decision
4. Evaluate the meeting
5. Closing round

**For AI agent organizations:** The Coordinator runs a "governance sync" by dispatching agents to report governance-relevant tensions. The delegators then review and make consent decisions. Frequency: every 2-4 weeks or after every 2-3 sprints.

### Daily Standup

A brief daily meeting to organize work and resolve blocks:

1. What did you accomplish since last standup?
2. What will you work on today?
3. What is blocking you?

**For AI agent organizations:** The Coordinator dispatches all agents for a brief status report (3 questions above). Synthesizes into a daily status for the delegators. For async teams, this can be a weekly cadence instead of daily.

### Planning and Review Meetings

Iterative work cycles with planning at the start and review at the end:

**Planning:** Select work items from the backlog, estimate effort, commit to what will be done this sprint.
**Review:** Demonstrate what was delivered, compare to what was planned, identify lessons.

**For AI agent organizations:** 
- Planning: Coordinator recommends dispatch priorities, delegators approve, agents pull from the board.
- Review: After each sprint, Coordinator collects agent outputs and produces a sprint review for delegators.

### Coordination Meeting

Regular meetings for reporting on and coordinating work across domains:

1. Each domain reports recent progress and upcoming work
2. Identify cross-domain dependencies and impediments
3. Align and distribute work across domains
4. Respond to impediments

**For AI agent organizations:** This is exactly what the Coordinator does — dispatch agents for status, synthesize, identify dependencies and blockers. Run after each sprint or weekly.

### Retrospective

See `phases/evolving.md` for the full retrospective pattern. Schedule retrospectives after every 2-3 sprints or after significant milestones.

## Meeting Practices

### Rounds

Go around the group giving everyone a chance to speak in turn:

- Clear purpose for each round
- Begin with a different person each time
- Change direction to vary who speaks first/last
- Everyone gets equal time

**For AI agent organizations:** When dispatching all agents for input, this IS a round — each agent speaks independently without being influenced by others. The parallel dispatch pattern naturally implements rounds.

### Facilitate Meetings

Choose someone to facilitate — keep the meeting on track, hold the space, navigate the agenda:

- Prepare an agenda before the meeting
- The facilitator holds time, navigates topics, draws out contributions
- Facilitate a meeting evaluation at the end
- Select the facilitator for a specific term

**For AI agent organizations:** The Coordinator is the default facilitator for cross-agent meetings. For human meetings (e.g., partnership discussions between Alex and Kirill), an agent can prepare the agenda and structure, while a human facilitates.

### Prepare For Meetings

Preparation makes meetings effective:

1. Clarify the driver and intended outcome
2. Decide who to invite
3. Create an agenda with driver, outcome, process, time-box, and prep needed for each item
4. Schedule in advance with appropriate duration
5. Assign facilitator, host, and notetaker
6. Participants review the agenda beforehand

**For AI agent organizations:** Before a governance sync or sprint planning, the Coordinator prepares:
- Agenda with specific items from the governance backlog
- Context for each item (which agents are affected, what the options are)
- Time estimates for delegator review

### Check In

A brief disclosure to help people become present and engaged:

- Share what's on your mind, how you're feeling, any distractions
- People can pass
- Use as an opening or closing round

**For AI agent organizations:** Agents don't have feelings, but humans do. When agents facilitate human meetings, include a check-in round. When agents self-report, the equivalent is: "What is the current state of my domain? What concerns do I have?"

### Evaluate Meetings

Take time for learning at the end of each meeting:

- Reserve 5 minutes for a 1-hour meeting
- Reflect on: what went well, what could improve, what to start/stop/keep
- Record learnings and review before the next meeting

**For AI agent organizations:** After each Coordinator synthesis:
- Did the agents provide useful status reports?
- Were the dispatch prompts clear enough?
- Did the delegators get what they needed to make decisions?
- What should change in the next cycle?

### Meeting Host

Someone responsible for logistics — preparation and follow-up:

**Before:** Identify goals, prepare agenda, invite participants, estimate time, schedule, set up the space.
**After:** Distribute minutes, tie up loose ends, ensure action items are tracked.

**For AI agent organizations:** The Coordinator is the default meeting host. After each coordination cycle, the Coordinator:
- Records decisions in the coordination directory (per CLAUDE.md)
- Updates the work board
- Ensures action items are captured as backlog items

### Governance Facilitator

Select someone to facilitate governance meetings specifically:

- Familiarize with the governance backlog before the meeting
- Use S3 patterns: Rounds, Proposal Forming, Consent, Role Selection, Resolve Objections
- Keep governance meetings on track and ensure they're evaluated
- Can invite others to facilitate specific items

**For AI agent organizations:** The Coordinator facilitates governance by:
- Identifying governance items that need attention (policies past review date, unresolved tensions, role changes)
- Preparing items with context and options
- Presenting to delegators for consent decisions
- Recording outcomes in the logbook
