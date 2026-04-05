---
name: content-seo-agent
description: AI content and SEO agent that audits sites, fixes indexing issues, writes blog posts aligned with OKRs, generates YouTube metadata, and produces monthly analytics reports. Use when asked to run SEO audit, write a blog post, create content calendar, fix indexing, generate YouTube descriptions, or produce an analytics report.
---

# Content & SEO Agent

AI agent that performs the work of a Content & SEO Marketer across the portfolio. Operates on 5 projects: DanceGods (SEO), razbakov.com (blog), web100 (lead gen content), ai-study-group (YouTube), SMM Manager (social distribution).

Reference: `ikigai/hiring/content-seo-marketer.md`

## Trigger Phrases

- "run SEO audit on [project]"
- "write a blog post about [topic]"
- "create content calendar"
- "fix indexing for [site]"
- "generate YouTube metadata for [video]"
- "analytics report"
- "content-seo sprint"

## Workflows

### 1. SEO Audit

**When:** "run SEO audit on [project]" or monthly check

**Process:**
1. Read the project's `nuxt.config.ts` to check SEO modules (sitemap, robots, schema-org)
2. Check for common issues:
   ```bash
   # Check sitemap exists and is valid
   curl -s https://[domain]/sitemap.xml | head -50
   # Check robots.txt
   curl -s https://[domain]/robots.txt
   # Check meta tags on key pages
   curl -s https://[domain]/ | grep -i '<meta'
   ```
3. Scan all pages for missing meta descriptions, titles, OG tags:
   - Read all `.vue` files in `pages/` for `useHead()` or `useSeoMeta()` calls
   - Read all `.md` files in `content/` for frontmatter (`title`, `description`, `image`)
4. Check schema.org markup in rendered HTML
5. Produce report:

**Output template** — save to `[project]/reports/seo-audit-YYYY-MM-DD.md`:
```markdown
# SEO Audit — [Project] — YYYY-MM-DD

## Summary
- Pages audited: N
- Issues found: N (critical: N, warning: N, info: N)

## Critical Issues
- [ ] [description] — [file:line] — [fix]

## Warnings
- [ ] [description] — [file:line] — [fix]

## Technical Checks
| Check | Status | Notes |
|-------|--------|-------|
| sitemap.xml | OK/FAIL | |
| robots.txt | OK/FAIL | |
| Schema.org | OK/FAIL | |
| OG tags | OK/FAIL | |
| Canonical URLs | OK/FAIL | |
| Trailing slashes | OK/FAIL | |

## Recommendations
1. [prioritized fix]
```

### 2. Blog Post Creation

**When:** "write a blog post about [topic]"

**Process:**
1. Read current OKRs from `ikigai/README.md` to ensure alignment
2. Read existing blog posts in `razbakov.com/content/blog/` to avoid duplication and match style
3. Research the topic (web search if needed)
4. Write the post in markdown with proper frontmatter:

**Template** — save to `razbakov.com/content/blog/YYYY-MM-DD-[slug].md`:
```markdown
---
title: "[Title — under 60 chars for SEO]"
description: "[Meta description — 150-160 chars, includes primary keyword]"
date: YYYY-MM-DD
image: /blog/[slug]/cover.png
tags: [relevant, tags]
lang: en
---

[Content — 800-1500 words, scannable with headers, practical value]
```

5. Generate German translation if applicable — save as separate file with `lang: de`
6. Suggest 3 social media snippets (Twitter/Threads, LinkedIn, Instagram caption)

### 3. Content Calendar

**When:** "create content calendar" or start of month

**Process:**
1. Read OKRs from `ikigai/README.md`
2. Read recent sessions from `ikigai/sessions/` for content ideas
3. Check existing blog posts to avoid repetition
4. Read `ikigai/marketing/` for brand voice guidelines
5. Produce monthly calendar:

