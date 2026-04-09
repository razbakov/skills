---
name: nuxt-i18n
description: Add internationalization (i18n) to a Nuxt 3 project — install @nuxtjs/i18n, extract hardcoded strings from components into locale JSON files, configure routing strategy, create a language switcher component, and fix hosting config for SSR locale routes. Use this skill whenever the user wants to translate a Nuxt site, add multiple languages, add a language switcher, or localize content in a Nuxt project. Also applies when migrating a monolingual Nuxt site to multilingual.
---

# Nuxt i18n Setup

Add multi-language support to any Nuxt 3 project. This skill covers the full workflow from installing the module to deploying translated SSR routes.

## Prerequisites

- Nuxt 3 project with components containing hardcoded text
- Target languages identified (e.g., de, ru, es)

## Step 1: Audit existing text

Before writing any code, scan all components and pages for hardcoded strings. This gives you the full picture of what needs translating.

```bash
# Find components and pages with text content
grep -rn ">[^<{]*[a-zA-Z][^<{]*<" components/ pages/ --include="*.vue" | head -50
```

Catalog every user-facing string:
- Component text and headings
- Form labels, placeholders, validation messages
- Button labels
- Meta tags in `nuxt.config.ts` and `useHead()` calls
- Alt text on images
- Error messages
- Arrays of objects with text (testimonials, feature lists, FAQ items, etc.)

## Step 2: Install @nuxtjs/i18n

```bash
# Use whatever package manager the project uses (check lockfile)
pnpm add @nuxtjs/i18n
# or: npm install @nuxtjs/i18n
# or: yarn add @nuxtjs/i18n
```

## Step 3: Create locale files

Create `i18n/locales/` directory with a JSON file per language. Start with the default language (usually `en.json`), then translate.

```
i18n/
└── locales/
    ├── en.json   # Source language
    ├── de.json   # German
    ├── ru.json   # Russian
    └── es.json   # Spanish
```

Structure keys semantically by component or section:

```json
{
  "hero": {
    "tagline": "The game begins when the lights go down.",
    "cta": "Request an Invitation"
  },
  "nav": {
    "requestEntry": "Request Entry"
  },
  "form": {
    "name": "Your name",
    "email": "your@email.com",
    "submit": "Get on the List",
    "errors": {
      "nameRequired": "Name is required",
      "emailInvalid": "Please enter a valid email"
    }
  }
}
```

Tips for translation keys:
- Use nested objects to group by component/section
- Use camelCase for key names
- Keep the same key structure across all locale files
- For arrays (testimonials, features, phases), use indexed keys or arrays in JSON
- Escape the `@` symbol as `{'@'}` in vue-i18n — it's a special character for linked messages

## Step 4: Configure nuxt.config.ts

Add the i18n module with lazy-loaded locale files:

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
      { code: 'ru', language: 'ru-RU', file: 'ru.json', name: 'Русский' },
      { code: 'es', language: 'es-ES', file: 'es.json', name: 'Español' },
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

**Strategy choice:** `prefix_except_default` means the default locale has no prefix (`/`) while others get prefixed (`/de/`, `/ru/`). This preserves existing URLs and is the most common choice.

## Step 5: Update components to use $t()

Replace every hardcoded string with `$t('key.path')`. In `<script setup>`, use `useI18n()`:

```vue
<script setup>
const { t } = useI18n()

// For reactive arrays/objects that use translations:
const items = computed(() => [
  { title: t('features.item1.title'), description: t('features.item1.description') },
  { title: t('features.item2.title'), description: t('features.item2.description') },
])
</script>

<template>
  <h1>{{ $t('hero.tagline') }}</h1>
  <button>{{ $t('form.submit') }}</button>
</template>
```

Important patterns:
- Static text in templates: `{{ $t('key') }}`
- Attributes: `:placeholder="$t('form.email')"`
- Script setup: `const { t } = useI18n()` then `t('key')`
- Computed arrays with translated content need `computed()` so they react to locale changes
- Navigation links between pages: use `useLocalePath()` or `<NuxtLinkLocale>` to preserve locale prefix

## Step 6: Locale-aware SEO meta

Update `useHead()` calls to use translated titles and descriptions:

```vue
<script setup>
const { t } = useI18n()

useHead({
  title: t('meta.title'),
  meta: [
    { name: 'description', content: t('meta.description') },
    { property: 'og:title', content: t('meta.title') },
    { property: 'og:description', content: t('meta.description') },
  ],
})
</script>
```

## Step 7: Create LanguageSwitcher component

Create a switcher that fits the project's design. Use `useLocalePath()` and `useSwitchLocalePath()`:

```vue
<script setup>
const { locale, locales } = useI18n()
const switchLocalePath = useSwitchLocalePath()
</script>

<template>
  <div class="flex items-center gap-1">
    <NuxtLink
      v-for="loc in locales"
      :key="loc.code"
      :to="switchLocalePath(loc.code)"
      :class="[
        'text-xs px-2 py-1 uppercase tracking-wider transition-all border',
        locale === loc.code
          ? 'text-primary border-primary/50 bg-primary/10'
          : 'text-muted border-transparent hover:text-foreground hover:border-muted/20'
      ]"
      :aria-label="loc.name"
    >
      {{ loc.code }}
    </NuxtLink>
  </div>
</template>
```

Add the switcher to the site header/navigation.

## Step 8: Fix hosting config for SSR routes

This step is critical — without it, locale routes like `/de/` will 404 in production.

### Netlify

If using Netlify with SSR (nitro preset "netlify"), remove any catch-all redirect from `netlify.toml`:

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

### Static hosting (nuxt generate)

If using static generation, add `prerender` routes for each locale in `nuxt.config.ts`:

```typescript
nitro: {
  prerender: {
    routes: ['/de', '/ru', '/es'],
    crawlLinks: true,
  }
}
```

## Step 9: Verify and deploy

```bash
# Build locally to catch errors
pnpm build

# Test locale routes
pnpm dev
# Visit /, /de/, /ru/, /es/ and verify:
# - Text is translated
# - Language switcher works
# - SEO meta tags change per locale
# - Forms show translated validation messages
# - Browser language detection redirects correctly

# Deploy
# Netlify: push to main or `npx netlify-cli deploy --prod --build`
# Vercel: push to main
```

## Checklist

- [ ] All hardcoded strings extracted to locale JSON files
- [ ] All components use `$t()` / `useI18n()`
- [ ] Arrays/objects with text use `computed()` for reactivity
- [ ] LanguageSwitcher component added to header
- [ ] SEO meta tags are locale-aware
- [ ] Hosting config allows SSR locale routes (no catch-all redirects)
- [ ] Build succeeds
- [ ] All locale routes render correctly
- [ ] Browser language detection works on root path
