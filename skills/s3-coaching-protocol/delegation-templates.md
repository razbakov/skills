# Delegation Templates

Ready-to-use subagent domain handoff templates for common parallel phase groups. Each follows the 5-part handoff format from the protocol.

## Generic Template

```
## Purpose
[What this subagent is responsible for producing]

## Context
[Summary of relevant prior phases — mission, hypothesis, key decisions.
Include only what this subagent needs. Not the full project history.]

## Constraints
- Read these files: [list]
- Use this template: [path]
- Output format: [markdown/feature file/etc.]
- Do NOT: [boundaries — what's out of scope]

## Deliverable
[Exact expected output with acceptance criteria]

## Dependencies
[What other parallel subagents are producing. Avoid conflicts.]
```

## Brand + Marketing + Architecture (Phases 11, 12, 13)

**Prerequisite:** Story map (Phase 8) and backlog (Phase 9) complete.

### Subagent A: Brand & Design (Phase 11)

```
## Purpose
Generate a brand guide and visual style for the project.

## Context
- Mission: [from README]
- Target customer: [from strategy.md]
- Hypothesis: [from README or strategy.md]
- Product personality: [from JTBD — what emotions should the brand evoke?]

## Constraints
- Read: README.md, strategy.md, jtbd.md
- Use templates: templates/brand.md, templates/style.md
- Output: brand guide + 1-3 style variants
- Do NOT make architectural or marketing decisions

## Deliverable
- brand.md with colors, typography, spacing, effects, logo rules
- At least 1 style.md variant with mood, palette, and usage rules

## Dependencies
- Marketing subagent will need the brand colors/fonts — produce those first
- Architecture subagent is independent — no conflicts
```

### Subagent B: Marketing (Phase 12)

```
## Purpose
Create a launch campaign and content plan.

## Context
- Mission: [from README]
- Target customer: [from strategy.md]
- Top jobs: [from jtbd.md — what messages resonate?]
- User journey aha moment: [from user-journey.md]

## Constraints
- Read: README.md, strategy.md, jtbd.md, user-journey.md
- Use templates: templates/campaign.md, templates/content-plan.md
- Output: campaign strategy + weekly content plan
- Do NOT make brand or architecture decisions
- If brand colors/fonts are available, use them for consistency

## Deliverable
- campaign.md with launch phases and tactics
- content-plan.md with weekly calendar and channels

## Dependencies
- Brand subagent produces colors/fonts — use if available, placeholder if not
- Architecture subagent is independent — no conflicts
```

### Subagent C: Architecture (Phase 13)

```
## Purpose
Design the technical architecture for the project.

## Context
- Mission: [from README]
- Story map: [from story-map.md — what features need technical support?]
- Backlog priorities: [from backlog.md — what's in the first release?]
- User journey: [from user-journey.md — what's the critical path?]

## Constraints
- Read: README.md, story-map.md, backlog.md, user-journey.md
- Use template: templates/architecture.md
- Output: system diagram, tech stack rationale, data model, deployment
- Do NOT make brand or marketing decisions
- Optimize for the first release slice, not the full vision

## Deliverable
- architecture.md with system diagram, tech choices with rationale, data model, deployment strategy

## Dependencies
- Brand and marketing subagents are independent — no conflicts
- If backlog has API-related stories, ensure data model covers them
```

## Sketch 3 Approaches (Phase 5)

**Prerequisite:** User journey (Phase 4) complete.

Each subagent generates one approach independently. The main agent then presents all three for comparison.

### Subagent per Approach

```
## Purpose
Generate approach [A/B/C] for solving the user's core job.

## Context
- Hypothesis: [from README]
- Top job: [from jtbd.md]
- User journey with struggle points: [from user-journey.md]
- Aha moment: [from user-journey.md]

## Constraints
- Read: README.md, jtbd.md, user-journey.md
- Approach angle: [A: simplest/MVP | B: most innovative | C: most scalable]
- Output: wireframe sketch (ASCII) + trade-offs table
- Do NOT pick a winner — the main agent compares all three

## Deliverable
- Approach name and one-line summary
- ASCII wireframe of the key screen(s)
- Trade-offs table: strengths, weaknesses, risks, effort estimate
- What Must Be True for this approach to succeed

## Dependencies
- Other approach subagents are independent — intentionally no coordination
- Divergence is the goal — don't converge prematurely
```

## Multi-Product Backlogs (Phase 9)

**Prerequisite:** Story map per product complete.

### Subagent per Product

```
## Purpose
Generate the backlog for [product name].

## Context
- Product strategy: [from product/strategy.md]
- Story map: [from product/story-map.md]
- JTBD: [from product/jtbd.md]

## Constraints
- Read: product-specific strategy.md, story-map.md, jtbd.md
- Use template: templates/backlog.md
- Output: epics with problem statements, stories with "so I can..."
- Scope: only this product — do not reference other products
- Every story must link back to a job from jtbd.md

## Deliverable
- backlog.md with epics grouped by problem, stories with JTBD references

## Dependencies
- Other product backlog subagents are independent
- Cross-product dependencies should be flagged but not resolved (main agent handles)
```

## Workspace Review (Parallel Layer Audit)

**Prerequisite:** README.md exists with workspace structure.

### Subagent per Layer Group

```
## Purpose
Audit the [foundation/product/design/engineering] layer of this workspace.

## Context
- Workspace structure: [from README.md]
- What to check: [specific checklist items from the review table]

## Constraints
- Read: README.md first, then scan directories listed in the structure
- Output: checklist with status (done/incomplete/missing) per item
- Do NOT fix anything — report only
- Be specific about what's missing (e.g., "no mission statement" not "foundation incomplete")

## Deliverable
- Layer audit with status per checklist item
- One suggested next action for this layer

## Dependencies
- Other layer audit subagents are independent
- Main agent synthesizes all layer audits into a single review
```
