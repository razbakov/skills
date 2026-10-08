---
name: test-strategy
description: Write an actionable, risk-based QA test strategy (German "Testkonzept") for a product — diagnose the current test pyramid, map features to a 5x5 risk matrix, set quality gates and measurable KPIs, and deliver it as Markdown plus PDF. Use when the user asks for a test strategy, test concept, Testkonzept, QA strategy, QA plan for a product or codebase, test pyramid assessment, or quality gates / testing KPIs. Not for a single sprint or release test plan, and not for writing the tests themselves.
license: MIT
metadata:
  author: Vitali
  version: "1.1"
  category: strategy
---

# Test Strategy

Produce a QA strategy tailored to one product, team, and risk profile — a document that drives daily testing decisions, not a compliance artifact that collects dust. A team with 150 E2E tests and a 52-minute pipeline thinks it has good coverage; this skill diagnoses the inverted pyramid, prescribes the rebalance, and ties every element to a measurable KPI.

**Output:** one Markdown document with 13 numbered sections plus a PDF rendered from it, both at an agreed path (default `docs/qa-strategy.md` + `docs/qa-strategy.pdf`).

**Language:** write the document in the language the user asked in. A request for a "Testkonzept" means a German document — translate the section headings too, keep the `### N.` numbering so verification still works. Tool names and metric abbreviations (MTTR, E2E, CI) stay in English.

## Workflow

