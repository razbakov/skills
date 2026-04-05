---
name: daily-seo-review
description: Daily SEO health check for dancegods + razbakov.com. Checks indexing status, sitemap, meta tags, and structured data. Reports findings and flags issues for the daily review pipeline. Use when running the morning SEO check or when asked for an SEO status report.
---

# Daily SEO Review

Automated daily SEO health check for two production sites:

| Site | Domain | Project Path |
|------|--------|-------------|
| dancegods | dancegodscompany.com | ~/Projects/dancegodscompany/engineering/website |
| razbakov.com | razbakov.com | ~/Projects/ikigai/engineering/razbakov.com |

## Trigger

- Scheduled daily at 5am via `~/.claude/scheduled-tasks/daily-seo-review/SKILL.md`
- Manual: "run daily SEO review" or `/daily-seo-review`

## Process

Run for each site in parallel where possible.

### 1. Check Sitemap

```bash
# Try sitemap_index first, then sitemap.xml
curl -s "https://[domain]/sitemap_index.xml" | head -30
curl -s "https://[domain]/sitemap.xml" | head -30

# Count total URLs
curl -s "https://[domain]/sitemap.xml" | grep -c "<url>" || \
  curl -s "https://[domain]/sitemap_index.xml" | grep -c "<sitemap>"
```

Flag if: sitemap missing, returns 4xx/5xx, or URL count drops vs yesterday.

### 2. Check Robots.txt

```bash
curl -s "https://[domain]/robots.txt"
```

Check:
- Sitemap reference present
- No critical pages disallowed (`/`, `/blog`, `/about`, `/style`)
- AI crawlers: GPTBot, ClaudeBot, Google-Extended — note if blocked

### 3. Check Meta Tags on Key Pages

```bash
for url in "/" "/about" "/blog"; do
  echo "=== $url ==="
  curl -sL "https://[domain]${url}" | \
    grep -oE '<title>[^<]+</title>|<meta[^>]*(name="description"|property="og:title"|property="og:image")[^>]*>' \
    | head -10
  echo
done
```

Check:
- Every page has unique `<title>`
- `description` meta present (150–160 chars)
- `og:title` and `og:image` present

### 4. Check Canonical and Hreflang

```bash
for url in "/" "/about" "/blog"; do
  echo "=== $url ==="
  curl -sL "https://[domain]${url}" | \
    grep -oE '<link[^>]*(canonical|hreflang)[^>]*>' | head -20
  echo
done
```

Check:
- `<link rel="canonical">` present on each page
- Canonical URL matches served URL (no trailing slash mismatch)
- hreflang alternates cover all supported locales
- `x-default` hreflang present

### 5. Check Structured Data (JSON-LD)

```bash
curl -sL "https://[domain]/" | python3 -c "
import sys, re
html = sys.stdin.read()
schemas = re.findall(r'<script[^>]*type=[\"\\']application/ld\+json[\"\\'][^>]*>(.*?)</script>', html, re.DOTALL)
print(f'Found {len(schemas)} JSON-LD schemas')
for s in schemas[:3]:
    print(s[:300])
"
```

Expected schemas:
- Homepage: `WebSite`, `WebPage`
- Blog post: `BlogPosting`, `BreadcrumbList`
- About: `Person`, `AboutPage`

### 6. Check HTTP Status + Prerendering

```bash
for url in "/" "/about" "/blog"; do
  status=$(curl -sI "https://[domain]${url}" | head -1 | awk '{print $2}')
  cache=$(curl -sI "https://[domain]${url}" | grep -i cache-control | head -1)
  echo "$status  $url  —  $cache"
done
```

Flag: any non-200/301 status, missing `cache-control: public` (may indicate SSR).

### 7. Check Indexing Proxy (Google Search Console)

Since GSC API requires authentication, do a quick spot-check:

```bash
# Check if pages are discoverable (site: operator equivalent check)
curl -sL "https://[domain]/sitemap.xml" | grep -c "<loc>"
```

Document for human review: "Visit GSC → Coverage → check Excluded / Not Indexed count."
Primary concern: **dancegods has 97% pages not indexed** — track via GSC manually until fixed.

## Report Format

Save to `[project_path]/reports/seo-daily-YYYY-MM-DD.md`:

```markdown
# Daily SEO Report — [Domain] — YYYY-MM-DD

## Summary
| Check | Status | Notes |
|-------|--------|-------|
| Sitemap | OK/FAIL | [N] URLs found |
| Robots.txt | OK/WARN/FAIL | |
| Meta tags | OK/WARN/FAIL | |
| Canonical/hreflang | OK/WARN/FAIL | |
| Structured data | OK/WARN/FAIL | [N] schemas |
| HTTP status | OK/FAIL | |

**Overall: HEALTHY / NEEDS ATTENTION / CRITICAL**

## Issues Found
- [ ] [CRITICAL] [description] — [suggested fix]
- [ ] [WARNING] [description] — [suggested action]

## Indexing Status (manual GSC check required)
- dancegods: ~97% not indexed (known issue — track canonical/trailing slash fix)
- razbakov.com: [status]

## Raw Check Output
[paste curl outputs]
```

## Reporting After Both Sites

1. Append combined summary to today's daily review session file: `ikigai/sessions/YYYY-MM-DD-daily-review.md`
2. If CRITICAL issues found: create a GitHub issue in the relevant repo and reference the report
3. No Telegram send on routine OK — only on CRITICAL or new regressions

## Integration Points

- **nuxt-seo-audit** — deeper one-off audit (this skill is the daily lightweight check)
- **content-seo-agent** — fixes and content work (triggered when issues found)
- **daily-review** — morning review incorporates SEO status
- **ikigai/sessions/** — reports linked from daily review files
- **dancegods reports/** — `~/Projects/dancegodscompany/engineering/website/reports/`
- **razbakov.com reports/** — `~/Projects/ikigai/engineering/razbakov.com/reports/`
