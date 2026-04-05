# Phase 0: Discovery

Before creating any files, coach the user through S3's "Describe Organizational Drivers" and "Determine Requirements" patterns.

## Describing the Organizational Driver

Per S3, a driver should be "a comprehensive but brief summary in two or three sentences." It weaves together three components — but is written as **flowing prose, not labeled sections**:

- **Current conditions** — observable circumstances. Must be concise, specific, objective (verifiable facts), and avoid evaluative language.
- **Effect** — current or anticipated consequences of those conditions. Be explicit about whether effects are happening already or anticipated.
- **Relevance** — why responding matters for the organization: will it generate value, eliminate waste, or avoid undesirable consequences? (Skip if obvious from the first two.)

Do NOT use labels like "Current conditions:", "Effect:", "Relevance:" in the output. Write it as natural sentences. When communicating with colleagues who share the context, describing just the conditions or just the effect can be enough.

A driver can be framed as a **problem to solve** or an **opportunity to pursue**.

**The conversation (4 questions max in autopilot, deeper in guided):**

1. "Describe the situation you're observing. What is actually happening or not happening right now?"
2. "What consequences does this lead to? Are they happening already or do you anticipate them?"
3. "Why is it worthwhile for the organization to respond? What value would be created or what cost avoided?"
4. Summarize the driver back as 2-3 flowing sentences. Ask: "Does this capture it?"
5. **Review the driver against the checklist below** before moving to the requirement. Fix any issues first.

**Rules:**
- Don't accept "I want to build X" as the driver. X is a solution — dig for the underlying situation.
- Describe conditions, not assumptions about what's missing.
- Keep it to 4 questions max in autopilot — don't interrogate.

**Common mistakes in conditions:**

| Mistake | Bad example | Good example |
|---|---|---|
| Assuming what's missing | "There is no single platform for dancers to discover events" | "Dance event info is scattered across Facebook, WhatsApp, Instagram, and flyers" |
| Evaluative language | "Organizers spend excessive effort on promotion" | "Organizers promote the same event across 4+ channels individually" |

Both bad examples feel natural but violate S3: the first describes an assumption about what *should* exist rather than what *does* exist; the second uses "excessive" which is subjective. Always describe what you can observe.

## Reviewing a Driver

Use this checklist when reviewing an existing driver (during logbook review, policy review, or periodic governance review):

1. **Is it still a driver?** — Ask: "Would responding to this situation help the organization generate value, eliminate waste, or avoid undesirable consequences?" If no, drop it or pass it to the appropriate domain.
2. **Conditions are objective** — Verify the text describes verifiable facts and observations, not assumptions about what might be missing. Language must be objective, concise, and specific — no vague or evaluative wording.
3. **Effect is clear** — Consequences are explicitly stated. It's clear whether effects are already occurring or anticipated. If the link isn't obvious, the text explains how the effect follows from the conditions.
4. **Relevance sticks to "why"** — States the benefit of responding and/or the cost of inaction. Explains how acting fulfills an organizational purpose or how inaction creates risk/waste. Must NOT prescribe solutions or requirements — that belongs elsewhere.
5. **Brief and digestible** — Still fits in 2-3 sentences. Excess detail belongs in the logbook, not the summary.
6. **Review driver before policy** — When reviewing a policy, always review the driver first. If the situation has changed and the driver is no longer relevant, retire and archive the associated policy. Updating the driver and requirement takes precedence over updating the policy.

## Determining the Requirement

The requirement connects the driver to what needs to change. It has two components that mirror the driver:

- **Intended outcomes** — specific, observable results to achieve (mirrors the driver's *effect*)
- **Enabling conditions** — circumstances necessary to establish for achieving those outcomes (mirrors the driver's *current conditions*)

**In autopilot:** Infer the requirement from the driver conversation. Present it for confirmation.
**In guided:** Ask separately: "What outcomes do you want to achieve?" and "What conditions need to be true to make that possible?"

Once discovery is complete, create the primary driver file using → `templates/primary-driver.md`. Place it in the logbook directory (path depends on the workspace preset chosen in Phase 1 — see `templates/structures/s3-organization.md`).

# Phase 1: Organization Canvas

The Organization Canvas clarifies the organization's **overall domain**. Per S3, it factors in:

1. **Purpose and overall strategy** — why the organization exists and the high-level approach
2. **Customers, partners, and other stakeholders** — who is served, who contributes, who is affected
3. **Business model(s)** — how value is created and captured
4. **Environmental conditions** — legal/economic constraints, market trends, competition

**In autopilot:** Infer as much as possible from Phase 0 answers, ask only what's missing.
**In guided:** Walk through each component with the user.

Once answered, create the organization canvas using → `templates/organization-canvas.md`

**Also create the workspace structure during this phase:**

1. Read the presets from `templates/structures/s3-organization.md`
2. Ask the user which preset fits their project (numbered, docs, flat, or custom)
3. Create the directory tree for the chosen preset
4. **Write the structure to CLAUDE.md** — this is critical. Add a `## Structure` section that maps every artifact type to its actual path. Example:

```markdown
## Structure

- Logbook: `docs/governance/`
- Primary driver: `docs/governance/primary-driver.md`
- Strategy: `docs/governance/strategy.md`
- Policies: `docs/governance/policies/`
- Domains: `docs/domains/<domain-name>/`
- Domain description: `docs/domains/<domain-name>/description.md`
- Domain governance backlog: `docs/domains/<domain-name>/governance/backlog/`
- Domain operations backlog: `docs/domains/<domain-name>/operations/backlog/`
- Roles: `docs/roles/<role-name>/`
- Role description: `docs/roles/<role-name>/description.md`
- Coordination: `docs/coordination/`
- Agents: `.claude/agents/`
```

All subsequent phases and agent definitions read CLAUDE.md to resolve paths. Never hardcode paths — always look them up from the Structure section.

# Phase 2: Strategy & Values

## Strategy

Per S3, a strategy is "a high-level approach for how people will fulfill the purpose of a domain." It is a type of policy and must include:

1. **Purpose** — the driver and requirement it responds to
2. **Intended outcome(s)** — what implementing the strategy aims to achieve
3. **The strategy itself** — the high-level approach, including rationale
4. **Responsibilities** — who is responsible for what
5. **Review date, metrics, and monitoring** — how and when effectiveness is evaluated

A strategy is a shared agreement between delegator and delegatee, regularly reviewed and updated (pivot or persevere).

**In autopilot:** Draft strategy from Phase 0-1 answers, present for confirmation.
**In guided:** Ask the user to define each component. Note: S3 says it's usually more effective if the team leads strategy development, with the delegator reviewing for impediments.

## Values

Present the S3 Seven Principles as the foundation:

1. **Effectiveness** — "Devote time only to what brings you closer towards achieving your organization's overall objectives"
2. **Consent** — "Raise, seek out and resolve objections to proposals, policies and activities"
3. **Empiricism** — "Test all assumptions you rely on through experiments and continuous revision"
4. **Continuous Improvement** — "Regularly review the outcomes of your actions, then make incremental improvements"
5. **Equivalence** — "Involve people in making and evolving decisions that affect them"
6. **Transparency** — "Record all information that is valuable for the organization and make it accessible to everyone, unless there is a reason for confidentiality"
7. **Accountability** — "Respond when something is needed, do what you agreed to do, and accept your share of responsibility"

Ask: "Do you want to adopt all seven as-is, or add/modify any?"

Create the strategy and values files using → `templates/strategy.md` and `templates/values.md`. Place them in the logbook directory per CLAUDE.md structure section.
