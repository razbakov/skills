---
name: app
description: Documentation-first, test-driven development workflow for building applications. Use when starting new features, implementing functionality, or following structured development processes. Guides through phases: vision, architecture, data modeling, integration tests, unit tests, and implementation.
---

See README.md for project details

# Rules

- Do one thing at a time, and suggest [Next Steps](docs/next-steps.md). Let human review and confirm before proceeding.
- Next steps should be very short and simple, without overexplanation.
- In the document-first phase, when brainstorming or documenting, make change in one file and write next steps in the document, wait for confirmation.
- ALWAYS run tests with test database so that user don't loose data.
- You can run specific feature file `pnpm test:feature __tests__/integration/content-extraction.feature`.
- When executing commands, you don't need to change directories. If you want to run pnpm, just run pnpm. NOT `cd ... && pnpm ...`

# Development Process

This project follows a structured, documentation-first and test-driven approach. Always start with documentation (README, architecture, types), then tests, then implementation. Guide users through these phases in order.

## Technology Stack Defaults

Unless specified otherwise in project documentation, use these defaults:

- **Package Manager**: pnpm
- **Framework**: Nuxt.js (following Nuxt best practices)
- **Styling**: Tailwind CSS
- **UI Components**: vue-shadcn
- **Icons**: nuxt-icon
- **Backend**: Postgres, Prisma, trpc, zod

**Important**: If technology stack is not already documented in README or architecture docs, confirm these defaults with the user before proceeding.

## Phase 1: Vision & High-Level Planning (README)

- **Start Here**: README.md defines the product vision
- Keep it scannable and user-focused
- Document what the system does, not how it works
- Update as vision evolves, but keep concise

## Phase 2: Architecture Design

Before writing any code, define technical architecture:

- **Create**: `docs/architecture.md`
- **Define**: System components, data flow, technology choices
- **Document**: High-level technical decisions and rationale
- **Questions to answer**:
  - What are the main system components?
  - How do they communicate?
  - What external services are needed?
  - What frameworks/libraries are we using? (see Technology Stack Defaults above)

## Phase 3: Data Modeling

Define data structures before implementation:

- **Location**: Appropriate directory for your stack (e.g., `types/`, `models/`, `schemas/`)
- **Format**: Type definitions with documentation (TypeScript interfaces, JSON schemas, class definitions, etc.)
- **Coverage**: All domain models and business entities
- **Documentation**: Design decisions in relevant detail docs
- **Identify**: Core entities, their relationships, and data flows

## Phase 4: Integration Tests

**Start from the end** - Write features before implementation:

- **Location**: Appropriate test directory (e.g., `__tests__/integration/`, `__tests__/e2e/`)
- **Format**: BDD/Gherkin syntax preferred (e.g., `.feature` files), or structured test suites
- **Purpose**: User stories, acceptance criteria, living documentation
- **Approach**:
  1. Write test scenarios describing user workflows
  2. Tests serve as specifications
  3. Easy for users/stakeholders to read, review, and adjust
  4. Tag incomplete tests (e.g., `@wip`) while in development
  5. Implement to make tests pass
  6. Outcome-focused: asserts persisted outcomes and keeps UI checks minimal
  7. Explicit data setup: uses "clean test database"
  8. Stable domain language: steps describe what the system does, not how the UI looks.

**Example structure**:

```gherkin
Feature: [Feature Name]

  Scenario: [Specific user workflow]
    Given [initial context/state]
    When [user action]
    And [additional actions]
    Then [expected outcome]
    And [verification step]
```

## Phase 5: Unit Tests

- **Purpose**: Catch regressions during development
- **Coverage**: Business logic, utilities, transformations
- **Framework**: Follow project testing conventions
- **When**: Write alongside implementation
- **Focus**: Edge cases, error handling, data transformations

## Phase 6: Implementation

Only after tests are defined:

- Implement features to make tests pass
- Follow TDD: Red → Green → Refactor
- Keep functions small and testable
- Document complex logic with comments

## Guiding Users Through the Process

**Documentation-First, Test-Driven Development**

When starting a new feature, follow this order:

1. **Documentation**: "Have we defined this in the architecture?" → If no, start with architecture docs
2. **Data Models**: "Do we have types for this data?" → If no, define type/schema definitions first
3. **Integration Tests**: "Have we written the test scenarios?" → If no, write integration tests first
4. **Implementation**: Implement the feature to make tests pass
5. **Unit Tests**: Write unit tests for edge cases and business logic

**Never skip to implementation without documentation and tests first.**

## Running Tests

Adapt commands based on your project's testing framework and package manager:

```bash
# Run all tests
npm test / pnpm test / yarn test

# Run integration tests
npm run test:integration

# Run specific test file
npm test path/to/test-file

# Skip WIP/incomplete tests (example for BDD)
npm test -- --tags "not @wip"
```

# Commit Message Rules

- Use Conventional Commits.
- Format: `<type>(<optional scope>): <short summary>`
- Types: feat, fix, refactor, chore, docs, perf, test
- Summary max 72 chars.
- Use imperative mood: "add", "fix", "remove".
- Do not mention specific filenames.
- Only include issue numbers if present in diff.
- Body is optional but when present:
  - Explain _why_, not _what_.
  - Wrap lines at ~80 chars.

# Documentation

## Single Source of Truth

- Code files (TypeScript/other) are the source of truth for data models
- Docs reference type/schema files via links, never duplicate schemas
- Keep data schemas in code, not in markdown

## Documentation Structure

- **README**: Very short overview
  - Keep it scannable (1 page max)
  - Key Features section with links to detail docs
  - All capabilities/details belong in component docs, not README
- **Detail docs**: Complete component documentation
  - Responsibility (1-2 sentences WHY this exists)
  - Capabilities (bullet list of WHAT it does)
  - Data Flow (Input/Output with type links)
  - Data Model (link to types + design decisions)
  - Implementation (tools, algorithms, rationale)
- **Schema/Type files**: Complete type definitions with documentation (JSDoc, comments, etc.)

## Writing Style

- No duplication between README and detail docs
- Avoid "here's how you could do it" - make concrete decisions
- Link to code files, don't paste code in docs
- User-facing names: prefer clear, verbose terms over jargon
- Linking style: Make feature names themselves clickable, avoid arrows/visual noise
  - Good: `**[Feature Name](link)**: description`
  - Bad: `**Feature Name** → [Details](link): description`
