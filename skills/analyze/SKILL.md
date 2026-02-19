---
name: analyze
description: Analyze topics using the Six Thinking Hats technique with parallel agents. Use when the user asks to analyze, evaluate, assess, brainstorm, or examine a topic from multiple perspectives. Triggers on requests like "analyze X", "pros and cons of Y", "evaluate this decision", or "think through Z". Saves findings to analysis/yyyy-mm-dd-title.md
---

# Six Thinking Hats Analysis

Perform structured multi-perspective analysis using Edward de Bono's Six Thinking Hats technique. This skill launches parallel agents to explore different viewpoints simultaneously.

## Workflow

### Step 1: Launch Parallel Analysis Agents

Spin up **5 parallel agents** to analyze simultaneously:

**Agent 1 - White Hat (Facts):**
```
Analyze "[TOPIC]" using WHITE HAT thinking:

Use web search to find all known facts, data, statistics about this topic. Note any information gaps.

Format as a bullet list of facts with source and a separate section for information gaps.
```

**Agent 2 - Red Hat (Emotions):**
```
Analyze "[TOPIC]" using RED HAT thinking:

What are the immediate emotional reactions to this? What feels right or wrong intuitively?

Format as a list of gut reactions and intuitions.
```

**Agent 3 - Black Hat (Caution):**
```
Analyze "[TOPIC]" using BLACK HAT thinking:

Identify all risks, downsides, obstacles, and failure modes. What could go wrong?

Format as a bullet list of concerns and potential problems.
```

**Agent 4 - Yellow Hat (Optimism):**
```
Analyze "[TOPIC]" using YELLOW HAT thinking:

Highlight advantages, benefits, ROI, and strategic fit. Why could this succeed?

Format as a bullet list of opportunities and advantages.
```

**Agent 5 - Green Hat (Creativity):**
```
Analyze "[TOPIC]" using GREEN HAT thinking:

Generate at least 5 novel ideas, unconventional approaches, or alternatives not yet considered. Think outside the box.

Format as a numbered list with brief explanations.
```

### Step 2: Blue Hat Synthesis

After all agents complete, perform the **Blue Hat** synthesis yourself:

1. Consolidate insights from all perspectives
2. Identify patterns and contradictions
3. Rank findings by relevance
4. Recommend concrete next actions

### Output Format

Present the final analysis using this structure:

```markdown
## Analysis: [Topic]

**Key Insights:** [2-3 main takeaways]
**Tensions:** [Any conflicting perspectives]
**Recommended Actions:**
1. [Action 1]
2. [Action 2]
3. [Action 3]

### Facts
[Key facts and data gaps]

### Emotions
[Gut reactions and intuitions]

### Risks
[Cautions and potential problems]

### Benefits
[Advantages and opportunities]

### Ideas
[Creative alternatives and novel approaches]
```

## Agent Configuration

When launching Task agents:
- Use `subagent_type: "generalPurpose"` for each analysis agent
- Set `readonly: true` since these are analysis-only tasks

## Tips

- **Be specific** with the topic to reduce ambiguity
- **Iterate** if any hat's output seems incomplete
- **Human review** the Blue Hat synthesis for final decisions
- For complex topics, consider running multiple passes
