All file paths below are relative to the engineering area defined in the workspace structure (README.md). Look up the actual directory before creating files.

# Phase 13: Architecture

Create `architecture.md` using → `templates/architecture.md`

**Rules:**
- Lead with an ASCII system diagram showing all layers and how they connect
- Technology choices table must have a Rationale column — "why this" not just "what"
- Include a project structure tree showing directory layout
- Define key domain concepts in a table (concept + description)
- Include a Mermaid ER diagram for the data model
- Describe the primary data flow as a numbered sequence
- Keep it high-level — link to code for specifics

# Phase 14: Decisions (ADRs)

Create `decisions/<NNN>-<slug>.md` using → `templates/adr.md`

**Rules:**
- Number sequentially: 001, 002, 003...
- Record decisions when they're made, not after
- "Superseded by ADR XXX" when a decision is replaced
- Focus on the *why* — the *what* is in the code

# Phase 15: Website / Landing Page

Use this phase when the product needs a marketing page, landing page, or any web presence. This is a content-first, mobile-first methodology — all copy is written before any code.

**Deliverables** (created before coding):

1. **`plan.md`** — Strategy + design system mapping
2. **`content.md`** — All copy: headlines, body, CTAs, microcopy

## Step 1: Content Strategy

Build on the product strategy and brand from earlier phases:

**Vision statement**: _"For [users] who [need], [product] offers [value] — [differentiator]."_

**Personas** (2–4, derived from the story map):

| Archetype | Motivation | Pain Points | Site Behavior |
|-----------|------------|-------------|---------------|

**Voice**: Tone, language rules, words to use/avoid — derived from the brand guide.

**Content model** — map sections by strategy, not layout:

| Section | Purpose | Content Type | Priority |
|---------|---------|--------------|----------|

**Principles**: Write full summaries (no truncation) · Content variants (S/M/L) · Max 5 nav items · Same content on all devices.

## Step 2: Design System Mapping

Translate tokens from the brand guide into CSS variables / Tailwind config — don't redefine them:

- **Colors** → CSS custom properties from brand color table
- **Typography** → font-family, sizes, weights, line-heights from brand typography table
- **Spacing** → spacing scale from brand spacing table
- **Effects** → border-radius, shadows from brand effects table
- **Aesthetic** → pillars and motifs from brand personality

**Design system principles:**
- The brand guide is the single source of truth — implementation maps, never duplicates
- Consistency across components
- Maximize signal, minimize chrome
- No dark patterns
- Content-based grids (not 12-column)

## Step 3: Write All Copy

Create `content.md` with every word that will appear on the site before touching code. This includes:
- Headlines and subheadlines
- Body copy for each section
- CTAs (primary and secondary)
- Microcopy (form labels, error messages, tooltips)
- Meta descriptions and page titles

## Step 4: Technical Setup

**Stack**: Bun + Nuxt + Tailwind (or match the project's existing stack).

```
<app>/
├── plan.md
├── content.md
└── src/
    ├── nuxt.config.ts
    ├── app/pages/index.vue
    ├── components/
    │   ├── base/       # Buttons, typography
    │   ├── layout/     # Header, footer, grid
    │   └── section/    # Hero, features
    ├── assets/css/
    └── public/images/
```

**Setup**:
- Prefer `bun` when installing dependencies
- Use `bunx nuxi@latest init` with `--template minimal --no-modules --packageManager bun --gitInit --force`
- Add modules separately with `bunx nuxi@latest module add`
- Run commands from `src/`

**Auto-import**: `components/section/Hero.vue` → `<SectionHero />`

## Step 5: Implementation

**Accessibility + SEO:**
- Semantic HTML (`nav`, `main`, `article`)
- Alt text, keyboard nav, color contrast
- One `h1`, logical heading hierarchy
- Meta descriptions, structured data

**Progressive Enhancement:**
HTML (works alone) → CSS (style) → JS (enhance) → Feature detection

**Anti-patterns to avoid:**
Carousels · large background images · hover-only info · autoplay media · pagination over scroll · text as images · device detection · JS-dependent core content
