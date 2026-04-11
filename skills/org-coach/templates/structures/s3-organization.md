# Workspace Structure Presets

Choose a preset during Phase 1. The chosen structure is recorded in CLAUDE.md so every agent and future conversation knows where to find things.

## Preset: kebab (default)

Lowercase kebab-case. No number prefixes — ordering is handled by sidebar config, not filenames. `index.md` for the main doc in each folder (cleaner URLs). Short descriptive names. Web-friendly.

```
organization/
  driver.md
  canvas.md
  strategy.md
  values.md
  policies/
    <policy-name>.md
  domain-map.md
domains/
  <domain-name>/
    index.md
    <operations-docs>.md
roles/
  <role-name>/
    index.md
coordination/
  review-schedule.md
  work-board.md
.claude/agents/
```

Best for: standalone governance repos, VitePress/docs sites, organizations where the logbook IS the project.

## Preset: docs

Everything under `docs/`. Good for projects where code is the main content and governance lives alongside it.

```
docs/
  organization/
    driver.md
    canvas.md
    strategy.md
    values.md
    policies/
    domain-map.md
  domains/<domain-name>/
    index.md
  roles/<role-name>/
    index.md
  coordination/
.claude/agents/
```

Best for: software projects, monorepos, teams where governance lives alongside code.

## Preset: flat

Minimal nesting. Good for small teams where simplicity matters more than formal structure.

```
organization/
  driver.md
  canvas.md
  strategy.md
  values.md
  policies/
domains/<domain-name>/
  index.md
roles/<role-name>.md
coordination/
.claude/agents/
```

Best for: small teams (2-5 people), early-stage projects, experiments.

## Preset: custom

Ask the user to specify their own paths. Start from any preset and modify.

## How to use

During Phase 1, present the presets and let the user choose. Then:

1. Create the directory structure
2. Record the structure in CLAUDE.md under a `## Structure` section
3. All subsequent phases read CLAUDE.md to know where to put files
4. Agent definitions reference CLAUDE.md, not hardcoded paths

The CLAUDE.md structure section should list each artifact type and its path — this becomes the single source of truth for file locations.
