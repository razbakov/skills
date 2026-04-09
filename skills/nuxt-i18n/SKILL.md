---
name: nuxt-i18n
description: Add internationalization (i18n) to a Nuxt 3 project — install @nuxtjs/i18n, extract hardcoded strings from components into locale JSON files, configure routing strategy, create a language switcher component, and fix hosting config for SSR locale routes. Use this skill whenever the user wants to translate a Nuxt site, add multiple languages, add a language switcher, localize content, or migrate a monolingual Nuxt site to multilingual. Also triggers when adding specific languages (e.g., "add German to my site") or when the user mentions i18n, localization, or translation in a Nuxt context.
---

# Nuxt i18n Setup

Add multi-language support to any Nuxt 3 project. This skill covers the full workflow from installing the module to deploying translated SSR routes.

## Prerequisites

- Nuxt 3 project with components containing hardcoded text
- Target languages identified (e.g., de, ru, es, fr, zh)

## Step 1: Audit existing text

Before writing any code, scan all components and pages for hardcoded strings. Use the Grep tool to find text content in Vue templates:

```
Pattern: ">[^<{]*[a-zA-Z][^<{]*<"
Glob: "*.vue"
Path: components/ and pages/
```

Catalog every user-facing string:
- Component text and headings
- Form labels, placeholders, validation messages
- Button labels
- Meta tags in `nuxt.config.ts` and `useHead()` calls
- Alt text on images
- Error messages
- Arrays of objects with text (testimonials, feature lists, FAQ items, etc.)
- API response messages (e.g., email subjects/bodies in server routes)

## Step 2: Install @nuxtjs/i18n

Check the lockfile to determine the package manager, then install:

```bash
pnpm add @nuxtjs/i18n    # if pnpm-lock.yaml exists
npm install @nuxtjs/i18n  # if package-lock.json exists
yarn add @nuxtjs/i18n     # if yarn.lock exists
```

## Step 3: Create locale files

Create `i18n/locales/` directory with a JSON file per language. Start with the default language (usually `en.json`), then translate.

```
i18n/
└── locales/
    ├── en.json   # Source language
    ├── de.json
    ├── fr.json
    └── ...
```

Structure keys semantically by component or section:

```json
{
  "nav": {
    "home": "Home",
    "about": "About",
    "contact": "Contact"
  },
  "hero": {
    "title": "Welcome to our platform",
    "subtitle": "Build something amazing",
    "cta": "Get Started"
  },
  "form": {
    "name": "Your name",
    "email": "your{'@'}email.com",
    "submit": "Submit",
    "errors": {
      "nameRequired": "Name is required",
      "emailInvalid": "Please enter a valid email"
    }
  },
  "meta": {
    "title": "My Website",
    "description": "A brief description of the site"
  }
}
```

Key conventions:
- Nested objects grouped by component/section
- camelCase for key names
- Identical key structure across all locale files
- For arrays (testimonials, features), use indexed keys like `"items": { "0": { "title": "..." }, "1": { ... } }` or JSON arrays
- Escape `@` as `{'@'}` — it's a vue-i18n special character for linked messages
- For pluralization: `"items": "no items | {count} item | {count} items"` (pipe-separated forms)
- For interpolation: `"greeting": "Hello, {name}!"` then `$t('greeting', { name: userName })`

## Step 4: Configure nuxt.config.ts

Add the i18n module with lazy-loaded locale files. Adapt the locale list to the project's target languages:

```typescript
export default defineNuxtConfig({
  modules: [
    // ...existing modules,
    '@nuxtjs/i18n'
  ],

  i18n: {
    locales: [
      { code: 'en', language: 'en-US', file: 'en.json', name: 'English' },
      { code: 'de', language: 'de-DE', file: 'de.json', name: 'Deutsch' },
      // Add more as needed
    ],
    defaultLocale: 'en',
    strategy: 'prefix_except_default',
    lazy: true,
    langDir: 'locales',
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'i18n_redirected',
      redirectOn: 'root',
    },
  },
})
```

**Strategy choice:** `prefix_except_default` means the default locale has no prefix (`/`) while others get prefixed (`/de/`, `/fr/`). This preserves existing URLs and is the most common choice. Other options: `prefix` (all locales get prefix), `no_prefix` (no URL differentiation — locale from cookie/header only).

## Step 5: Update components to use $t()

Replace every hardcoded string with `$t('key.path')`. In `<script setup>`, use `useI18n()`:

