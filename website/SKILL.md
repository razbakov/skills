---
name: website
description: A content-first, mobile-first methodology for creating modern websites. Use this prompt when starting any new website project.
---

## Deliverables

Create at project root before coding:

1. **`plan.md`** — Strategy + design system (Steps 1–3)
2. **`content.md`** — All copy: headlines, body, CTAs, microcopy

Reference both during implementation.

---

## Step 1: Discovery

Ask before designing:

1. **Goal**: Primary purpose of the site?
2. **Audience**: Who uses it? What do they need?
3. **Action**: What should visitors do?

---

## Step 2: Content Strategy

### Vision

_"For [users] who [need], [product] offers [value] — [differentiator]."_

### Personas (2–4)

| Archetype | Motivation | Pain Points | Site Behavior |
| --------- | ---------- | ----------- | ------------- |

### Voice

- Tone (friendly/authoritative/playful)
- Language rules (formal vs casual)
- Words to use/avoid

### Content Model

Map sections — strategy only, not layout or visuals:

| Section | Purpose | Content Type | Priority |
| ------- | ------- | ------------ | -------- |

**Principles**: Write summaries (no truncation) · Content variants (S/M/L) · Max 5 nav items · Same content on all devices

---

## Step 3: Design System

### Tokens

- **Colors**: primary, secondary, accent, text, background
- **Typography**: heading/body fonts, sizes, line-heights
- **Spacing**: 4, 8, 16, 24, 32, 48, 64px
- **Effects**: shadows/elevation if needed

### Aesthetic

- 3–4 pillars (e.g., "minimal, warm, playful")
- Icon/image style, recurring motifs

### Principles

- Consistency across components
- Maximize signal, minimize chrome
- No dark patterns
- Content-based grids (not 12-column)

---

## Step 4: Technical Setup

**Stack**: Bun + Nuxt + Tailwind

```
project/
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

**Setup**: `bun create nuxt@latest src` → run commands from `src/`

**Auto-import**: `components/section/Hero.vue` → `<SectionHero />`

---

## Step 5: Implementation

### Accessibility + SEO

- Semantic HTML (`nav`, `main`, `article`)
- Alt text, keyboard nav, color contrast
- One `h1`, logical heading hierarchy
- Meta descriptions, structured data

### Progressive Enhancement

HTML (works alone) → CSS (style) → JS (enhance) → Feature detection

---

## Anti-Patterns

Avoid: carousels · large background images · hover-only info · autoplay media · pagination over scroll · text as images · device detection · JS-dependent core content
