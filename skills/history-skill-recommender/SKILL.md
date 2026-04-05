---
name: history-skill-recommender
description: Recommend installed skills by mining Cursor and Codex transcript history and matching recurring needs to skill metadata. Supports both standard recommendations and "new/unused skill" discovery with evidence, trigger phrasing, and SKILL.md paths.
---

# History Skill Recommender

You are a skill recommendation analyst who turns past user requests into practical skill recommendations.

<behavior>
By default, read the installed skill index plus Cursor and Codex transcript history, then return 3-7 recommendations with concrete evidence.

Pick recommendation mode from user intent:
- Standard mode: prioritize skills that match recurring user needs.
- Exploration mode: if the user asks for "new", "unused", "haven't used", or similar, prioritize zero-usage and low-usage skills that still match their themes.

Prefer specific evidence over generic suggestions so recommendations are easy to trust and act on.
</behavior>

<inputs>
- Skill index: `~/.config/skills-manager/scan-cache.json`
- Cursor session history: `~/.cursor/projects/*/agent-transcripts/*`
- Codex compact history: `~/.codex/history.jsonl`
- Codex raw sessions (optional fallback): `~/.codex/sessions/*/*/*/*.jsonl`
</inputs>

<workflow>
1. Read `scan-cache.json` and collect skill entries:
- `name`
- `description`
- `skillMdPath`

2. Read Cursor transcripts and extract user requests from `<user_query>` blocks.

3. Read Codex transcript history:
- Prefer `~/.codex/history.jsonl` and treat each JSON line `text` field as a user query.
- If needed, parse `~/.codex/sessions/*/*/*/*.jsonl` and extract only entries where:
  - `type` is `response_item`
  - `payload.type` is `message`
  - `payload.role` is `user`
  - content item type is `input_text`

4. Normalize extracted queries:
- Convert escaped newlines to spaces.
- Keep short, user-intent text.
- Exclude noisy transcript blocks that are not clean user requests (for example, long meeting transcript chunks with timestamp markers like `###### 00:00` or repeated `speaker -1` lines).
- Exclude boilerplate payload blocks from Codex raw sessions (for example large AGENTS/INSTRUCTIONS payloads, `<environment_context>`, or `<skill>` dumps) when they are not the actual request intent.

5. Detect evidence from history in two channels:
- Direct signals: explicit skill names/slash triggers (for example `/create-skill`, `jira`, `google doc`, `.xlsx`).
- Thematic signals: repeated intent and domain patterns (for example ticketing, document processing, planning, frontend design).

6. Compute recurrence with de-duplication:
- Count matched queries.
- Count unique transcript sessions containing the signal.
- De-duplicate near-identical queries that appear in both Cursor and Codex sources.
- Use unique sessions to avoid over-weighting long back-and-forth in one chat.
- Use recency as a tie-breaker when confidence is similar.

7. Match themes/signals to skill metadata and rank.

8. Choose recommendation set by mode:
- Standard mode: prioritize highest-confidence, highest-recurrence matches.
- Exploration mode: prioritize `unused` first, then `low-use`, while still requiring thematic fit.
</workflow>

<ranking>
Use this usage-status model for each skill:
- `unused`: 0 matched sessions
- `low-use`: 1-2 matched sessions
- `used`: 3+ matched sessions

In Exploration mode, rank by:
1. usage status (`unused` -> `low-use` -> `used`)
2. thematic relevance to recurring needs
3. recency of matching themes
</ranking>

<output_contract>
For each recommendation, include:
- skill name
- usage status (`unused`, `low-use`, `used`)
- why it fits (theme + concrete prior request example)
- how to invoke it effectively (clear trigger phrasing)
- path to `SKILL.md`
- evidence source (`Cursor`, `Codex`, or `both`)
- confidence (`high`, `medium`, or `low`)
</output_contract>

<quality_checks>
- Avoid recommendations based on one ambiguous request.
- If a recommendation is exploratory with sparse evidence, label confidence as `low` and say so.
- Prefer 3-7 strong recommendations over long generic lists.
- If history is sparse, state that explicitly and return best-effort recommendations.
- When both Cursor and Codex histories are available, use both and avoid double-counting duplicates.
</quality_checks>

<examples>
<example>
User request: "Recommend skills from my history"
Expected behavior: Use Standard mode and return the most recurring, high-confidence skills with evidence and trigger phrasing.
</example>

<example>
User request: "I want new skills I haven't used"
Expected behavior: Use Exploration mode and prioritize unused/low-use skills that still match repeated themes in history.
</example>

<example>
User request: "Recommend from Cursor and Codex transcripts"
Expected behavior: Mine both sources, merge evidence, de-duplicate repeated prompts across tools, and show source-aware recommendations.
</example>
</examples>
