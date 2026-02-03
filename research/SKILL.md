---
name: research
description: Conduct and document research with consistent file organization. Use when researching topics, gathering information, or when the user asks to investigate a subject. Saves findings to research/yyyy-mm-dd-title.md format.
---

# Research

## Workflow

1. **Create research file**: `research/YYYY-MM-DD-topic-slug.md`
2. **Conduct research**: Use web search for current information
3. **Document findings**: Keep content short and scannable
4. **Multiple topics**: Launch sub-agents in parallel

## File Naming

```
research/
├── 2026-01-31-vue-composables.md
├── 2026-01-31-tailwind-v4.md
└── 2026-01-30-typescript-patterns.md
```

Format: `research/YYYY-MM-DD-slug.md`

- Use today's date
- Lowercase slug with hyphens
- One file per topic

## Document Structure

```markdown
# [Topic Title]

## Summary

[2-3 sentence overview]

## Key Findings

- Finding 1
- Finding 2
- Finding 3

## Sources

- [Source 1](url)
- [Source 2](url)

## Next Steps (optional)

- Action item 1
- Action item 2
```

## Research with Web Search

1. Use `WebSearch` tool to find current information
2. Use `WebFetch` for specific documentation pages
3. Extract key points, avoid copying large blocks
4. Always cite sources with URLs

## Multiple Topics

For 2+ topics, launch parallel sub-agents:

```
Task tool calls (in parallel):
- Agent 1: "Research [topic A], save to research/YYYY-MM-DD-topic-a.md"
- Agent 2: "Research [topic B], save to research/YYYY-MM-DD-topic-b.md"
```

Each agent:

- Researches one topic
- Creates one file
- Returns summary of findings

## Quality Checklist

- [ ] File saved in `research/` directory
- [ ] Filename follows `YYYY-MM-DD-slug.md` format
- [ ] Content is scannable (bullets, headers)
- [ ] Sources cited with URLs
- [ ] No walls of text
