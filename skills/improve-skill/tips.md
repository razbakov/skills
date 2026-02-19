## Anthropic Prompt Engineering Best Practices (2026)

### Core Principles

**Be explicit, not implicit**
Tell the model exactly what you want. Don't rely on it to infer "above and beyond" behavior — state it directly.

```
Bad:  "Create an analytics dashboard"
Good: "Create an analytics dashboard. Include as many relevant features as possible. Go beyond the basics to create a fully-featured implementation."
```

**Add context/motivation behind instructions**
Explain *why* a rule exists. The model generalizes from explanations better than blind rules.

```
Bad:  "NEVER use ellipses"
Good: "Never use ellipses — your response will be read aloud by TTS and ellipses won't pronounce correctly."
```

**Tell it what to DO instead of what NOT to do**
This applies especially to formatting:
```
Bad:  "Do not use markdown"
Good: "Your response should be composed of smoothly flowing prose paragraphs."
```

---

### Recommended Techniques (in order of effectiveness)

1. **Long context tips** — use the full context window effectively
2. **Chain complex prompts** — break tasks into steps
3. **Give Claude a role via system prompt** — e.g. "You are a seasoned data scientist..."
4. **Use XML tags** — structure sections clearly: `<instructions>`, `<context>`, `<examples>`
5. **Let Claude think (chain of thought)** — ask it to reason before answering
6. **Use examples (multishot)** — input/output pairs are very effective

---

### System Prompt Patterns That Work

**Control action vs. suggestion behavior:**
```xml
<default_to_action>
By default, implement changes rather than only suggesting them. If the user's intent is unclear, infer the most useful likely action and proceed.
</default_to_action>
```

Or the opposite:
```xml
<do_not_act_before_instructions>
Do not jump into implementation unless clearly instructed. Default to research and recommendations when intent is ambiguous.
</do_not_act_before_instructions>
```

**Control formatting:**
```xml
<avoid_excessive_markdown_and_bullet_points>
Write in clear, flowing prose. Reserve markdown for code blocks and simple headings.
Avoid bullet points unless truly discrete items. Never output a series of overly short bullet points.
</avoid_excessive_markdown_and_bullet_points>
```

**Prevent over-engineering:**
```xml
Avoid over-engineering. Only make changes that are directly requested. Don't add docstrings, refactors, or abstractions beyond what was asked.
```

**Parallel tool calls:**
```xml
<use_parallel_tool_calls>
If multiple tool calls have no dependencies, make them all in parallel. Maximize parallelism for speed.
</use_parallel_tool_calls>
```

---

### Key Gotchas for Claude 4.x

| Issue | Fix |
|-------|-----|
| Model overtriggers on tools | Replace "CRITICAL: MUST use..." with "Use this tool when..." |
| Model thinks too much / slow | Remove "think carefully", "be thorough" — these amplify already-proactive behavior |
| Model over-engineers solutions | Add explicit "keep it minimal" guidance |
| Model suggests instead of acts | Say "Change X" not "Can you suggest changes to X?" |
| Risky irreversible actions | Add explicit confirmation requirements for destructive ops |

---

### Most Impactful Takeaways

1. **Match prompt style to desired output style** — if you want prose, write your prompt in prose (not bullets)
2. **Remove anti-laziness prompts** — "be thorough", "think carefully" now backfire on Claude 4.x
3. **XML tags** are the single most reliable formatting tool for structuring system prompts
4. **Examples beat instructions** — showing input/output pairs is more effective than describing behavior

The full docs are at [docs.anthropic.com/en/docs/build-with-claude/prompt-engineering](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview). The Claude 4 best practices page is particularly worth bookmarking — it's clearly been updated very recently.
