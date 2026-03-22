# Skill Consolidation TODO

Based on [similarity report](./skill-similarity-report.md) from 2026-03-22.

## High Priority

- [ ] **Deduplicate `run-sprint` / `github-next-issue`**: Extract shared GitHub Project V2 logic (steps 1-4) or have `run-sprint` loop over `github-next-issue`
- [ ] **Delete or repurpose `workflow` skill**: It's a verbatim copy of CLAUDE.md `## Workflow Orchestration` — redundant in every session
- [ ] **Clarify 3 "implement issue" skills**: Define clear entry points for `github-issue` vs `developing-tickets` vs `thank-you-next` — consider shared implementation core

## Medium Priority

- [ ] **Align `year-review` with `personal-coach`**: Make `year-review` a quick-access alias that delegates to `personal-coach` assessment, or explicitly differentiate them
- [ ] **Simplify image generation routing**: Consider making `image-from-*` skills internal techniques of `brand-poster` rather than standalone skills

## Low Priority

- [ ] **Document `review-all-prs` → `pr-review-responder` relationship**: Already clean, just needs explicit documentation
- [ ] **Differentiate "start something new" skills**: Add a decision guide for `startup` vs `startup-coach` vs `project-start` vs `design-sprint`
