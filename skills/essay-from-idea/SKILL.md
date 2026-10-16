---
name: essay-from-idea
description: "Write a single, publishable long-form essay or thesis from an idea, argument, or reflection — one focused piece, not a cluster. Establishes a real thesis, structures the argument, integrates evidence and sources, and matches the target blog's voice and frontmatter before optionally publishing. Use when the user says 'write an essay', 'write a thesis', 'turn this into a post', 'make this into an article', or wants one considered piece on a topic. For turning ONE long transcript into MANY posts, use essay-cluster-from-transcript instead."
---

# Essay From Idea

## When to use

Trigger this skill when the user wants **one** considered long-form piece:

- "Write an essay / thesis / article on X"
- "Turn this idea into a blog post"
- "Make this reflection into a publishable piece"
- "I want one strong essay about …"

Do NOT use this for:

- **Many essays from one dump** → use `essay-cluster-from-transcript`.
- **Polishing prose that already has a thesis and structure** → use `copy-editing`.
- **Pure research with no argument to make** → use `research` / `deep-research`.

## The difference between an essay and a summary

A summary reports what is known. An **essay makes a claim and defends it.** If the piece could be titled "Notes on X," it is not an essay yet. Every essay produced by this skill must be reducible to a single sentence the reader could disagree with — the thesis. If you cannot write that sentence, stop and find it before drafting.

## Inputs to gather first

| Input | Where it usually lives |
|---|---|
| The core idea / argument | The user's message or a transcript they point to |
| Blog repo path + post-path convention | Project Path Registry + repo CLAUDE.md |
| Frontmatter shape | A recent post in the same repo (read one, match exactly) |
| Brand voice / words to use & avoid | Repo CLAUDE.md; infer from 1–2 existing posts |
| Translation + hero-image + Telegram rules | User's private CLAUDE.md (per-domain publishing rules) |
| Publish vs. draft | Ask if unclear; publishing is irreversible |

If any publishing input is missing or the topic is sensitive/public-facing, ask **one** consolidated question before drafting — never guess on an irreversible public push.

## Workflow

### 1. Find the thesis

Read the source idea end-to-end. Write the one-sentence claim the whole essay will defend. Show it to yourself: is it arguable? Non-obvious? True to what the user actually thinks? Refine until it is a spine, not a topic.

### 2. Outline the argument, not the topics

Sketch 4–7 sections that each *move the argument forward* — setup → development → turn → the part only this author could write → resolution. Avoid the encyclopedia shape (one section per subtopic with no through-line). A good essay has a direction; the reader should feel pulled, not catalogued.

### 3. Verify every factual and source claim

Before drafting, check every specific: book titles, author names, dates, quotes, statistics, named people or businesses, "first/only/no-one-else" superlatives. Source it, use a defensible range, or cut it. AI-written argument-prose is confidently wrong on specifics — this step is non-negotiable for anything external-facing. (See the framework's fact-check rule.) Reproduce at most one short quote per source, attributed; never reconstruct copyrighted text.

### 4. Draft in the target voice

Match the blog's actual voice by reading a recent post first — sentence rhythm, first-person stance, use of italics, header style, how it opens and closes. Write the essay to *sound like the author on their best day*, not like a generic explainer. Prefer concrete images over abstractions; earn every claim.

### 5. Self-edit against the thesis

Cut every sentence that does not serve the thesis. Tighten openings (no throat-clearing) and endings (no summary-of-the-summary — end on the sharpest form of the claim). If a section could be deleted without weakening the argument, delete it.

### 6. Frontmatter + hero image

Create the post file with frontmatter copied structurally from a recent post (title, description, date, image path, category, language, tags). Generate the hero image per the repo's rules (this instance: `/image-from-gemini`, never HTML). Place it at the repo's hero-image convention.

### 7. Publish per the domain's rules

Follow the user's per-domain publishing rules exactly — for this instance that means: translate to all configured languages (de, es, ru, uk) with `language:` in each file's frontmatter, add the `telegram:` link, commit & push (verify auto-deploy succeeded remotely), then send the live link to the user's messaging surface. Confirm the deployed URL resolves before reporting done — never announce a link you have not seen return 200.

## Output

- One EN essay file with correct frontmatter, plus configured translations.
- One hero image at the repo convention.
- A pushed commit that auto-deploys.
- A verified live URL delivered to the user's messaging surface.

## Notes

- **Irreversibility gate.** Publishing to a public blog is hard to reverse and indexed fast. If the topic is personal, sensitive, or reputationally loaded, show the draft and get an explicit go before the public push — even when the user said "just publish" — then proceed.
- **Voice fidelity beats cleverness.** The failure mode is a technically-correct essay that does not sound like the author. Read their existing work first, every time.
