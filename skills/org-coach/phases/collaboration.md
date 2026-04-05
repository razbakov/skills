# Collaboration Patterns

These patterns support healthy collaboration between agents, humans, and external parties.

## Ask for Help

A simple protocol for agents to request assistance from other agents or humans:

1. Explicitly ask: "Would you be willing to help me with [specific request]?"
2. The person/agent asked either accepts or declines — a simple yes or no.
3. If the request is unclear, ask for more information before answering.
4. If declined, accept the answer without negotiation.
5. If accepted, provide support in the best way possible.

**For AI agent organizations:** Agents should flag when they need input from another agent's domain. The Coordinator routes these requests. Example: the Engineer needs the Designer's input on a UI pattern — the Engineer flags it as a dependency in their PR, and the Coordinator dispatches the Designer to respond.

Add to agent definitions: "If your task requires knowledge or artifacts from another agent's domain, flag it as a dependency rather than guessing. Ask for help."

## Peer Feedback

Invite any member of the organization to give constructive feedback on your performance.

**Before:** Decide who to ask, clarify the topic, and explain you want both appreciations and improvement suggestions.

**During:** Take notes, repeat back what you heard, ask clarifying questions. Do not discuss or judge the feedback.

**After:** Review and decide how to act on it.

**For AI agent organizations:** After a sprint, the Coordinator can dispatch each agent to review one other agent's PR output and provide feedback:
- What was done well?
- What could be improved?
- Any suggestions for the next sprint?

This creates a peer feedback loop between agents without requiring human facilitation for every review.

## Involve Those Affected

When making decisions that impact others, involve them in the process:

- Identify who is affected by the decision
- Include them in the decision-making process (or their representative)
- Also involve them when reviewing and evolving the decision later

**For AI agent organizations:** When the Coordinator recommends dispatch priorities, agents whose work will be affected should be consulted (dispatched for a brief status/opinion) before the delegator finalizes. Example: before dispatching the Engineer to refactor the data model, ask the Operations Manager if this will break their conversion pipeline.

## Invest in Ongoing Learning

Make continuous learning part of every role:

- Embed learning directly into daily operations and role expectations
- After each sprint, identify what was learned and what should change
- Maintain a "lessons learned" section in sprint retrospectives
- When an agent encounters a pattern it hasn't seen before, document it for future reference

**For AI agent organizations:** Agent definitions should include: "After completing each task, note in your PR description what you learned that could improve future work in this domain." The Coordinator aggregates these across agents during sprint synthesis.

## Breaking Agreements

Sometimes an agent needs to deviate from established policy because following the rule would cause harm or miss an opportunity. S3 allows this, with conditions:

1. You must be **certain** the benefit outweighs the cost of waiting to amend the agreement properly.
2. **Clean up** any disturbances caused by breaking the agreement.
3. **Follow up** as soon as possible with anyone affected.
4. **Change the agreement** through proper channels — don't repeatedly break it.

**For AI agent organizations:** Agents should almost never break agreements unilaterally. Instead, flag the tension and escalate: "Policy X says I should do Y, but in this case Y would cause [harm]. I recommend amending the policy." The delegator decides whether to authorize the exception.

## Contract for Successful Collaboration

When onboarding a new agent, external contributor, or partnership, co-create a working agreement:

1. **Define expectations and culture** — state the reasons for collaboration, describe the desired working style.
2. **Agree on terms** — what each party contributes, what they expect in return.
3. **Use clear language** — no jargon, include a glossary if needed.
4. **Build in lifecycle support** — onboarding process, review schedule, how to handle disagreements, how to end the collaboration.

**For AI agent organizations:** The agent definition IS the contract. It defines what the agent does, what it can't do, how it delivers, and how it's evaluated. Ensure every agent definition covers all these aspects. When adding a new agent, treat the definition as a mutual agreement — the delegator commits to timely reviews and clear direction, the agent commits to operating within boundaries.

## Artful Participation

An individual commitment to act in ways that enable effective collaboration:

- Take responsibility for your own learning and development
- Consider the needs of the team alongside your own
- Refrain from or change actions that are not helpful
- Raise objections and concerns when you see them

**For AI agent organizations:** This translates to the tension-sensing and self-assessment sections in the agent template. Every agent should be "artfully participating" — not just executing instructions, but actively contributing to the organization's effectiveness.

## Open Systems

Intentionally communicate with and learn from others outside the organization:

- Invite external experts for specialized perspectives
- Involve representatives of affected parties (customers, partners)
- Seek outside input when internal knowledge is insufficient

**For AI agent organizations:** When agents research competitors, market trends, or technical approaches, they are practicing Open Systems. Make this explicit: agents should cite external sources, reference industry practices, and flag when the organization might benefit from external input (e.g., "A UX researcher could validate these wireframes with real users").

## Helping Team

A team that executes work without making governance decisions. The delegator defines rules and constraints; the team executes and informs the delegator when governance decisions are needed.

**For AI agent organizations:** This is exactly how AI agents already work — they execute within boundaries and escalate governance decisions. Make this explicit in the skill: AI agent teams are Helping Teams by default. They:
- Execute tasks within defined constraints
- Inform the delegator when they see a need for governance changes
- Can raise objections to decisions affecting them
- Can select a representative (the Coordinator) to participate in governance
