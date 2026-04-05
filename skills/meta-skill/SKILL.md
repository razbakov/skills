---
description: Decompose a skill into child skills and convert it into a meta-skill orchestrator. Use when the user says "meta-skill X", "decompose skill X", or "break skill X into sub-skills". Takes an existing skill with multiple sequential tasks and splits each task into its own standalone skill, then rewrites the original as a meta-skill that triggers child skills in order via the Skill tool.
user_invocable: true
argument: skill name to decompose
---

# Meta-Skill: Decompose & Orchestrate

You are converting skill **`{argument}`** into a meta-skill with child skills.

## Process

### 1. Read the source skill

```
~/.cursor/skills/{argument}/SKILL.md
```

If not found, check project-local `.claude/skills/{argument}/SKILL.md`.

Parse the SKILL.md fully: frontmatter, description, all steps/tasks/phases.

### 2. Identify discrete tasks

Extract every distinct task, phase, or step from the skill. A task is discrete if:
- It has a clear single responsibility
- It could run independently given the right inputs
- It produces a defined output that subsequent tasks consume

List the tasks in execution order. Confirm with the user before proceeding:

```
I found N tasks in skill "{argument}":
1. task-name-a — one-line summary
2. task-name-b — one-line summary
3. task-name-c — one-line summary

Should I create a child skill for each and convert "{argument}" into a meta-skill?
```

### 3. Create child skills

For each task, create a standalone skill at:

```
~/.cursor/skills/{argument}-{task-name}/SKILL.md
```

Each child skill MUST:
- Have proper frontmatter with `description` and `user_invocable: true`
- Be fully self-contained — include all context needed to run independently
- Define its **inputs** (what it expects) and **outputs** (what it produces)
- Preserve all logic, templates, commands, and details from the original task
- NOT reference the parent meta-skill — it must work standalone

### 4. Rewrite the original as a meta-skill

Replace the original `{argument}/SKILL.md` with a meta-skill that:
- Keeps the same frontmatter `description` (updated to mention orchestration)
- Lists child skills in execution order
- Uses the `Skill` tool to invoke each child skill sequentially
- Passes outputs from one skill as context to the next
- Handles the flow: run skill 1 → capture result → run skill 2 → ... → done

Use this template for the rewritten meta-skill:

```markdown
---
description: (original description, updated to mention it orchestrates child skills)
user_invocable: true
argument: (same as original if applicable)
---

# {Skill Name} (Meta-Skill)

This is a meta-skill that orchestrates the following child skills in order:

1. **{argument}-{task-1}** — summary
2. **{argument}-{task-2}** — summary
3. **{argument}-{task-3}** — summary

## Execution

Run each child skill sequentially using the Skill tool:

### Step 1: {task-1}
Invoke: `//{argument}-{task-1}`
Captures: (what this step produces for the next)

### Step 2: {task-2}
Invoke: `//{argument}-{task-2}`
Depends on: (what it needs from step 1)
Captures: (what this step produces)

### Step 3: {task-3}
Invoke: `//{argument}-{task-3}`
Depends on: (what it needs from previous steps)

## Notes
- Each child skill can also be run independently via `/{argument}-{task-name}`
- If a step fails, fix the issue and re-run that specific child skill
```

### 5. Verify

- Confirm all child skill files exist and have valid frontmatter
- Confirm the meta-skill references all children correctly
- List the created files for the user

## Output

```
Decomposed "{argument}" into N child skills:
- /{argument}-{task-1} — summary
- /{argument}-{task-2} — summary
- /{argument}-{task-3} — summary

Meta-skill "/{argument}" now orchestrates all children in order.
Each child skill can also be invoked independently.
```