**Output template** — save to `ikigai/marketing/content-calendar-YYYY-MM.md`:
```markdown
# Content Calendar — YYYY-MM

## Strategy
- OKR alignment: [which OKRs this serves]
- Primary topics: [2-3 themes]
- Target audience: [who]

## Schedule

| Week | Type | Topic | Channel | Status |
|------|------|-------|---------|--------|
| W1 | Blog post | [topic] | razbakov.com | draft/published |
| W1 | Thread | [topic] | X/Threads | draft/published |
| W2 | YouTube | [session topic] | ai-study-group | draft/published |
| W2 | Social | [poster topic] | IG/LinkedIn | draft/published |
| W3 | Blog post | [topic] | razbakov.com | draft/published |
| W4 | Newsletter | [monthly roundup] | email | draft/published |

## Content Ideas Backlog
- [ ] [idea from sessions/Telegram inbox]
```

### 4. YouTube Publishing

**When:** "generate YouTube metadata for [video]" or after ai-study-group recording

**Process:**
1. If video has a transcript (check `ai-study-group/meetings/`), read it
2. If no transcript, use the `transcribe-via-faster-whisper` skill first
3. Generate metadata:

**Output template:**
```markdown
## YouTube Metadata

**Title:** [under 60 chars, keyword-front-loaded]
**Description:**
[First 2 lines: hook + value proposition — these show in search]

Timestamps:
00:00 — [topic]
MM:SS — [topic]

[2-3 sentences expanding on the content]

Links:
- [relevant project URLs]
- Subscribe: [channel URL]

**Tags:** [10-15 comma-separated tags, mix of broad and specific]

**Thumbnail text:** [2-4 words for overlay]
```

4. Suggest 3 clip timestamps for Shorts (under 60s segments with strong hooks)

### 5. Analytics Report

**When:** "analytics report" or end of month

**Process:**
1. Check PostHog for traffic data (use PostHog MCP tools if available):
   - Page views, unique visitors, top pages
   - Bounce rate, session duration
   - Traffic sources
2. Check Google Search Console data (via web if accessible)
3. Compare to previous month
4. Produce report:

**Output template** — save to `ikigai/marketing/analytics-YYYY-MM.md`:
```markdown
# Analytics Report — YYYY-MM

## Summary
| Metric | This Month | Last Month | Change |
|--------|-----------|------------|--------|
| Unique visitors | N | N | +/-N% |
| Page views | N | N | +/-N% |
| Bounce rate | N% | N% | +/-N% |
| Avg session | Ns | Ns | +/-Ns |

## Top Pages
1. [page] — N views
2. [page] — N views

## Traffic Sources
- Organic: N%
- Direct: N%
- Social: N%
- Referral: N%

## SEO Performance
- Indexed pages: N/N
- Search impressions: N
- Search clicks: N
- Avg position: N

## Recommendations
1. [action based on data]
```

### 6. Full Content Sprint

**When:** "content-seo sprint"

Runs all workflows in sequence:
1. SEO audit on all production sites (DanceGods, razbakov.com)
2. Analytics report for the month
3. Content calendar for next month
4. Fix any critical SEO issues found in audit
5. Write first blog post from calendar

## Integration Points

- **ikigai/README.md** — OKRs drive content topics
- **ikigai/sessions/** — Daily sessions are content idea sources
- **ikigai/marketing/** — Content calendars and analytics reports saved here
- **razbakov.com/content/blog/** — Blog posts published here
- **dancegods/** — SEO fixes applied to nuxt.config.ts and page components
- **ai-study-group/meetings/** — Transcripts feed YouTube metadata
- **smm-manager/** — Posters feed social media distribution
- **PostHog MCP** — Analytics data source

## Project-Specific Notes

### DanceGods (dancegodscompany.com)
- Nuxt 3 + Decap CMS + Netlify
- SEO modules: nuxt-gtag, schema-org, sitemap
- Critical: 97% pages not indexed — likely trailing slash or canonical issue
- Has i18n (EN, ES) — check hreflang tags

### razbakov.com
- Nuxt 3 + @nuxt/content + Netlify
- 5 languages (EN, DE, ES, RU, UK)
- Blog in `content/blog/` with markdown frontmatter
- PostHog (EU) for analytics
- Coral Bloom brand style (warm, approachable)

### web100
- Lead gen content lives in `web100/leads/`
- Outreach queue: `leads/outreach_queue.csv`
- Target: local Munich businesses (hairdressers, restaurants, cafes)
- German-first content
