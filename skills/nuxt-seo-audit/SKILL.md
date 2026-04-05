---
name: nuxt-seo-audit
description: Use when auditing or setting up SEO for a Nuxt site. Triggers include missing page titles, no structured data, sitemap not including all pages, hreflang/canonical issues, pages not prerendered, trailing slash redirect loops, AI crawlers blocked in robots.txt, or preparing a site for search engine indexing.
---

# Nuxt SEO Audit

Full SEO audit for a Nuxt site. Check live responses, not just source code — what Google sees is what matters.

## When to Use

- Setting up SEO for a new Nuxt site
- After adding i18n / multiple languages
- After switching rendering mode (SSR / static / hybrid)
- When Google Search Console reports issues
- Before submitting site to search engines

## Audit Checklist

Run each check against the **live deployed site** using `curl`.

### 1. Page Titles

```bash
# Check every page type
for url in "/" "/about" "/blog" "/projects" "/cv"; do
  title=$(curl -sL "https://example.com${url}" | grep -oP '(?<=<title>).*(?=</title>)')
  echo "$url — $title"
done
```

**What to check:**
- Every page has a unique `<title>`
- `titleTemplate` set in `nuxt.config.ts` (e.g., `%s · Site Name`)
- Homepage overrides template (no "undefined · Site Name")
- Titles include target keywords (location, tech stack, role)
- SEO titles can differ from display titles — Google gets keywords, social gets voice

### 2. Meta Descriptions

```bash
curl -sL "https://example.com/about" | grep -oP '(?<=name="description" content=")[^"]*'
```

**What to check:**
- Every page has `useSeoMeta({ description })`
- Descriptions are 150-160 characters
- Include target keywords naturally
- Different per page (no duplicates)
- **Localized** — use `t('seo.pageDesc')` not hardcoded English
- Check each locale: `/de/about`, `/ru/blog`, etc.

### 3. Open Graph Tags

```bash
curl -sL "https://example.com/about" | grep -oE '<meta property="og:[^"]*" content="[^"]*"'
```

**What to check:**
- `og:title` — can differ from `<title>` (voice-first for social sharing)
- `og:description` — short, punchy version
- `og:image` — set on every page (avatar for static, hero for blog posts)
- `twitter:card` — `summary` for static pages, `summary_large_image` for posts with images

### 4. Structured Data (JSON-LD)

```bash
curl -sL "https://example.com/" | grep -oP '(?<=<script type="application/ld\+json">).*?(?=</script>)' | python3 -m json.tool
```

**Required schema per page type:**

| Page | Schema types |
|---|---|
| Home | `WebSite`, `WebPage` |
| About | `AboutPage`, `Person` (job, employer, languages, social links) |
| Blog index | `CollectionPage`, `BreadcrumbList` |
| Blog post | `BlogPosting` (headline, date, author, image), `BreadcrumbList` |
| Project index | `WebPage`, `BreadcrumbList` |
| Project detail | `SoftwareApplication` (name, url, author), `BreadcrumbList` |

**Nuxt implementation:** Use `useSchemaOrg()` with `defineArticle`, `definePerson`, `defineBreadcrumb`, `defineSoftwareApp`, `defineWebSite`, `defineWebPage` from `nuxt-schema-org`.

Validate at: Google Rich Results Test (search.google.com/test/rich-results)

### 5. Sitemap

```bash
curl -sL "https://example.com/sitemap_index.xml" | head -30
curl -sL "https://example.com/__sitemap__/en.xml" | grep -c "<url>"
```

**What to check:**
- Sitemap exists and is linked from `robots.txt`
- Includes ALL pages (blog posts, project pages, not just static routes)
- Per-locale sitemaps with `hreflang` alternates
- If content pages are missing, add a server API route:

```typescript
// server/api/__sitemap__/urls.ts
import { serverQueryContent } from "#content/server";
import { defineSitemapEventHandler, asSitemapUrl } from "#imports";

export default defineSitemapEventHandler(async (e) => {
  const content = await serverQueryContent(e).find();
  return content
    .filter((c) => c._path && !c._path.startsWith("/data/"))
    .map((c) => asSitemapUrl({ loc: c._path, lastmod: c.date }));
});
```

