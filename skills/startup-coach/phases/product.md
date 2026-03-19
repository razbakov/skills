All file paths below are relative to the product area defined in the workspace structure (README.md). Look up the actual directory before creating files.

# Phase 2: Product Strategy

Create `strategy.md` using → `templates/strategy.md`

**Rules:**
- Lead with a testable hypothesis — not a feature list
- Pricing must explain "why this price" not just "what the price is"
- Success metrics must have targets and timeframes
- Next steps use ✅ / 🔲 to show progress at a glance

# Phase 3: Jobs to Be Done

Create `jtbd.md` using → `templates/jtbd.md`

The JTBD analysis captures what users are trying to accomplish independent of the product. It feeds directly into the user journey and story map.

**Rules:**
- Use the JTBD format: "When [situation], I want to [motivation], so I can [expected outcome]"
- Group jobs by persona — one section per persona
- Each job gets 2–4 "Struggling moments" — real-world triggers that create urgency
- End with a Job Priority Map table ordered by frequency and business impact
- Jobs exist independent of your product — they describe what users do today, not what your product will do
- Number jobs sequentially across personas (Job 1, Job 2, ...) for cross-referencing in the backlog

# Phase 4: User Journey

Create `user-journey.md` using → `templates/user-journey.md`

**Rules:**
- Write from the user's perspective, not the system's
- 4–6 steps maximum — this is the happy path, not edge cases
- Include an ASCII wireframe showing the main interface layout
- Identify the "aha moment" explicitly — the step where value clicks
- End with "What Must Be True" — preconditions the system needs for the first impression to succeed

# Phase 8: Story Map

Create `story-map.md` using → `templates/story-map.md`

**Rules:**
- Columns represent the user's journey (left to right) — not epics or technical layers
- Rows stack stories by priority (top = essential), with bold separator rows marking release slices (MVP, R1, R2)
- Story numbers reference the backlog (e.g., 1.1, 3.4) and each cell is a short label + number
- Cross-reference JTBD and backlog at the top: "Research in [Jobs to Be Done](jtbd.md). Story numbers reference [Backlog](backlog.md)."
- Secondary personas get their own row at the bottom (e.g., "Consultant journey (parallel): ...")

# Phase 9: Backlog

After the story map is approved, create `backlog.md` using → `templates/backlog.md`

This is the detailed specification of all stories. Each epic starts with the problem it solves and references the JTBD that drive it.

**Rules:**
- Start with a Personas table — same personas as the story map
- Group stories by epic — each epic opens with a **Problem** statement and **Jobs** references (linking to jtbd.md)
- Stories use the format: "goal + outcome" — always include "so I can [benefit]"
- Story numbers use `<epic>.<story>` format matching the story map
- Each story belongs to exactly one persona

# Phase 10: Scenarios (BDD)

After the backlog is created, generate feature files in the `scenarios/` directory.

Create each file using → `templates/scenario.feature`

Feature files are living documentation that progress through three levels of detail:

1. **User story only** — the Feature description captures the "As a / I want / So that" from the backlog
2. **Acceptance criteria** — Rules are added as the story is refined (one Rule per AC)
3. **Scenarios** — concrete Given-When-Then examples are added when development begins

**Rules:**
- One `.feature` file per story or tightly related group of stories
- Filename is a short slug (e.g., `grid-view.feature`, `create-booking.feature`)
- Feature description is the user story from the backlog
- Use `Rule:` blocks to express acceptance criteria
- Scenarios use `Given-When-Then` with concrete data (data tables, not vague phrases)
- Use `Background:` for shared setup within a feature
- Use tags (`@epic-1`, `@mvp`, `@wip`) for organization and test filtering
- BDD tooling: **playwright-bdd** (not cucumber-js) — feature files drive Playwright tests
