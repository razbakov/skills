---
name: history-skill-recommender
description: Recommend useful installed skills by reading previous Cursor sessions and the skills inventory in scan-cache.json, then reasoning about recurring user needs. Use when asked to suggest skills from history and explain why and how to use each recommendation.
---

# History Skill Recommender

Recommend skills from transcript history

## Inputs

- Skill index: `~/.config/skills-manager/scan-cache.json`
- Session history: `~/.cursor/projects/*/agent-transcripts/*`

## Workflow

1. Read `scan-cache.json` and collect skill entries with:
- `name`
- `description`
- `skillMdPath`
2. Read transcript files and extract user requests from `<user_query>` blocks.
3. Identify repeated needs and themes from history:
- file types (`.pptx`, `.docx`, `.xlsx`, etc.)
- task intents (create, fix, analyze, convert, summarize, plan)
- domain signals (Jira, Confluence, security, frontend, reporting, etc.)
4. Match these themes to skill descriptions and prioritize:
- explicit trigger matches in description
- repeated requests across multiple sessions
- recency (prefer recent recurring requests over old one-offs)
5. Recommend top skills and explain each with:
- why: concrete transcript evidence and matching theme
- how: what users should say to trigger the skill reliably

## Output Contract

For each recommendation, include:

- skill name
- why it fits (theme + example prior request)
- how to invoke it effectively (trigger phrasing)
- path to `SKILL.md` for follow-up usage

## Notes

- Avoid recommending skills based on a single ambiguous request.
- Prefer 3-7 high-confidence recommendations over long generic lists.
- If history is sparse, say so and provide best-effort recommendations with lower confidence wording.