### 6. Robots.txt

```bash
curl -sL "https://example.com/robots.txt"
```

**What to check:**
- Not blocking important pages
- **AI crawlers** — check for `Disallow` on ClaudeBot, GPTBot, Google-Extended, Applebot-Extended. If blocked, content is invisible to AI search (Perplexity, ChatGPT, Google AI Overviews)
- Cloudflare may inject AI crawler blocks automatically — check Cloudflare dashboard
- Sitemap URL is referenced

### 7. Hreflang and Canonical

```bash
for url in "/" "/about" "/de/about" "/blog"; do
  echo "=== $url ==="
  curl -sL "https://example.com${url}" | grep -oE '<link[^>]*(canonical|hreflang)[^>]*>'
  echo
done
```

**What to check:**
- Every page has `<link rel="canonical">`
- Canonical URL matches the actual served URL (no trailing slash mismatch)
- Every page has `hreflang` alternates for all languages + `x-default`
- Alternates point to correct locale-specific URLs
- No redirect loops (canonical → 301 → different URL → canonical)

**Nuxt i18n setup:**
- Set `baseUrl` in i18n config (required for hreflang generation)
- Add `language` property to each locale definition
- If `useLocaleHead` doesn't work in `app.vue` during SSR, generate links manually based on `route.path`

### 8. Prerendering

```bash
for url in "/" "/about" "/blog"; do
  cache=$(curl -sI "https://example.com${url}" | grep -i "cache-control" | head -1)
  code=$(curl -sI "https://example.com${url}" | head -1 | awk '{print $2}')
  echo "$code  $url  —  $cache"
done
```

**What to check:**
- Static content sites should be prerendered, not SSR
- `nuxt generate` (not `nuxt build`) for full static
- `nitro.preset: "static"` to prevent hosting platform SSR override
- `cache-control: public` indicates static file serving
- No `cache-control` or SSR-style headers means server-rendered

**Nuxt config for static:**
```typescript
nitro: {
  preset: "static",
  prerender: {
    crawlLinks: true,
    routes: ["/", "/about", "/blog", "/projects"],
    failOnError: false,
  },
}
```

### 9. Trailing Slash Consistency

```bash
curl -sI "https://example.com/about" | grep -i "HTTP\|location"
```

**What to check:**
- No 301 redirects adding/removing trailing slashes
- If redirects exist, canonical must match the final URL (not the pre-redirect URL)
- Netlify: set `pretty_urls = false` in `netlify.toml` to prevent trailing slash redirects
- Check `_redirects` file for legacy rules that conflict with current pages

### 10. Legacy Redirects

```bash
cat public/_redirects
```

**What to check:**
- No redirects that conflict with actual pages (e.g., `/about /` when `/about` is a real page)
- Old slug redirects still point to valid destinations
- No redirect chains (A → B → C)

## Report Format

```markdown
## SEO Audit: [site URL]

| Check | Status | Issues |
|---|---|---|
| Page titles | Pass/Fail | ... |
| Meta descriptions | Pass/Fail | ... |
| OG tags | Pass/Fail | ... |
| Structured data | Pass/Fail | ... |
| Sitemap | Pass/Fail | ... |
| Robots.txt | Pass/Fail | ... |
| Hreflang/canonical | Pass/Fail | ... |
| Prerendering | Pass/Fail | ... |
| Trailing slashes | Pass/Fail | ... |
| Legacy redirects | Pass/Fail | ... |

### Issues Found
...

### Fixes Applied
...
```

## Common Mistakes

- Hardcoding meta descriptions in English instead of using i18n `t()` keys
- Missing `baseUrl` in i18n config — hreflang tags won't generate without it
- `useLocaleHead` in `app.vue` not reactive to route during SSR — may need manual link generation
- Netlify auto-detecting Nuxt and deploying as SSR even with `nuxt generate`
- Cloudflare injecting AI crawler blocks without your knowledge
- `_redirects` containing legacy rules that 301 away from real pages
- Prerender `failOnError: true` (default) failing build on broken internal links
