---
name: bdd-from-ux
description: Write BDD scenarios grounded in existing UI/UX implementation. Researches pages, components, types, and mock data before writing any scenario. Use when generating .feature files for a product that already has a working app or prototype.
allowed-tools:
  - Agent
  - Bash
  - Read
  - Grep
  - Glob
  - Write
  - Edit
---

# BDD from UX

Write BDD scenarios that reflect the **actual** UI/UX, not imagined flows. Every scenario must be traceable to real components, pages, types, or mock data in the codebase.

## The Problem This Solves

When writing BDD scenarios from backlog stories alone, AI invents UI patterns that don't exist: forms instead of swipe decks, browse pages instead of sidebar sections, modal flows in the wrong order. These scenarios are worse than useless — they document a product that doesn't exist and mislead implementers.

## Process

### Step 1: Identify what stories need scenarios

Read the backlog and story map to understand which stories need `.feature` files. Group tightly related stories into one file per epic or feature area.

### Step 2: Research the actual UX — one subagent per feature area

Before writing a single scenario, spawn **one Explore subagent per feature area** to gather UX facts from the codebase. Each subagent must answer:

1. **Where does this feature live?** Which page/route, which component, which section of the page?
2. **What is the interaction model?** Swipe cards? Form? Toggle? Sidebar section? Modal? Inline? How does the user trigger and complete the action?
3. **What are the exact UI elements?** Read the component template. What buttons, labels, badges, icons, progress bars, placeholders, and states exist? Quote exact text strings.
4. **What data model backs it?** Read the TypeScript types. What fields exist? What are the valid values? How are they displayed?
5. **What are the states and transitions?** Empty state, loading, partial, full, error, success — what does the component render for each?
6. **What gates or triggers exist?** Auth gates? Freemium paywalls? Onboarding prerequisites? What exact action/headline/message appears?
7. **What mock data reveals the UX?** Read mock data files to see realistic examples of how data is structured and displayed.

**Search locations for each subagent:**
- `app/pages/` — routes and page-level logic
- `app/components/` — UI components (read the `<template>` section carefully)
- `app/types/` — TypeScript interfaces and type unions
- `app/data/` — mock data revealing realistic content
- `app/composables/` — shared state and business logic
- `app/lib/` — utility functions (display helpers, formatters)

**Subagent prompt template:**
```
Research the UX for [FEATURE AREA] in [APP PATH].

I need to write BDD scenarios that match the real implementation. For each question below, quote the actual code — component names, template strings, type definitions, mock data values:

1. Which page route and component renders this feature?
2. What is the interaction model? (swipe, form, toggle, sidebar, modal, etc.)
3. What exact UI elements exist? (buttons, labels, badges, icons, states — quote template strings)
4. What TypeScript types/interfaces back this feature? (quote the type definition)
5. What states does the component handle? (empty, loading, partial, full, success, error, disabled)
6. What gates exist? (auth, paywall, onboarding — quote the trigger logic and headlines/messages)
7. What does the mock data look like? (quote 2-3 realistic examples)

Search broadly in pages/, components/, types/, data/, composables/, lib/. DO NOT write code. Just research and quote findings.
```

### Step 3: Write scenarios grounded in research

Only after all subagents return, write the `.feature` files. Every scenario must satisfy:

**Grounding rules:**
- UI interactions must match the actual component (swipe right, not "click Join")
- Text strings in Then steps must match actual template strings (quote from component)
- Data tables must use actual type fields and valid values (from TypeScript types)
- States (empty, full, disabled) must match actual component conditionals
- Gate triggers must use actual action names and exact headline strings
- Feature areas that don't exist yet in the UI must have a `# Note:` comment explaining what pattern they extend

**Scenario quality rules (from bdd-scenarios skill):**
- One behavior per scenario
- Declarative: describe what, not how (no "I click the button", but "I tap 'Save profile'")
- Business-focused: use domain language
- Independent: no dependencies on other scenarios
- 3-7 steps per scenario
- Happy path first, then edge cases
- Use `Rule:` blocks for acceptance criteria
- Use `Background:` for shared setup
- Use `Scenario Outline:` with `Examples:` for data-driven variations
- Tags: `@epic-N`, `@mvp`, `@r1`, `@r2`, `@wip`

**Template:**
```gherkin
@epic-N @mvp
Feature: Feature name
  As a Persona
  I want to action
  so that benefit.

  Background:
    Given shared precondition

  Rule: Business rule derived from actual UI behavior

    Scenario: Happy path matching real UX
      Given concrete precondition with real data
      When user action matching actual interaction model
      Then observable outcome with actual UI text/state
```

### Step 4: Cross-check before writing files

Before writing each `.feature` file, verify:
- [ ] Every `When` step matches an actual interaction in the component
- [ ] Every `Then` step matches an actual UI state or text string
- [ ] Data tables use fields from actual TypeScript types
- [ ] Gate/paywall scenarios use exact headlines from the code
- [ ] Features not yet built are clearly annotated with `# Note:`

## Anti-patterns

| Don't | Do |
|-------|-----|
| Invent UI flows from story titles | Read the component template first |
| Assume forms exist for every input | Check if it's a swipe card, toggle, or sidebar section |
| Use generic headlines like "Sign up" | Quote the exact headline from the SignUpModal component |
| Write "I click the Join button" | Match the real interaction: "I swipe right" or "I tap 'Join this dinner'" |
| Assume separate pages per feature | Check if features share a page (e.g., everything on the festival page) |
| Skip features that aren't built yet | Write scenarios with a `# Note:` explaining the design intent |

## When to Use This Skill

- Writing `.feature` files for a product that already has UI components
- Updating scenarios after the UI has changed
- Auditing existing scenarios against the actual implementation
- Onboarding to a codebase by documenting actual behavior as scenarios