1. **Discover** — gather context (codebase first, then questions). See [Discovery](#discovery).
2. **Calibrate** — pick the team maturity level; it sets the document's depth.
3. **Draft** — fill the 13 sections in order, using [Section Guide](#section-guide). Copy the skeleton from `references/diagrams-and-worksheets.md`; borrow phrasing and realistic numbers from the worked examples in `references/strategy-templates.md`.
4. **Save** the Markdown file.
5. **Verify** — run the checks in [Verification](#verification). Fix and re-run until all pass.
6. **Render PDF** — `scripts/md-to-pdf.sh <file.md>` (relative to this skill). Read the first pages of the PDF to confirm tables and diagrams render.
7. **Deliver** — report both paths, the current → target pyramid in one line, and any open questions that blocked a number.

## Discovery

Ground the strategy in the real codebase before asking anything. Read the project's README, CLAUDE.md/AGENTS.md, and any `.agents/qa-project-context.md` — if that file exists, use it as the foundation and skip questions it already answers.

Count what exists instead of asking for it:

```bash
# test files per level — adapt globs to the stack
find . -path ./node_modules -prune -o -type f \( -name '*.test.*' -o -name '*.spec.*' -o -name 'test_*.py' \) -print | wc -l
ls e2e tests/e2e playwright cypress 2>/dev/null
cat package.json pyproject.toml 2>/dev/null | grep -iE 'vitest|jest|playwright|cypress|pytest|k6|axe'
ls .github/workflows .gitlab-ci.yml bitbucket-pipelines.yml 2>/dev/null
gh run list --limit 20 --json conclusion,createdAt,updatedAt 2>/dev/null   # CI duration + failure rate
```

Classify each test file as unit / integration / E2E by what it touches (pure functions vs. DB/HTTP vs. browser), not by folder name alone.

Then ask only what the code cannot tell you:

- **Product & business:** what the product is and who uses it; the business-critical flows (signup, checkout, payment, data export); release cadence; compliance needs (SOC2, HIPAA, PCI-DSS, GDPR, EU AI Act).
- **Current state gaps:** current coverage and flakiness if CI does not expose them.
- **Pain points & goals:** biggest quality pain; what broke in the last 3 releases and what escaped to production; what "good enough" looks like; appetite for test-infrastructure investment.
- **Team & constraints:** team size and composition (devs, QA, SDET, manual testers); automation skill; tooling budget; deadline pressure.

Ask in one batch. If the user cannot answer something, write the section with a clearly marked assumption rather than stalling.

### Calibrate to team maturity

Record `team_maturity` in `.agents/qa-project-context.md` if the project uses that file.

- **startup** — minimal pyramid: unit tests + a handful of critical E2E paths. Skip contract testing and formal metrics until CI runs reliably. Phase 1 under 4 weeks. ~5 pages.
- **growing** — full pyramid with coverage targets, flakiness thresholds, and CI quality gates. Add risk-based prioritization.
- **established** — SLA-backed quality gates, multi-environment coverage, advanced tooling (contract testing, chaos, observability), formal review cadence.

## Core Principles

1. **Risk-based prioritization over exhaustive coverage.** A payment bug costs 1000x more than a tooltip typo. Allocate testing effort by business risk, not code volume — the risk matrix decides where to invest.
2. **Test pyramid health is the leading indicator.** Many fast unit tests, fewer integration, fewest E2E. An inverted shape means slow feedback, high maintenance, and paradoxically low confidence. Diagnose the current shape before prescribing anything.
3. **Shift left.** Every defect found later costs exponentially more. Static analysis before tests, unit before integration, contract before E2E. Design reviews catch architecture bugs no test can find.
4. **Every strategy element has a KPI.** Each section names a number and a tracking cadence. If success cannot be stated as a number, question whether the element belongs.
5. **Living document.** Reviewed quarterly at minimum, with a revision history, a named owner per section, and explicit re-evaluation triggers (new product area, team change, major incident, defect escape).

## Section Guide

The output follows the 13-section skeleton in `references/diagrams-and-worksheets.md`. Header line: `# QA Strategy: <Product>` then `## Version X.Y | Last Updated: <YYYY-MM-DD> | Owner: <Name>`. Tailor depth to complexity — a 5-person startup needs 5 pages, not 50.

### 1. Executive Summary

One paragraph: what the product is, which flows carry the most risk, the headline targets (escape rate, CI time), and the shape change the strategy drives (e.g. "ice cream cone → pyramid over two quarters"). Write it last.

### 2. Scope & Objectives

- **In scope:** every product area, service, and integration covered; functional and non-functional test types; platforms, browsers, devices.
- **Out of scope:** what is NOT covered and why — third-party services tested only at the contract level, legacy systems slated for deprecation.
- **Objectives:** 3–5 measurable objectives with timelines, e.g. "Reduce defect escape rate from 12% to under 5% within two quarters."

### 3. Test Levels & Types

Define each level, what it validates, owner, framework, expected volume, and run frequency.

| Level | What It Validates | Owner | Framework | Target Share / Count | Run Frequency |
|---|---|---|---|---|---|
| Unit | Functions, business logic, edge cases | Developers | Vitest/Jest/pytest | 70–80% of all tests | Every commit |
| Integration | Service interactions, DB queries, API contracts | Developers + QA | Supertest/pytest + Testcontainers | 15–20% | Every PR |
| E2E | Critical user journeys through the full stack | QA/SDET | Playwright/Cypress | 5–10% | Pre-deploy + nightly |
| API | Contract compliance, schemas, error handling | Developers | Playwright APIRequestContext/Schemathesis | Per endpoint | Every PR |
| Visual | UI regression, layout shifts, responsive | QA | Playwright/Argos/Chromatic | Key pages | Nightly |
| Performance | Response times, throughput, resource usage | DevOps/QA | k6/Lighthouse | Critical paths | Weekly + pre-release |
| Security | OWASP Top 10, dependency vulns, auth flows | Security/DevOps | OWASP ZAP/Snyk | Per release | Pre-release + scheduled |
| Accessibility | WCAG 2.2 AA, screen-reader compatibility | QA/Frontend | axe-core | Key flows | Every PR |

Keep only the rows the product needs. Every product needs unit and integration; not every product needs visual regression. State what stays **manual** (exploratory testing, new features before they stabilize) and why.

### 4. Test Pyramid Analysis

**Shape.** The suite takes one of four shapes — healthy pyramid, ice cream cone (E2E-heavy), diamond (integration-heavy), hourglass (missing integration middle). Include the matching ASCII diagram from the reference file.

**Current state.** From the discovery counts: tests per level, percentage split, shape, CI duration, flaky rate, pass rate (Current State Worksheet).

**Target state.** Target ratios (70–80 / 15–20 / 5–10) with concrete counts, target CI duration and flaky rate, and a date (Target State Worksheet). Percentages must sum to ~100%.

**Action plan — ice cream cone or diamond:**

1. Freeze E2E growth — no new E2E unless it covers a net-new critical path.
2. Decompose existing E2E — a checkout E2E asserting tax math becomes a unit test on the tax function.
3. Add unit-test requirements to the PR checklist for any change touching business logic.
4. Set a CI gate that fails PRs when the unit:E2E ratio drops below threshold.

Before rebalancing, separate genuinely flaky E2E tests from ones exposing real bugs — quarantining a flaky test that hides a race condition is how the regression escapes.

**Action plan — hourglass:** invest in integration infrastructure (DB fixtures, service stubs, contract tests); identify every service boundary and give each happy-path + error-case integration tests; use contract testing (e.g. Pact) between services.

### 5. Risk Assessment

Score each feature area Impact (1 Negligible → 5 Catastrophic) × Likelihood (1 Rare → 5 Almost Certain). The product (1–25) maps to a band via the 5x5 matrix in the reference file. Include the matrix and a feature mapping table; the band decides testing depth through this **Risk-to-Testing Action Map**:

| Risk Level | Testing Action | Automation | Monitoring |
|---|---|---|---|
| CRITICAL (15–25) | Full automation + manual exploratory + load test | Mandatory, every commit | Real-time alerts, synthetic monitoring |
| HIGH (10–14) | Full automation + periodic manual review | Mandatory, every PR | Dashboard + daily checks |
| MEDIUM (5–9) | Automate happy path + key error cases | Recommended | Weekly review |
| LOW (1–4) | Manual testing or skip | Optional | None required |

Example mapping:

| Feature Area | Impact | Likelihood | Score | Testing Approach |
|---|---|---|---|---|
| Payment processing | 5 | 3 | 15 – CRIT | E2E + unit + contract + monitoring |
| User authentication | 5 | 2 | 10 – HIGH | E2E + security scan + unit |
| Product search | 3 | 3 | 9 – MED | Unit + integration + happy-path E2E |
| Dashboard rendering | 2 | 3 | 6 – MED | Unit + visual regression |
| Email preferences | 1 | 2 | 2 – LOW | Manual verification |

Use the Feature Inventory Template in `references/strategy-templates.md` to list features systematically. For AI/LLM features add explicit risk classes: hallucination, bias, prompt injection, privacy.

### 6. Environment Strategy

| Environment | Purpose | Test Types | Data | Deploy Trigger |
|---|---|---|---|---|
| Local | Developer feedback | Unit, integration | Mocked/seeded | On save |
| CI | Automated validation | Unit, integration, lint, SAST | Ephemeral | On push/PR |
| Staging / Preview | Pre-production validation | E2E, visual, performance, security | Production-like (anonymized) | On merge / per PR |
| Production | Monitoring & smoke | Smoke, synthetic monitoring | Live | On deploy |

Also document: test-data management per environment, ephemeral (preview deploys) vs. long-lived, who has access, how environment config is managed.

### 7. Tool Selection

Never lead with tools. State what must be validated, then score candidates:

| Criteria (weight) | Tool A | Tool B | Tool C |
|---|---|---|---|
| Fits tech stack (25%) | | | |
| Team familiarity (20%) | | | |
| Community & docs (15%) | | | |
| CI integration (15%) | | | |
| Maintenance cost (10%) | | | |
| Speed of execution (10%) | | | |
| License cost (5%) | | | |
| **Weighted total** | | | |

Score 1–5, multiply by weight, sum. Weigh total cost of ownership: setup, time to write 5 real tests, breakage on framework updates, debug time, infrastructure (browser farms, parallel runners). If the team already uses a tool that scores acceptably, keeping it is a valid decision — say so.

Common starting points (document why you chose or deviated):

| Product Type | Unit | Integration | E2E | API | Visual |
|---|---|---|---|---|---|
| React / Next.js SaaS | Vitest | Testing Library + MSW | Playwright | Supertest | Playwright screenshots |
| Vue / Nuxt SaaS | Vitest | Testing Library + MSW | Playwright | Supertest | Playwright screenshots |
| Python API | pytest | pytest + Testcontainers | pytest + requests | Schemathesis | — |
| Mobile (React Native) | Jest | Testing Library + MSW | Detox / Maestro / Appium | Supertest | Appium screenshots |
| AI/LLM features | Vitest | DeepEval | Playwright + Promptfoo evals | Promptfoo / Ragas | — |

**CI scaling levers** — when the suite grows, pull these before deleting tests, and put the matching metric in section 10:

- **Sharding** across N runners (Playwright `--shard=1/4`, Jest `--shard`, pytest-xdist).
- **Test impact analysis** — run only tests affected by the diff on PRs (Nx affected, Vitest `--changed`, Bazel); keep the full suite on merge/nightly.
- **Caching** dependencies, build artifacts, browser binaries.
- **Selective E2E** — smoke on PR, full on merge/nightly.

Parallel efficiency = summed test time ÷ wall-clock time; it should approach the shard count. Track CI-minutes-per-PR so parallelization doesn't balloon billed compute.

Optional framing references, if the audience expects a standard: ISTQB (CTFL v4.0 vocabulary, Advanced Agile Tester, GenAI testing syllabus), Bach's Heuristic Test Strategy Model, ISO/IEC/IEEE 29119-3 (common expectation behind a German "Testkonzept"). Check current versions before citing them by number.

### 8. Entry/Exit Criteria

Write both for every level:

- **Unit** — Entry: code compiles, function has a documented contract. Exit: branches covered, edge cases tested, no skipped tests, coverage target met.
- **Integration** — Entry: unit tests pass, dependencies available or stubbed, test data seeded. Exit: all service boundaries tested, error paths validated, no flaky tests.
- **E2E** — Entry: integration passes, staging deployed, test accounts provisioned. Exit: all critical journeys pass, no open P0/P1, performance within SLA.
- **Release** — Entry: all levels pass, no open CRITICAL/HIGH defects, release notes drafted. Exit: production smoke passes, no anomalies during the bake window (30 min default — tune to deploy frequency and alert latency), rollback plan verified.

### 9. Quality Gates

Each gate names concrete pass/fail thresholds and is enforced in CI — a gate that can be clicked past is documentation, not a gate. Also state the Definition of Done that PR authors see.

- **PR gate:** unit + integration pass; coverage does not decrease; no new lint errors; SAST has no new high/critical; bundle size within threshold; one reviewer approval.
- **Merge gate:** PR gate passes; E2E smoke against preview deploy; branch up to date.
- **Deploy gate:** full E2E on staging; performance within benchmark; security scan passes; feature flags configured; rollback plan tested.
- **Nightly gate:** full E2E incl. edge cases; visual regression; load tests; accessibility scan; dependency vulnerability scan; results reviewed next morning by a named owner.

### 10. Metrics & KPIs

| Metric | Definition | Target | Cadence |
|---|---|---|---|
| Code coverage | Lines/branches covered by unit + integration | >80% critical services, >60% overall | Per PR |
| Test pyramid ratio | Unit:Integration:E2E split | 70:20:10 (±10%) | Monthly |
| Flakiness rate | % of runs with non-deterministic failures | <2% | Weekly |
| Defect escape rate | % of defects found in production | <5% | Per release |
| MTTR | Detection to fix deployed | <4h P0, <24h P1 | Per incident |
| CI pipeline duration | Push to green/red signal | <15 min PR, <30 min full | Weekly |
| CI parallel efficiency | Summed test time ÷ wall-clock | Approaching shard count | Weekly |
| CI-minutes-per-PR | Billed compute per PR run | Flat or decreasing | Monthly |
| Automation rate | % of regression cases automated | >80% | Quarterly |
| False positive rate | % of failures that are not real bugs | <5% | Weekly |

Set targets from the current baseline — 20%→90% coverage in one quarter is a fantasy, not a plan. Track trends, investigate spikes (a sudden flakiness jump is usually infrastructure), never use metrics to punish people. Drop rows that have no data source yet, or add the data source as a Phase 1 task.

### 11. Timeline & Milestones

Phase it; doing everything at once guarantees nothing is done well. Each phase has an exit criterion.

- **Phase 1 — Foundation (weeks 1–4):** risk assessment; CI with unit-test gate; baseline metrics; unit tests for the top 5 risk areas; E2E framework configured. *Exit: CI runs unit tests on every PR, baseline documented.*
- **Phase 2 — Coverage (weeks 5–10):** integration tests on all service boundaries; E2E for top 10 journeys; visual regression on key pages; test-data management; nightly runs. *Exit: every critical path has E2E, every API has integration tests.*
- **Phase 3 — Gates (weeks 11–14):** coverage gate; performance benchmarks in CI; security scanning; KPI dashboard. *Exit: all four gates enforced.*
- **Phase 4 — Optimization (weeks 15–20):** de-flake/quarantine; CI scaling levers; production synthetic monitoring; first quarterly review. *Exit: CI <15 min, flakiness <2%, revision 1.1 published.*
- **Ongoing:** quarterly strategy review, monthly metrics review, continuous maintenance.

Compress for a startup (Phase 1 only, then reassess); stretch for an established team with many services.

### 12. Risks to the Strategy Itself

What could stop this strategy from working, with a mitigation each: no QA capacity, deadline pressure freezing test work, flaky infrastructure eroding trust, a missing test-data source, tool migration cost, team turnover.

### 13. Revision History

Table: version, date, author, change summary. Version 1.0 is the initial draft. List the re-evaluation triggers (quarterly review, post-incident, new product area, team change).

## Anti-Patterns

- **100% coverage targets.** Diminishing returns past ~80%; set coverage per module by risk.
- **Ice cream cone.** CI 45+ minutes, tests break on every UI change, nobody trusts the suite. Freeze E2E, decompose downward.
- **Shelf document.** Written once, never updated — worse than none because it gives false confidence.
- **Tool-first thinking.** "We should use Playwright" is a tool choice masquerading as a plan.
- **No metrics.** A strategy without measurable targets is a wish list.
- **Testing in isolation.** If it lives only in a QA wiki, it doesn't exist. It must show up in PR templates, CI gates, and the Definition of Done.
- **Copy-paste strategy.** The worked examples are starting points; every section must reflect this product's risks, team, and constraints.
- **Automating everything immediately.** Automate regression; keep exploration manual, and say what stays manual.

## Verification

Run against the saved file before rendering the PDF:

```bash
DOC=docs/qa-strategy.md
grep -cE '^### [0-9]+\.' "$DOC"                       # expect 13
grep -nE '^\|' "$DOC" | grep -iE 'target|coverage|flak|mttr|escape'   # every KPI row has a Target
grep -niE 'revision|owner' "$DOC"                     # owner + revision history exist
grep -nE '\[(Product Name|Name|Date|X\.Y)\]|_____|TBD' "$DOC"   # expect nothing: no unfilled placeholders
```

Then by hand: target unit% + integration% + E2E% ≈ 100%; if sharding is recommended, a parallel-efficiency or CI-minutes target appears in section 10; every assumption made for a missing answer is marked as such.

## Done When

- Markdown and PDF both exist at the agreed path; the PDF was opened and its tables render.
- `grep -cE '^### [0-9]+\.'` returns 13.
- Pyramid targets have concrete counts and dates; percentages sum to ~100%.
- Entry and exit criteria exist for unit, integration, E2E, and release.
- Tool choices are backed by a weighted scoring matrix, not just named.
- All four gates (PR, merge, deploy, nightly) have pass/fail thresholds.
- Every KPI row has a Target and a Cadence.

## Related Skills

- `bdd-from-ux` / `user-story` — turn the CRITICAL and HIGH flows from section 5 into acceptance scenarios.
- `test-driven-development` — the day-to-day practice behind the unit layer.
- `sprint-planning` — schedule the Phase 1–4 work as tickets.
- `latex-pdf` — use instead of `scripts/md-to-pdf.sh` when the PDF needs custom typesetting or branding.

## Reference Files

- `references/diagrams-and-worksheets.md` — pyramid shape diagrams, current/target worksheets, the 5x5 risk matrix, and the 13-section output skeleton.
- `references/strategy-templates.md` — four worked strategies (SaaS, e-commerce, API-first, media), a step-by-step pyramid worksheet, and a feature-inventory template.
- `scripts/md-to-pdf.sh` — Markdown → A4 PDF via `marked` + headless Chrome. Usage: `md-to-pdf.sh <file.md> [out.pdf]`.
