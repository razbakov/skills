---
name: analyze
description: Analyze topics using the Six Thinking Hats technique with parallel agents. Use when the user asks to analyze, evaluate, assess, brainstorm, or examine a topic from multiple perspectives. Triggers on requests like "analyze X", "pros and cons of Y", "evaluate this decision", or "think through Z".
---

# Six Thinking Hats Analysis

Perform structured multi-perspective analysis using Edward de Bono's Six Thinking Hats technique. This skill launches parallel agents to explore different viewpoints simultaneously.

## The Six Hats

| Hat | Perspective | Focus |
|-----|-------------|-------|
| **White** | Facts & Data | What do we know? What information is missing? |
| **Red** | Emotions & Intuition | Gut reactions, feelings, immediate responses |
| **Black** | Caution & Risks | What could go wrong? Weaknesses, obstacles |
| **Yellow** | Optimism & Benefits | Strengths, advantages, why it could work |
| **Green** | Creativity & Alternatives | New ideas, novel approaches, possibilities |
| **Blue** | Process & Synthesis | Orchestration, summary, next steps |

## Workflow

### Step 1: Launch Parallel Analysis Agents

Spin up **3 parallel agents** to analyze simultaneously:

**Agent 1 - Facts & Feelings:**
```
Analyze "[TOPIC]" using Six Thinking Hats:

WHITE HAT (Facts): List all known facts, data, statistics about this topic. Note any information gaps.

RED HAT (Emotions): What are the immediate emotional reactions to this? What feels right or wrong intuitively?

Format as two clearly labeled sections.
```

**Agent 2 - Risks & Benefits:**
```
Analyze "[TOPIC]" using Six Thinking Hats:

BLACK HAT (Caution): Identify all risks, downsides, obstacles, and failure modes. What could go wrong?

YELLOW HAT (Optimism): Highlight advantages, benefits, ROI, and strategic fit. Why could this succeed?

Format as two clearly labeled sections.
```

**Agent 3 - Creativity:**
```
Analyze "[TOPIC]" using Six Thinking Hats:

GREEN HAT (Creativity): Generate at least 5 novel ideas, unconventional approaches, or alternatives not yet considered. Think outside the box.

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
## Six Hats Analysis: [Topic]

### ⚪ White Hat – Facts
[Key facts and data gaps]

### 🔴 Red Hat – Emotions
[Gut reactions and intuitions]

### ⚫ Black Hat – Risks
[Cautions and potential problems]

### 🟡 Yellow Hat – Benefits
[Advantages and opportunities]

### 🟢 Green Hat – Ideas
[Creative alternatives and novel approaches]

### 🔵 Blue Hat – Synthesis
**Key Insights:** [2-3 main takeaways]
**Tensions:** [Any conflicting perspectives]
**Recommended Actions:**
1. [Action 1]
2. [Action 2]
3. [Action 3]
```

## Agent Configuration

When launching Task agents:
- Use `subagent_type: "generalPurpose"` for each analysis agent
- Set `readonly: true` since these are analysis-only tasks
- Launch all 3 agents in a **single message** for parallel execution

## Tips

- **Be specific** with the topic to reduce ambiguity
- **Iterate** if any hat's output seems incomplete
- **Human review** the Blue Hat synthesis for final decisions
- For complex topics, consider running multiple passes