```vue
<script setup>
const { t } = useI18n()

// For reactive arrays/objects that use translations, wrap in computed()
// so they update when the user switches language:
const features = computed(() => [
  { title: t('features.item1.title'), desc: t('features.item1.desc') },
  { title: t('features.item2.title'), desc: t('features.item2.desc') },
])
</script>

<template>
  <h1>{{ $t('hero.title') }}</h1>
  <p>{{ $t('hero.subtitle') }}</p>
  <button>{{ $t('form.submit') }}</button>
  <input :placeholder="$t('form.email')" />
</template>
```

Important patterns:
- Static text in templates: `{{ $t('key') }}`
- Attributes: `:placeholder="$t('form.email')"`
- Script setup: `const { t } = useI18n()` then `t('key')`
- Computed arrays/objects are essential — without `computed()`, translated content won't update when the user switches locale
- Interpolation: `$t('greeting', { name: userName })`
- Pluralization: `$t('items', { count: itemCount })`
- Navigation links: use `useLocalePath()` or `<NuxtLinkLocale>` to preserve locale prefix in `<NuxtLink>` hrefs

## Step 6: Locale-aware SEO meta

Update `useHead()` calls with `computed` wrapping — this ensures meta tags react to locale changes:

```vue
<script setup>
const { t } = useI18n()

useHead(computed(() => ({
  title: t('meta.title'),
  meta: [
    { name: 'description', content: t('meta.description') },
    { property: 'og:title', content: t('meta.title') },
    { property: 'og:description', content: t('meta.description') },
  ],
})))
</script>
```

The `computed()` wrapper is important here — without it, meta tags won't update when the user switches language via the switcher.

## Step 7: Create LanguageSwitcher component

Create a switcher component. Adapt the styling to match the project's design system (the example below uses minimal inline styles — replace with Tailwind, UnoCSS, or plain CSS as appropriate):

```vue
<script setup>
const { locale, locales } = useI18n()
const switchLocalePath = useSwitchLocalePath()
</script>

<template>
  <nav class="language-switcher" aria-label="Language">
    <NuxtLink
      v-for="loc in locales"
      :key="loc.code"
      :to="switchLocalePath(loc.code)"
      :class="['lang-link', { active: locale === loc.code }]"
      :aria-label="loc.name"
      :aria-current="locale === loc.code ? 'true' : undefined"
    >
      {{ loc.code }}
    </NuxtLink>
  </nav>
</template>
```

Place the switcher in the site header/navigation. Style it to match the project's existing design — the component handles the locale switching logic, you handle the look and feel.

## Step 8: Fix hosting config for SSR routes

This step is critical — without it, locale routes like `/de/` will 404 in production.

### Netlify

If using Netlify with SSR (nitro preset `"netlify"`), remove any catch-all redirect from `netlify.toml`:

```toml
# REMOVE this — it blocks SSR routes:
# [[redirects]]
#   from = "/*"
#   to = "/index.html"
#   status = 200

# Correct config for Nuxt SSR on Netlify:
[build]
  command = "pnpm install --frozen-lockfile && pnpm build"
  publish = ".output/public"

[build.environment]
  NODE_VERSION = "20"
```

The Nuxt Netlify preset handles routing via server functions automatically — no redirects needed.

### Vercel

Vercel with `preset: 'vercel'` handles SSR routes automatically. No special config needed.

### Cloudflare Pages

With `preset: 'cloudflare-pages'`, routes work automatically via Workers.

### Static hosting (nuxt generate)

If using static generation, add `prerender` routes for each locale in `nuxt.config.ts`:

```typescript
nitro: {
  prerender: {
    routes: ['/de', '/fr', '/es'],
    crawlLinks: true,
  }
}
```

## Step 9: Verify and deploy

```bash
# Build locally to catch errors
pnpm build

# Test locale routes in dev
pnpm dev
```

Verify each locale route:
- Text is translated (not showing raw keys)
- Language switcher changes the locale and URL
- SEO meta tags update per locale (check page source)
- Forms show translated validation messages
- Browser language detection redirects correctly on root path
- Internal links preserve the locale prefix

Then deploy using the project's normal deployment method.

## Checklist

- [ ] All hardcoded strings extracted to locale JSON files
- [ ] All components use `$t()` / `useI18n()`
- [ ] Arrays/objects with text use `computed()` for reactivity
- [ ] `useHead()` wrapped in `computed()` for reactive meta tags
- [ ] LanguageSwitcher component added to header
- [ ] Hosting config allows SSR locale routes (no catch-all redirects)
- [ ] Build succeeds
- [ ] All locale routes render correctly
- [ ] Browser language detection works on root path
