---
name: translate-blog-post
description: "Translate one English blog post into multiple target languages via parallel sub-agents, preserving frontmatter conventions, hero image, and brand voice. Use when the user shares a published English post URL or markdown path and says 'translate it', 'add other languages', 'publish in DE/ES/RU/UK', 'translate to 5 languages', or asks for localized versions of a specific post."
---

# Translate Blog Post

## When to use

Trigger this skill when:

- The user points at a single English blog post (URL, markdown filepath, or slug) and asks to translate it.
- They say "translate to 5 languages", "add German/Spanish/Russian/Ukrainian", "publish in other languages", "make multilingual versions".
- They want translations as a follow-up to publishing the original.

Do NOT use this for translating arbitrary text snippets, UI strings, or untouched non-blog content. This is specifically for blog posts that follow the repo's blog conventions.

## Inputs the skill needs

Confirm or read from the project's CLAUDE.md / repo conventions:

| Input | Where it usually lives |
|---|---|
| Source post path | User-provided URL or filepath |
| Target languages | User request, or default set in repo's CLAUDE.md (e.g. `de, es, ru, uk`) |
| Filename convention | An existing 5-lang post in the same repo |
| Frontmatter shape | An existing translation in the same repo |
| Per-language overrides | Repo's CLAUDE.md (e.g. RU/UK Telegram channel differs from EN) |
| Hero image policy | Repo's CLAUDE.md (usually shared across translations — same `image:` path) |

Read one existing 5-language post in the same repo before dispatching agents. Filename + frontmatter conventions are always per-repo and never inferred from training data.

## Workflow

### 1. Read the source

Read the full English markdown — frontmatter and body. Note:

- Title, description, hero image path
- Category and tags (tags are usually slugs; do NOT translate them)
- Telegram / messaging links
- Voice register (formal? conversational? second person? umlaut on the author's name?)

### 2. Dispatch one sub-agent per target language (parallel)

For each target language, dispatch one sub-agent (in Claude Code: the `Agent` tool with `subagent_type: general-purpose` and `run_in_background: true`). Each prompt must include:

- The exact filepath to write (matching repo convention)
- The full source markdown (so the agent translates from the canonical version, not a paraphrase)
- The frontmatter template with that language's overrides (`language: <lang>`, telegram channel if it differs, etc.)
- Translation rules (see below)
- Explicit instruction: **NO git commits**

All agent dispatches go in a single message (parallel). One agent per language, not one per paragraph.

### 3. Translation rules to include in every agent prompt

Tailor per language but always cover:

- **Voice & register** — match the source. First-person if source is. Conversational if source is. Don't make it more formal than the English.
- **Author's name** — preserve umlauts and accents (e.g. "Alösha" stays "Alösha"; in Cyrillic-script languages use the native form like "Алёша" / "Альоша").
- **Reserved nouns** — Newton, Einstein, brand names, the Matrix → keep as proper nouns (translate to local scripts only when conventional, e.g. Cyrillic).
- **Headings** — translate H2/H3 too. Don't leave English headings.
- **Cultural references** — use the localized version where it exists (e.g. "the spoon doesn't exist" → "ложки не существует" in RU, "la cuchara no existe" in ES).
- **Tags** — keep as English slugs (they're URL paths, not display text).
- **Form of address** — informal ("ты" / "tú" / "du") unless the source repo's voice guide says otherwise.
- **Native vocabulary** — for Ukrainian especially: write proper Ukrainian, not Russian-sounding Ukrainian. Same caution applies to any closely-related language pair.

### 4. Verify, commit, deploy

When all language agents report back:

- Confirm each file exists with correct frontmatter (`language:`, hero image path, title in the target language, etc.).
- Stage all translation files and commit in one commit. Push.
- Wait for the deploy.
- Verify each language URL returns 200 (the canonical i18n URL is usually `/<locale>/blog/<slug>-<locale>` — check an existing 5-lang post to confirm the pattern).
- Verify the localized title shows in the rendered HTML (curl + grep `<title>`).

Report back with the 5 URLs grouped by language.

## Common gotchas

- **i18n routing prefix.** Most Nuxt/Next sites with i18n route non-default-locale pages under `/<locale>/...`. Direct URLs without the prefix may also work (because the file is prerendered) but the canonical URL is the prefixed one — use that for sharing.
- **Translation state inheritance.** If the source post has `hidden: true` or `draft: true`, translations should usually inherit that. Confirm with the user before publishing translations of an unpublished essay.
- **Hero image is usually shared, not duplicated.** The same `/images/blog/<slug>/hero.png` works for all languages by default. Generate per-language images only when the hero embeds text or a culturally-specific symbol that wouldn't read in the target language.
- **Tags are slugs, not display text.** Translating tags breaks tag-based filtering and routing. Always keep the English slug.
- **Per-language messaging channels.** Some repos route RU + UK posts to a different Telegram/social channel than EN/DE/ES. Check the repo's CLAUDE.md for the mapping; don't hardcode.
- **Don't translate the date.** Date stays in ISO format.
- **Don't have agents do git work in parallel.** Same rule as essay-cluster-from-transcript — orchestrator commits, agents only write files.

## Optional: review pass

After translation, the user may want a native-speaker review pass. Note in the final report which languages would benefit (typically RU/UK if the user is more confident in those, ES if not). Don't auto-trigger reviews — leave that as a follow-up.
