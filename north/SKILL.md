---
name: north
description: Standards and process for building modern web projects with AI. Content-first, mobile-first, component-based methodology. Use when starting a new project, creating features, designing components, making architecture decisions, or when the user asks to build something for the web.
---

# North — Build Web Projects With AI

A content-first, mobile-first, component-based methodology for building modern web projects. Adapted from [North](https://github.com/north/north/) standards, updated for AI-driven development.

**Core belief**: AI generates code. Humans define intent. The better the intent, the better the output. North    is how you define intent.

## Process: From Vision to Shipping

Follow this sequence. Never skip a step. Each step feeds the next.

### 1. Vision Statement

Before anything — answer these questions in one paragraph:

- Who uses this product?
- What needs does it address?
- What makes it different?
- What does success look like?

> Without a vision statement, every AI prompt is a shot in the dark.

### 2. User Personas

Define 2-4 personas based on **how people use** the product, not demographics.

Each persona needs:
- Name and description of typical use
- Primary motivation (why they come)
- Pain points (what frustrates them)

Don't stereotype. Don't assume mobile users are rushed. Don't assume desktop users want more. **Users are the same people on every device.**

### 3. Content Model

Model your content types BEFORE any design or code. Each content type needs:

- **Title** and **description**
- **Benefit statement**: "As [persona], I want [desire] so that [rationale]"
- **Attributes** with data types and limits
- **Relationships** to other content types

Content lives longer than any presentation. Never tie content to a specific device, layout, or platform. No "mobile title" or "desktop image" — build systems of content with small/medium/large variants.

### 4. Information Architecture

Determine what content goes where and why. Rules:

- Most valuable content = most prominent
- Never truncate headlines
- Always provide summaries for long copy
- Max 5 main navigation items
- Max 3 navigation levels
- Don't restrict content based on screen size
- Don't paginate unnecessarily — users can scroll

### 5. Design System (Components, Not Pages)

**The page metaphor is dead.** Design reusable components and layouts, not pages.

- **Components** — the building blocks (buttons, cards, messages, menus)
- **Layouts** — the structure (how components are positioned)
- **Aspects** — variations of a component (primary, secondary, danger)
- **Elements** — individual pieces within a component (title, body, icon)
- **States** — behavioral changes (active, open, loading, error)

Design tokens (colors, spacing, typography scales) ensure consistency across all components.

### 6. Build Iteratively

Work in 2-week sprints. Each sprint:
- Commit to specific user stories
- Each story has benefit statement + requirements + size
- Ship working increments — not "almost done"
- Demo to stakeholders at sprint end
- Failed sprint = bad estimate, not failure. Adjust and continue.

## Principles That Never Change

### Content First

Users come for content. Everything else is decoration. Content is the most basic need — if it fails, nothing else matters.

**Website Hierarchy of Needs** (bottom to top):
1. **Content & Navigation** — can users find what they need?
2. **IA & Predictability** — do users feel safe navigating?
3. **Performance & Progressive Enhancement** — does it work everywhere?
4. **Branding** — does it look and feel right?
5. **Delight** — animations, interactions, the cherry on top

Each layer depends on the one below. Never sacrifice a lower layer for a higher one.

### Mobile First

Not "design for phones." Use mobile as a **focusing lens**:

- One eye, one thumb — what matters most?
- Prioritize ruthlessly
- Don't fill large screens with noise just because there's space
- What works for mobile works for everyone

### Progressive Enhancement

Start with semantic HTML. Layer CSS. Layer JS. Every layer is optional.

- Use `@supports` for CSS feature detection
- Use native `<picture>` and `srcset` for responsive images
- Use Container Queries for component-level responsiveness
- Use modern CSS (grid, flexbox, custom properties, nesting) — no frameworks needed for layout

### Performance Is a Design Constraint

Every design decision has a performance cost. Measure it.

**Targets (Core Web Vitals):**
- LCP (Largest Contentful Paint): < 2.5s
- INP (Interaction to Next Paint): < 200ms
- CLS (Cumulative Layout Shift): < 0.1
- Total bundle: aim under 200KB JS (compressed)

**Rules:**
- Lazy load non-critical content
- Use modern image formats (AVIF > WebP > JPEG)
- SVG for icons and logos
- No render-blocking resources except critical CSS
- Async/defer all scripts
- Use a CDN

### One Codebase, No Device Detection

No "mobile site" vs "desktop site." One codebase. One URL. Responsive by default. Never hide content based on screen size. Never assume capabilities from viewport width.

### Accessibility From Day One

- Semantic HTML is the foundation
- Test with a screen reader (VoiceOver on Mac/iOS)
- Structured data via JSON-LD for SEO and machine readability
- Logical heading hierarchy
- Sufficient color contrast
- Keyboard navigable

## Anti-Patterns — Never Do These

- **Carousels** — only the first slide gets clicks
- **Auto-play media** — user triggers media, always
- **Dark patterns** — no tricks, no misdirection, no forced actions
- **Content insertionals** — don't interrupt reading flow
- **Hiding content** — if it's not worth showing, remove it entirely
- **Social share button spam** — good content gets shared organically
- **Page preloaders** — show content progressively, never block
- **Overlays on load** — respect the user's attention
- **Infinite everything** — paginate after 2-4 loads, then let user choose

### User Story Format for AI

When creating tasks:

```
As [persona], I want [desire] so that [rationale].

Requirements:
- [Specific, buildable requirement]
- [Another requirement]
- [Acceptance criteria]

Component: [which component this affects]
Content type: [which content model this uses]
```

### Version Control

- Feature branches per story
- Never commit directly to main
- PRs reviewed before merge
- Tag releases with semver (v1.0.0)
- Compiled output in .gitignore — build in CI

## Consistency Checklist

Before shipping any feature:

- [ ] Follows content model
- [ ] Uses existing components (or justifies new ones)
- [ ] Works without JS (core content accessible)
- [ ] Responsive from 320px up
- [ ] Accessible (keyboard, screen reader)
- [ ] Core Web Vitals within targets
- [ ] No anti-patterns
- [ ] Semantic HTML with JSON-LD where applicable
