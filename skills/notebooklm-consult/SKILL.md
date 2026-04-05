# NotebookLM Consult

Connect to an existing NotebookLM notebook and consult it on specific topics — ask questions, get grounded answers with citations, and optionally generate artifacts.

## Trigger

When the user asks to consult a notebook, query NotebookLM, ask a question to their research, look something up in their notes, or references a specific NotebookLM notebook by name or ID.

## Prerequisites

- `notebooklm` CLI installed (`pipx install "notebooklm-py[browser]"`)
- Authenticated: `notebooklm login` (one-time browser auth)

## Process

### Step 1: Select the notebook

List available notebooks and match by name or ID:

```bash
notebooklm list
```

If the user specified a notebook name, match it from the list. If ambiguous, show options and ask. Once identified:

```bash
notebooklm use <notebook_id>
```

If no notebook is specified, show the list and ask the user to pick one.

### Step 2: Understand the notebook context

Get a summary and source list to understand what content is available:

```bash
notebooklm summary --topics
notebooklm source list
```

Share a brief overview with the user: notebook title, number of sources, and suggested topics.

### Step 3: Configure persona (optional)

If the user wants a specific consultation style, configure the chat mode:

```bash
# For learning/educational queries
notebooklm configure --mode learning-guide

# For quick answers
notebooklm configure --mode concise

# For deep analysis
notebooklm configure --mode detailed

# For custom expert persona
notebooklm configure --persona "Act as a ${DOMAIN} expert consultant"
```

Default: skip this step (uses notebook's existing configuration).

### Step 4: Ask questions

Query the notebook with the user's questions:

```bash
notebooklm ask "What does the research say about ${TOPIC}?"
```

For follow-up questions in the same conversation context, just keep asking:

```bash
notebooklm ask "Can you elaborate on that second point?"
```

To focus on specific sources within the notebook:

```bash
# First check source IDs
notebooklm source list --json

# Then query specific sources
notebooklm ask -s <source_id> -s <source_id> "Compare these two perspectives on ${TOPIC}"
```

For structured output with citation references:

```bash
notebooklm ask "${QUESTION}" --json
```

To save an important answer as a note inside the notebook:

```bash
notebooklm ask "${QUESTION}" --save-as-note --note-title "Key findings on ${TOPIC}"
```

### Step 5: Multi-turn consultation

For deeper exploration, chain questions logically:

1. Start broad: "What are the main themes covered?"
2. Narrow down: "What specific evidence supports ${CLAIM}?"
3. Compare: "How do different sources agree or disagree on ${POINT}?"
4. Synthesize: "Summarize the practical implications for ${USE_CASE}"

### Step 6: Generate artifacts (optional)

If the user wants deliverables from the consultation:

```bash
# Study guide summarizing the consultation topic
notebooklm generate report --style study-guide --wait

# Quiz to test understanding
notebooklm generate quiz --difficulty medium

# Audio summary for later listening
notebooklm generate audio "Focus on ${TOPIC}" --wait
notebooklm download audio ./consult-${TOPIC}.mp3

# Mind map of concepts
notebooklm generate mind-map --wait
```

### Step 7: Save consultation history (optional)

```bash
# View full Q&A history
notebooklm history --show-all

# Save as a note for future reference
notebooklm history --save --note-title "Consultation: ${TOPIC} - $(date +%Y-%m-%d)"
```

## Output

- Grounded answers from NotebookLM with inline citations referencing specific sources
- Optional: saved notes, study guides, audio summaries, or other artifacts
- Consultation history preserved in the notebook

## Notes

- Answers are grounded in the notebook's sources — NotebookLM will not hallucinate beyond what's in the content
- Use `--json` flag on `ask` to get structured output with source references for programmatic use
- Conversations persist — follow-up questions maintain context from earlier in the session
- Use `-s` flag to scope questions to specific sources when the notebook has many
- If auth expires, re-run `notebooklm login`
