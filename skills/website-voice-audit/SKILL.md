---
name: website-voice-audit
description: Use when reviewing a website's UI copy, content, and meta for brand voice consistency. Triggers include launching a new site, rebranding, noticing inconsistent tone across pages, or preparing content for SEO. Checks nav, CTAs, author bios, meta descriptions, blog posts, project descriptions, config files, and locale files against brand voice guidelines.
---

# Website Voice Audit

Systematically audit every text surface of a website against its brand voice guidelines. Produce a report of violations with concrete fixes.

## When to Use

- Before a site launch or rebrand
- When copy feels inconsistent across pages
- After migrating content from another site/template
- When blog posts span different time periods (voice drift)
- When locale files were translated without voice review

## Audit Checklist

### 1. Read Brand Voice Guidelines First

Find the voice/tone definition (usually in CLAUDE.md, brand docs, or style guide). Extract:

- **Tone keywords** (e.g., "direct, reflective, authentic")
- **Words to use** (e.g., "build, ship, validate")
- **Words to avoid** (e.g., "synergy, leverage, empower, impactful")
- **Writing style** (first person? casual? process-oriented?)
- **CTA style** (e.g., "Let's talk" > "Schedule a consultation")

### 2. Audit Every Text Surface

Check each surface against the guidelines. Read the actual files, don't guess.

| Surface | Where to find | Common violations |
|---|---|---|
| **Site config** | `config.json`, `nuxt.config.ts` | Generic `description`, dead marketing copy |
| **Navigation** | Nav components, i18n files | Corporate labels ("Schedule a Consultation") |
| **Homepage** | Hero, subtitle, CTAs | Template filler, banned words |
| **About page** | Bio, section headings, CTAs | LinkedIn-style corporate bio |
| **Blog subtitles** | i18n files, page components | Generic ("Sharing insights on topics I'm passionate about") |
| **Author bio** | Blog post template | Mismatch with personal voice |
| **CTA fallbacks** | i18n files | "Ready to Get Started?" / "Take the next step" |
| **Blog posts** | Content markdown files | Voice drift across years, emoji abuse, marketing hype |
| **Project descriptions** | Content markdown files | Third-person pitch deck voice vs first-person |
| **Meta descriptions** | `useSeoMeta`, i18n files | Generic or missing |
| **Footer** | App/layout component | Boilerplate |
| **Empty states** | Page components | Dev-facing text in production |
| **All locale files** | i18n directory | Translations that don't match voice |

### 3. Classify Violations

For each violation, note:

- **File and line** — exact location
- **Current text** — what it says now
- **Problem** — why it violates the voice (reference specific guideline)
- **Fix** — concrete replacement text

### 4. Prioritize

| Priority | Description |
|---|---|
| **P0** | Uses explicitly banned words |
| **P1** | Dead/template copy visible to users |
| **P2** | Inconsistent with voice but not terrible |
| **P3** | Could be better but functional |

## Report Format

```markdown
## Voice Audit: [site name]

### Voice Guidelines Summary
- Tone: ...
- Words to use: ...
- Words to avoid: ...

### Violations Found

| Priority | Location | Current | Problem | Fix |
|---|---|---|---|---|

### Blog Post Voice Assessment
| Post | Voice match | Issues |
|---|---|---|

### Recommendations
1. ...
```

## Blog Post Rewrites

When rewriting blog posts to match voice:

- **Keep**: frontmatter (dates, images, links, tags, CTAs), core ideas, code blocks, internal links
- **Remove**: emojis in headers, marketing hype, exclamation-mark emphasis, "Perfect For" audience sections, "Ready to revolutionize?" CTAs
- **Rewrite**: titles, descriptions, section structure, all body copy
- **Dispatch parallel agents** for independent post rewrites (one agent per post)
- **Spot-check** each rewrite: grep for emojis, verify no banned words, read opening and closing paragraphs

## Common Mistakes

- Auditing only English and forgetting locale files
- Fixing UI text but leaving meta descriptions in old voice
- Rewriting blog posts without preserving frontmatter links and CTAs
- Not checking config files for dead/unused marketing copy
- Over-correcting: CV pages should stay professional, not match casual blog voice
