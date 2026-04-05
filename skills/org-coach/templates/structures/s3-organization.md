# Workspace Structure Presets

Choose a preset during Phase 1. The chosen structure is recorded in CLAUDE.md so every agent and future conversation knows where to find things.

## Preset: numbered (default)

Numbered top-level directories. Clear hierarchy, good for governance-heavy organizations.

```
00_Organization_Logbook/
  01_Primary_Driver_and_Requirement.md
  02_Organization_Canvas.md
  03_Strategy.md
  04_Values.md
  Org_Wide_Policies/
  Requirements_Mapping/
  Organizational_Structure/
01_Domains/<Domain_Name>/
  Domain_Description.md
  Governance/Backlog/
  Operations/Backlog/
  Metrics/
02_Roles/<Role_Name>/
  Role_Description.md
03_Coordination/
.claude/agents/
```

Best for: standalone governance repos, organizations where the logbook IS the project.

## Preset: docs

Everything under `docs/`. Good for projects where code is the main content and governance lives alongside it.

```
docs/
  governance/
    primary-driver.md
    organization-canvas.md
    strategy.md
    values.md
    policies/
    requirements/
    structure/
  domains/<domain-name>/
    description.md
    governance/backlog/
    operations/backlog/
    metrics/
  roles/<role-name>/
    description.md
  coordination/
.claude/agents/
```

Best for: software projects, monorepos, teams that prefer kebab-case.

## Preset: flat

Minimal nesting. Good for small teams where simplicity matters more than formal structure.

```
logbook/
  primary-driver.md
  canvas.md
  strategy.md
  values.md
  policies/
domains/<domain-name>/
  description.md
  backlog/
  operations/
  metrics/
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
