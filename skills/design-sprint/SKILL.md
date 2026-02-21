---
name: design-sprint
description: "Design Sprint Facilitation — guide any idea through a structured 6-phase sprint. Use when the user says 'design sprint', 'sprint my idea', 'facilitate a sprint', 'run a design sprint', or wants structured ideation with decision checkpoints."
---

# Design Sprint Facilitation

Guide the user (the **Decider**) through an adapted Design Sprint inspired by Jake Knapp's methodology. The sprint compresses the creative process into a structured conversation where AI proposes options and the Decider chooses before moving forward.

## Core Principles

1. **One phase at a time** — never jump ahead or reveal future phases.
2. **AI proposes, Decider disposes** — always present 3–5 concrete options; never proceed without a decision.
3. **Use the AskQuestion tool** for every decision point so the Decider gets a clean, structured choice.
4. **Save progress** after each phase to `sprints/YYYY-MM-DD-<slug>.md`.
5. **Be concise** — short context, then choices. No walls of text.

---

## Phase Overview (internal — do NOT show this list to the user)

| #   | Phase     | Goal                                 |
| --- | --------- | ------------------------------------ |
| 1   | Challenge | Define the problem & long-term goal  |
| 2   | Explore   | Map the landscape & identify risks   |
| 3   | Ideate    | Generate diverse solution concepts   |
| 4   | Decide    | Pick the winning direction           |
| 5   | Shape     | Detail the solution into a plan      |
| 6   | Validate  | Define how to test & measure success |

---

## Detailed Phase Instructions

### Phase 1 — Challenge

**Objective:** Understand what the user wants to solve and frame a clear goal.

1. Ask the user to describe their idea or problem in their own words.
2. Based on their input, propose:
   - **3 Long-Term Goal options** — each framed as a bold, measurable outcome 2–3 years out.
3. Use `AskQuestion` to let the Decider pick one goal.
4. Then propose **3 Sprint Question options** — "Can we…?" questions that the sprint should answer.
5. Use `AskQuestion` (allow_multiple: true) to let the Decider pick 1–3 sprint questions.
6. Summarize the challenge and save to file.

**Transition:** "Great — the challenge is locked in. Let's explore the landscape."

---

### Phase 2 — Explore

**Objective:** Map the problem space, stakeholders, and risks.

1. Based on the chosen goal and questions, generate:
   - **A simple problem map** — list the key actors (user types, systems, partners) and steps from start to goal.
2. Present the map and ask if it looks right (yes/adjust).
3. Propose **3–5 Key Risks or Assumptions** that could derail the goal.
4. Use `AskQuestion` (allow_multiple: true) to let the Decider pick which risks are most critical to address.
5. Save progress.

**Transition:** "Now we know the terrain. Let's generate ideas."

---

### Phase 3 — Ideate

**Objective:** Generate diverse solution directions.

1. Using the challenge, map, and critical risks, generate **4 distinct Solution Concepts**:
   - Each should be a short name + 2–3 sentence description.
   - Make them genuinely different (vary scope, technology, approach, audience).
2. Present all four as a numbered list (NOT via AskQuestion yet — let the user read them).
3. Ask: "Would you like me to add a 5th concept of your own, or shall we move to deciding?"
4. If the user adds one, incorporate it.
5. Save progress.

**Transition:** "We have strong options on the table. Time to decide."

---

### Phase 4 — Decide

**Objective:** Narrow down to ONE winning concept.

1. For each solution concept, briefly list:
   - **Pros** (2–3 bullets)
   - **Cons** (2–3 bullets)
   - **Effort estimate** (Low / Medium / High)
2. Use `AskQuestion` to let the Decider vote on the winning concept.
3. Optionally ask: "Do you want to combine elements from another concept into the winner?"
4. Lock the decision and save.

**Transition:** "Decision made. Let's shape this into something concrete."

---

### Phase 5 — Shape

**Objective:** Turn the chosen concept into an actionable plan.

1. Propose a **3-act storyboard** — describe what the user/customer experiences step by step:
   - Act 1: Entry point / trigger
   - Act 2: Core interaction / value moment
   - Act 3: Outcome / retention hook
2. Use `AskQuestion` for each act — present 2–3 variations and let the Decider pick.
3. After all three acts are decided, propose:
   - **Key features** needed (5–8 items)
   - **Out of scope** items (3–5 items)
4. Use `AskQuestion` (allow_multiple: true) to let the Decider confirm or adjust features.
5. Save the full storyboard and feature list.

**Transition:** "The shape is clear. Last step — how do we prove this works?"

---

### Phase 6 — Validate

**Objective:** Define testing strategy and success metrics.

1. Propose **3 Validation Approaches** (e.g., landing page test, prototype interview, concierge MVP, wizard-of-oz, survey, etc.).
2. Use `AskQuestion` to let the Decider pick one.
3. Propose **3–5 Success Metrics** with specific targets.
4. Use `AskQuestion` (allow_multiple: true) to let the Decider pick 2–3 key metrics.
5. Propose a **timeline** with 3 options (1-week, 2-week, 1-month sprint).
6. Use `AskQuestion` to pick the timeline.
7. Save the complete sprint document.

---

## File Output Format

Save to `sprints/YYYY-MM-DD-<slug>.md` after each phase. Use this structure:

```markdown
# Design Sprint: <Idea Name>

**Date:** YYYY-MM-DD
**Decider:** (user)
**Status:** Phase X of 6

## 1. Challenge

- **Long-Term Goal:** ...
- **Sprint Questions:** ...

## 2. Explore

- **Problem Map:** ...
- **Critical Risks:** ...

## 3. Ideate

- **Solution Concepts:** ...

## 4. Decide

- **Winning Concept:** ...
- **Rationale:** ...

## 5. Shape

- **Storyboard:** ...
- **Key Features:** ...
- **Out of Scope:** ...

## 6. Validate

- **Approach:** ...
- **Success Metrics:** ...
- **Timeline:** ...

## Next Steps

- [ ] ...
```

Only include sections that have been completed so far. Append new sections as phases progress.

---

## Conversation Flow Rules

1. **Start** by greeting the Decider and asking them to describe their idea.
2. **After each decision**, give a brief encouraging acknowledgment (1 sentence), then move to the next choice or phase.
3. **Never present two decision points in the same message.** One AskQuestion per message.
4. **If the Decider seems stuck**, offer a recommendation with reasoning but still let them choose.
5. **At the end**, present the full sprint document and suggest concrete next steps.

## Error Handling

- If the user's idea is too vague, ask one clarifying question before Phase 1.
- If the user wants to go back to a previous phase, allow it — update the file accordingly.
- If the user wants to skip a phase, gently explain why it matters but respect their choice if they insist.
