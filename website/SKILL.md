---
name: website
description: A content-first, mobile-first methodology for creating modern websites. Use this prompt when starting any new website project.
---

## Deliverables

Create two files at the project root before implementation:

1. **`plan.md`** — Strategy, design system, and architecture (Steps 1–4). Include: project context, vision & personas, brand voice, content model, design tokens, and technical decisions.

2. **`content.md`** — Actual copy for the site: headlines, body text, CTAs, microcopy. Write content here first, then implement in code.

Reference both files during implementation to stay aligned with the plan and approved content.

---

## Step 1: Gather Project Context

Before any design or code, ask:

1. **Purpose**: What is the primary goal of this website?
2. **Target audience**: Who will use this site? What do they want?
3. **Desired action**: What should visitors do? (sign up, buy, contact, etc.)

---

## Step 2: Define Content Strategy

### Vision Statement

Write a single statement:
_"For [target users] who [need/want], [product name] offers [value proposition] - [key differentiator]."_

### User Personas

Define 2-4 user types with:

- Name/archetype
- Primary motivation
- Pain points
- Expected behavior on site

### Brand Voice

Define tone and language style:

- Tone (e.g., friendly, authoritative, playful, cryptic)
- Language rules (formal vs casual, punctuation preferences)
- Words to use / words to avoid

### Content Model

Map each section in a **table** (Section | Purpose | Content Type | Priority, or Section | Purpose | Content). Keep it strategy-level: what each section is for and what content it holds—not how it looks or is built.

**Good:** Table rows with purpose + content type/description + optional priority. Example: `Hero | Establish mystique and VIP tone | Headline, subhead, CTA | P0`.

**Bad:** Numbered "Page Sections" with long bullet lists that describe layout ("full viewport"), visual design ("dark gradient", "gold accent"), or UI ("email input + submit button"). That mixes content strategy with design/implementation and belongs in Design System or Technical Architecture, not the Content Model.

| Section | Purpose | Content Type | Priority |
| ------- | ------- | ------------ | -------- |

**Content principles:**

- Truncation is not a content strategy—write proper summaries
- Build systems of content (small/medium/large variants)
- Max 5 main nav items
- All content available on all devices (never hide based on viewport)

---

## Step 3: Design System

### Aesthetic Direction

Define the visual identity:

- **Aesthetic pillars**: 3-4 words that capture the feeling (e.g., "minimal, warm, playful")
- **Iconography & imagery**: Photo style, icon style, recurring motifs

### Design Tokens

1. **Colors**: Primary, secondary, accent, text, background
2. **Typography**: Heading font, body font, sizes, line heights
3. **Spacing**: Consistent scale (4, 8, 16, 24, 32, 48, 64px)
4. **Shadows/Effects**: Elevation levels if needed

### UI Components

- Button styles, hover/focus states
- Form inputs, borders, cards
- Keep sharp or rounded consistently

### Design Principles

- **Consistency**: Same style components in same places
- **Signal-to-noise**: Maximize content, minimize chrome
- **No dark patterns**: Never trick users or hide important info
- **Grids**: Content-based, not generic 12-column

---

## Step 4: Technical Architecture

### Tech Stack

- bun
- nuxt
- tailwind

### Project Structure

```
project/
├── plan.md                  # Strategy, design system, architecture
├── content.md               # Site copy: headlines, body, CTAs
└── src/                     # Nuxt app (self-contained)
    ├── package.json
    ├── nuxt.config.ts
    ├── app/
    │   ├── app.vue
    │   └── pages/
    │       └── index.vue
    ├── components/
    │   ├── base/            # Buttons, typography
    │   ├── layout/          # Header, footer, grid
    │   └── section/         # Hero, features, etc.
    ├── assets/
    │   └── css/             # Styles, design tokens
    └── public/
        └── images/          # Optimized images
```

Nuxt component auto-import (default): Components in nested folders include the folder path in their name. components/section/Hero.vue → <SectionHero />.

### Setup Workflow

1. Create project folder
2. Add `plan.md` and `content.md` at root
3. Create `src/` folder and scaffold Nuxt inside: `bun create nuxt@latest src`
4. Run all Bun commands from `src/`: `bun install`, `bun run dev`, etc.

### Component Guidelines

- **Base**: Style raw elements (h1-h6, p, buttons)
- **Layout**: Page structure, grids, spacing
- **Sections**: Combine base + layout for page sections
- Each component should be self-contained and reusable

---

## Step 5: Responsive Design (Mobile-First)

1. **Start mobile**: Design smallest viewport first, enhance upward
2. **One codebase**: Same HTML for all devices
3. **Source order matters**: HTML order = accessibility order

### Implementation

- CSS mobile-first, use `min-width` media queries to enhance
- Flexible grids and fluid typography
- Breakpoints based on content needs, not device sizes
- Test on real devices

---

## Step 6: Performance

- Optimize images (WebP, responsive sizes, lazy load below-fold)
- Minimize JavaScript; load scripts after content
- Use appropriate caching headers
- Test with Lighthouse and set project-specific budgets

---

## Step 7: Accessibility & SEO

### Accessibility

- Semantic HTML (nav, main, article, aside)
- Alt text for all images
- Keyboard navigable
- Sufficient color contrast

### SEO

- Descriptive title tags and meta descriptions
- Proper heading hierarchy (one h1, logical h2-h6)
- Structured data where appropriate
- Fast load times

---

## Step 8: Progressive Enhancement

1. Start with semantic HTML that works without CSS/JS
2. Add CSS for visual design
3. Add JavaScript for enhanced interactions
4. Use feature detection (not browser detection)

---

## Anti-Patterns to Avoid

- **Carousels**: First item gets 90% of clicks
- **Large background images**: Heavy, invisible on mobile
- **Hover-only information**: Inaccessible on touch
- **Auto-playing media**
- **Content pagination**: Users prefer scrolling
- **Text as images**: Inaccessible, not scalable
- **Device detection**: Never serve different content by device
- **Assuming screen size = capability**
- **Requiring JavaScript for core content**
