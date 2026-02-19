# S3 Collaboration Examples

Concrete workflows showing S3 patterns applied to human-agent-subagent collaboration.

## Example 1: Feature Request (Full Governance Cycle)

**Scenario**: User asks "Add dark mode to the app."

### Step 1: Navigate via Tension
The human identifies a need (user request = driver).

### Step 2: Describe the Driver
```markdown
# docs/drivers/2026-02-05-dark-mode.md

## Current Conditions
Users have requested dark mode support. The app currently only has a light theme.

## Effects
Users in low-light environments report eye strain. Some users avoid the app at night.

## Relevance
Impacts user retention and satisfaction -- core to the project's purpose of serving users well.

## Priority
Medium

## Status
Open
```

### Step 3: Determine Requirement
Agent clarifies with human:
- **Intended outcome**: Users can toggle between light and dark themes
- **Enabling conditions**: Theme preference persists across sessions; all components support both themes

### Step 4: Form Proposal (using subagents)
Agent delegates exploration to parallel subagents:

```
Subagent 1 (explore): "How is theming currently implemented in this codebase?"
Subagent 2 (explore): "What CSS-in-JS or design token patterns exist in this project?"
```

Agent synthesizes findings into a proposal:
- Use CSS custom properties for theme tokens
- Add ThemeProvider context component
- Store preference in localStorage
- Respect OS-level prefers-color-scheme

### Step 5: Consent Decision
Agent presents proposal to human. Human checks for objections:
- "What about SSR flash?" → Objection resolved: add script in `<head>` to set class before paint
- No further objections → Proceed

### Step 6: Implement (Operations)
Agent creates todo list and works through it:
```
- [x] Define color tokens for light/dark
- [x] Create ThemeProvider component
- [x] Add toggle UI in settings
- [x] Update all components to use tokens
- [x] Add localStorage persistence
- [x] Handle SSR flash prevention
```

### Step 7: Record & Evaluate
```markdown
# docs/logbook/2026-02-05-dark-mode.md

**Date**: 2026-02-05
**Participants**: Human, Agent

## Driver
Users reported eye strain in low-light environments.

## Decision
Implemented CSS custom properties-based theming with light/dark toggle.

## Review Date
2026-03-05 (check user feedback metrics)
```

---

## Example 2: Creating a New Skill (Role Definition)

**Scenario**: The agent notices it keeps doing similar code review tasks. Time to formalize as a skill.

### Tension
Agent observes: "I've done 5 code reviews this week following the same pattern. This is a recurring domain."

### Proposal to Human
"I notice code review is a recurring task with consistent patterns. I propose creating a `code-review` skill to formalize the process. This would include review checklists, severity levels, and domain-specific standards."

### Human Consent
Human: "Go ahead, but include security checks as a mandatory step."

### Create the Skill (Domain Description)
```
.cursor/skills/code-review/
├── SKILL.md          # Domain: purpose, responsibilities, constraints
└── STANDARDS.md      # Reference: detailed coding standards
```

### SKILL.md follows domain description structure:
```markdown
---
name: code-review
description: Review code changes for quality, security, and maintainability. 
  Use when reviewing PRs, examining diffs, or when asked for a code review.
---

# Code Review

## Purpose (Primary Driver)
Ensure code quality and security across the project.

## Key Responsibilities
- Check logic correctness and edge cases
- Verify security best practices (MANDATORY)
- Assess readability and maintainability
- Verify test coverage

## Constraints
- Security checks are never skipped
- Reviews must reference specific line numbers
- Use severity levels: Critical / Suggestion / Nice-to-have

## Deliverables
Structured review with categorized findings.

## Review Schedule
Monthly: evaluate if review criteria need updating.
```

---

## Example 3: Delegating to Subagents (Circle Pattern)

**Scenario**: User asks "Refactor the authentication module to use JWT."

### Agent Forms a Circle (team)
This task has independent subtasks suitable for parallel delegation:

```
Human (Delegator)
  └── Agent (Coordinator / Governance)
        ├── Subagent 1 (explore): "How does auth currently work in this codebase?"
        ├── Subagent 2 (explore): "What are the JWT best practices for this stack?"
        └── Subagent 3 (explore): "What tests exist for the auth module?"
```

### Agent Provides Clear Domain Description in Each Task Prompt:
```
Subagent 1 prompt:
  "Explore /src/auth/ and related files. Describe:
   - Current authentication flow
   - Where sessions are created/validated
   - External dependencies
   Return a summary of the current auth architecture."
```

### Agent Synthesizes Results
After subagents return, the agent:
1. Merges findings into a coherent understanding
2. Creates a todo list for the refactoring
3. Implements changes sequentially (since code changes have dependencies)
4. Runs tests to validate

---

## Example 4: Governance Backlog (Accumulated Improvements)

**Scenario**: Over several sessions, tensions accumulate that aren't urgent but need addressing.

### Maintaining the Governance Backlog
Agent maintains a governance backlog in `docs/policies/governance-backlog.md`:

```markdown
# Governance Backlog

## Pending Items (prioritized)

1. **Review deployment skill** -- hasn't been updated since adding CI/CD
   - Driver: deployment process has changed
   - Priority: High
   - Owner: Human + Agent

2. **Define testing domain** -- no clear policy on test expectations
   - Driver: inconsistent test coverage across modules
   - Priority: Medium
   - Owner: Agent

3. **Evaluate research skill effectiveness** -- used 8 times, unclear value
   - Driver: token cost may exceed benefit
   - Priority: Low
   - Owner: Human
```

### Processing the Backlog
At the start of a governance-focused session:
1. Agent surfaces the backlog to human
2. Human and agent pick the top item
3. Follow the governance process (describe driver → determine requirement → propose → consent → implement)
4. Record the decision in the logbook

---

## Example 5: Standard Constraints (Cross-Domain Rules)

**Scenario**: Human wants to establish coding standards that apply everywhere.

### Standard Constraint = Cursor Rule

Create `.cursor/rules/coding-standards.mdc`:
```markdown
# Coding Standards

## When to Apply
All code changes in this project.

## Rules
- TypeScript strict mode required
- No `any` types without documented justification
- All public functions must have JSDoc comments
- Error handling: never swallow errors silently
- Tests required for all new features
```

This is a **standard constraint** in S3 terms -- it affects all domains in the project. Unlike a skill (which is domain-specific), a rule applies everywhere.

### Relationship Between Rules and Skills

| Aspect | Rule (`.cursor/rules/`) | Skill (`.cursor/skills/`) |
|---|---|---|
| S3 Equivalent | Standard Constraint | Role / Domain |
| Scope | All domains | Specific domain |
| Activation | Always active (or glob-matched) | On demand (when relevant) |
| Content | Constraints and boundaries | Capabilities and instructions |
| Governance | Human-defined | Human + Agent co-created |

---

## Example 6: Retrospective (Evaluate and Evolve)

**Scenario**: After completing a major feature, evaluate the collaboration.

### Agent-Led Retrospective
```
## Retrospective: Authentication Refactor

### What Worked
- Parallel subagent exploration saved time
- Clear domain descriptions in task prompts reduced confusion
- Incremental delivery allowed early feedback

### What Didn't Work
- Subagent for JWT best practices returned generic info (need to scope better)
- No governance record was kept for the architecture decision
- Testing skill wasn't invoked -- tests were written ad-hoc

### Actions
- [ ] Update subagent prompts to include project stack context
- [ ] Create logbook entry for auth architecture decision
- [ ] Create a testing skill for consistent test patterns
```

### Evolve Based on Learning
- Update the relevant skill's SKILL.md with lessons learned
- Add new items to the governance backlog
- Create new skills if recurring patterns emerged
