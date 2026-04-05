---
name: portfolio-hiring-analysis
description: Analyze all projects in a portfolio to identify skill gaps, then recommend roles/teams to hire and produce job descriptions. Use when the user asks to figure out hiring needs, what roles to hire, team structure, or skill gaps across their projects.
---

# Portfolio Hiring Analysis

## Overview

Parallel deep-dive of every project in a portfolio to map tech stacks, maturity levels, feature gaps, and skill requirements. Synthesizes findings into a hiring strategy with prioritized roles and individual job descriptions ready for posting.

## When to Use

- When the user asks "what roles do we need?" or "who should we hire?"
- When planning team growth or restructuring
- When auditing skill coverage across a multi-project portfolio
- When creating job descriptions grounded in actual codebase needs

## Inputs

- **Project registry** — from `CLAUDE.md` or `PROJECTS.md` (project names, stacks, domains, status)
- **Project directories** — actual codebases on disk to analyze

## Process

### Step 1: Group Projects by Domain

Read the project registry and group active projects into logical domains (e.g., by business area, tech cluster, or team). Skip stale/archived projects unless explicitly requested.

### Step 2: Launch Parallel Exploration Agents

Spin up one Agent (subagent_type: Explore, thoroughness: medium) per domain group. Each agent analyzes every project in its group by examining:

- `package.json` / `requirements.txt` — dependencies, scripts, package manager
- `README.md` / `CLAUDE.md` — project purpose, status, conventions
- `src/` or `app/` structure — key modules, pages, components, server routes
- Database schema — `prisma/schema.prisma`, `drizzle/`, migrations
- CI/CD configs — `.github/workflows/`, `netlify.toml`, `vercel.json`
- Test coverage — test files, feature files, test infrastructure
- Docker setup — `Dockerfile`, `docker-compose.yml`
- LLM/AI integrations — LangChain, OpenAI, Anthropic SDK usage
- Content/marketing assets — docs, design files, brand guidelines

Each agent returns a structured summary per project:

```
## Project Name
**Status:** Active/PoC/MVP/Production/Stale
**Tech Stack:** Framework | ORM | DB | Deploy target
**Codebase Size:** ~N files, N pages, N components
**Key Features:** bullet list
**What's Missing/Incomplete:** bullet list
**Complexity Level:** LOW / MEDIUM / HIGH
**Skills Needed:** categorized by role type
```

Plus a cross-project summary table and skill requirements grouped by role.

### Step 3: Synthesize Hiring Recommendations

Once all agents report back, synthesize into:

1. **The Problem** — quantify the unsustainability (project count, LOC, framework count, test coverage, CI/CD gaps)
2. **Recommended Roles** — prioritized table with:
   - Role name
   - Priority (HIGH / MEDIUM-HIGH / MEDIUM)
   - Which projects it covers
   - Type (full-time / part-time / contract / freelance / commission)
3. **What You Don't Need (Yet)** — roles explicitly excluded with reasoning
4. **Team Structure** — core team vs extended team suggestion

### Step 4: Save Hiring Strategy

Save to `ikigai/hiring/strategy.md` with:
- Portfolio summary tables (per domain)
- Key findings (patterns, gaps, risks)
- Hiring plan (core + extended team)
- References to individual job descriptions

### Step 5: Create Individual Job Descriptions

One file per role in `ikigai/hiring/<role-slug>.md`. Each JD contains:

```markdown
# Role Title

**Priority:** HIGH / MEDIUM-HIGH / MEDIUM
**Type:** Full-time / Part-time / Contract / Freelance / Commission
**Location:** Remote / On-site / Hybrid

## Why This Role
1-2 paragraphs connecting role to portfolio needs.

## What You'll Work On
Bullet list: project name (stack) — specific scope.

## Required Skills
Bullet list with experience level hints.

## Nice to Have
Bullet list of bonus skills.

## Day-to-Day
What a typical week looks like.

## Metrics
How success is measured.

## Deliverables (for contract roles)
Numbered list with timelines.

## Compensation Model (for commission roles)
Terms and renegotiation timeline.
```

### Step 6: Present Summary

Show the user a concise priority table and ask if they want to:
- Adjust priorities or scope
- `hire agent X` to create an AI agent for any role
- Create budget/engagement model breakdown

## Output Files

```
ikigai/hiring/
  strategy.md                  # Portfolio analysis + hiring plan
  <role-slug-1>.md             # Job description per role
  <role-slug-2>.md
  ...
```

## Key Principles

- **Evidence-based:** Every recommendation traces back to actual codebase analysis, not assumptions
- **Parallel execution:** Use sub-agents per domain to maximize speed
- **Prioritized:** Roles ranked by project coverage and revenue impact
- **Actionable:** Job descriptions ready to post, not abstract wishlists
- **Minimal team:** Prefer fewer roles covering more projects over specialized silos
