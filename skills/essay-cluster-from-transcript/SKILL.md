---
name: essay-cluster-from-transcript
description: "Take a long stream-of-thought transcript (voice memo, video reflection, text dump) and turn it into a cluster of 5-20 publishable blog essays. Clusters ideas by theme, drafts each essay via parallel sub-agents, generates Gemini hero images, batch-commits, and (optionally) sends a grouped link list via the user's preferred messaging surface. Use when the user shares a transcript and says 'turn this into essays', 'write a series', 'split into posts', 'draft all of them', or pastes a long stream of ideas they want shipped."
---

# Essay Cluster From Transcript

## When to use

Trigger this skill when:

- The user shares a long stream of thought (voice memo transcript, free-form text, video reflection) and asks to publish from it.
- They say "turn this into essays", "write a series", "split into separate posts", "draft all of these", "ship the cluster".
- They paste many ideas in one message and ask for blog posts.

Do NOT use this for single-essay requests, polishing existing drafts, or extracting one quick takeaway. This is for the case where one transcript becomes 5-20 essays.

## Inputs the skill needs

Before drafting, confirm or read from the project's CLAUDE.md:

| Input | Where it usually lives |
|---|---|
| Blog repo path | Project Path Registry in user's CLAUDE.md |
| Blog post path convention | Repo's CLAUDE.md (e.g. `content/blog/YYYY-MM-DD-slug-en.md`) |
| Hero image path convention | Repo's CLAUDE.md (e.g. `public/images/blog/<slug>/hero.png`) |
| Frontmatter shape | An existing recent post in the same repo |
| Brand voice + style | Repo's CLAUDE.md (tone, words to use, words to avoid) |
| Hero image style guide | Repo's CLAUDE.md (palette, typography, motifs) |
| Default state for new posts | `hidden: true` if the repo has a draft mechanism, else publish directly |
| Messaging surface for the link list | User's CLAUDE.md (Telegram bot, Slack channel, etc.) |

If any are missing or unclear, ask one consolidated question — don't draft 17 essays in the wrong voice.

## Workflow

### 1. Cluster the transcript into a numbered list of titles

Read the full transcript end-to-end. Identify distinct ideas. Group them — typical structure:

- **Core philosophy / framework** (the load-bearing concepts)
- **Mechanics / how it works** (operational claims)
- **Examples / cases** (concrete material)
- **Personal / autobiographical** (vulnerable, first-person)

Aim for 5-20 essays. Fewer if the transcript is thin; more if it's dense. Each title should be a single concrete claim — not a category. Bad: "Thoughts on Productivity". Good: "I Stopped Treating Myself Like a One-Job Person".

Present the numbered list to the user grouped by theme. Suggest a 3-5 essay reading order for the impatient. Confirm before drafting.

### 2. Dispatch one sub-agent per essay (parallel)

For each essay, dispatch one sub-agent (in Claude Code: the `Agent` tool with `subagent_type: general-purpose` and `run_in_background: true`). The prompt for each agent must include:

- The exact markdown file path to write
- The exact hero image path to write
- The full frontmatter template (filled with title and slug; agent fills `description`)
- The voice/tone rules (cite from repo's CLAUDE.md, don't paraphrase)
- The relevant slice of the transcript as **source material** (verbatim — anchor the essay in the user's actual words, not your paraphrase)
- The specific essay angle for this post (one paragraph)
- The Gemini image generation command, with a prompt tuned to the brand style and this essay's metaphor
- Word count target (typical: 700-1100 words)
- Explicit instruction: **NO git commits**

Send all dispatch calls in a single message (parallel). The skill orchestrator does the git work after, not the sub-agents — otherwise they race on `git status`.

### 3. Verify and batch-commit

When all agents report back:

- Confirm each markdown file and hero image exists (`ls`, file size > 0).
- Spot-check one essay's prose quality.
- Stage all new files (markdown + images) and commit in a single descriptive commit. Push.
- Wait for the deploy (Netlify, Vercel, etc.) — check via API or status badge.
- Verify one URL returns 200 before sending the link list.

### 4. Send the grouped link list

Compose a single message with:

- Bold theme headers
- Numbered links in publishing order (full URLs, with the actual title as the link text)
- A short suggested reading order (3-5 essays) for cherry-pickers
- A one-line summary of what the cluster is about

Send via the messaging surface configured in the user's CLAUDE.md. Format using whatever markup the surface supports (HTML for Telegram, mrkdwn for Slack).

## Hero image rules

- Always `/image-from-gemini` — never HTML+headless Chrome (looks generic).
- Each essay's image prompt should be tuned to that essay's central metaphor (the egregore, the spoon, the dome, etc.) — not a generic "abstract concept" image.
- Always include the brand palette and "no text" in every prompt.
- Folder convention: `public/images/blog/<slug>/hero.png` (or whatever the repo uses).

## Default state: drafts vs. published

If the repo has a draft mechanism (a `hidden:` or `draft:` field with a query-param toggle on the homepage), default new clusters to **draft**. The user reviews 17 essays before deciding to publish — that's the right gate. Confirm with the user before flipping the publish switch.

If the repo has no draft mechanism, publish directly only after the user explicitly says "publish" — not from "draft them".

## Common gotchas

- **Nuxt Content auto-strips `draft: true`**. If you use Nuxt Content, the `draft` field is reserved — pages with `draft: true` are excluded from `queryContent` results in production. Use `hidden: true` (or any other field name) instead, with a manual filter in the homepage component.
- **Hydration mismatch with query-param filters in static SSG sites**. If the homepage filter depends on `route.query`, both SSR (empty query) and CSR (full query) render different lists, and Vue's hydration reuses DOM nodes from the smaller list against the larger one — titles end up paired with the wrong hrefs. Defer the toggle inside `onMounted` so SSR and initial CSR match exactly, and watch the route afterward.
- **Prerender misses hidden pages**. With `crawlLinks: true`, hidden posts that don't appear on the homepage never get prerendered → 404 on direct URLs. Scan the content directory at build time and explicitly add hidden routes to the prerender list.
- **Don't have agents do git work in parallel**. They race. The orchestrator commits.
- **Cap parallelism reasonably**. 17 essays in parallel is fine on a modern stack; 50 is asking for trouble.

## Optional follow-ups

After the cluster ships, ask the user whether to translate the cluster (or specific essays) using the `translate-blog-post` skill. Translations are usually a separate, lower-priority pass.
