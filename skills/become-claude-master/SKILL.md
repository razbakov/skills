---
name: become-claude-master
description: Onboard a new Claude Code user — set up their ~/.claude/CLAUDE.md, install relevant skills, and start a structured learning program covering best practices. Use when setting up Claude Code for the first time, onboarding someone to Claude Code, or continuing a learning session.
---

# Become a Claude Master

A guided onboarding and learning skill for new Claude Code users. Three phases:

## Phase 1: Setup (~5 min)

Create `~/.claude/CLAUDE.md` with the starter template and interview the user to fill in their details.

### Template

```markdown
## Personal Info

- **Name:** {{name}}
- **Address:** {{address}}

## Rules

- When I say `rule: <text>` — decide whether the rule is project-specific or global, add it to the appropriate CLAUDE.md (project or `~/.claude/CLAUDE.md`), and execute it immediately.
- When I say `learned?` — analyze the process that just happened, extract lessons/insights, and add them to the project README.
- When I say `new skill` — analyze the current conversation to extract the repeatable process that was just performed, then create a SKILL.md that captures it: trigger conditions, step-by-step process, inputs/outputs, templates used, and integration points. The skill should let anyone (human or AI) reproduce the same workflow from scratch.
- Paths and configurations should be on the project level. Skills can use paths only inside templates to set up when needed, or as aliases for lookup.
- When a task requires the user's authenticated browser session (social media, developer consoles, dashboards, any site where the user is signed in): use `mcp__Claude_in_Chrome__tabs_context_mcp` to connect to the user's existing browser, then use Claude in Chrome tools (`navigate`, `computer`, `read_page`, `find`, `form_input`).
```

### Steps

1. Check if `~/.claude/CLAUDE.md` already exists
   - If yes: read it, show the user, ask if they want to reset or keep
   - If no: proceed with creation
2. Ask the user for their name and address (or skip address if they prefer)
3. Write `~/.claude/CLAUDE.md` with the filled template
4. Explain what was created and why each rule is useful

### Explanation to give after setup

Tell the user:
- `~/.claude/CLAUDE.md` is loaded into EVERY Claude Code conversation as global instructions
- It's the place for personal info Claude needs, global rules, and cross-project preferences
- The 5 starter rules give them: instant rule creation (`rule:`), lesson extraction (`learned?`), skill creation (`new skill`), clean path management, and browser automation support
- They can add more rules anytime by saying `rule: <whatever>`
- Project-specific instructions go in `<project>/CLAUDE.md` instead

## Phase 2: Skill Installation (~10 min)

Interview the user about their work to recommend skills from https://github.com/razbakov/skills.

### Interview questions (ask 3-5, adapt based on answers)

1. What do you mainly use Claude Code for? (coding, writing, research, automation)
2. What's your tech stack? (languages, frameworks, tools)
3. Do you work with GitHub PRs, issues, CI/CD?
4. Do you write content? (blog, social media, docs)
5. Do you need browser automation? (form filling, testing, scraping)
6. Do you manage projects? (Jira, Notion, Linear)

### Skill recommendation mapping

Based on answers, suggest from these categories:

**Developer essentials:**
- `test-driven-development` — if they write code
- `writing-plans` — if they do multi-step implementations
- `github-issue` — if they use GitHub issues
- `pr-review-responder` — if they do PR reviews
- `estimation` — if they estimate tickets

**Content & writing:**
- `social-post` — if they post on social media
- `viral-threads` — if they want Twitter/X presence
- `doc-coauthoring` — if they write docs
- `latex-pdf` — if they need PDF reports

**Productivity:**
- `workflow` — for complex multi-step tasks
- `pdf` — for PDF manipulation
- `research` — for structured research
- `google-drive` — if they use Google Workspace

**Browser & automation:**
- `use-browser` — meta-skill for browser tasks
- `agent-browser` — CLI browser automation

### Installation

For each approved skill:
```bash
claude install-skill https://github.com/razbakov/skills/tree/main/skills/<skill-name>
```

## Phase 3: Learning Program

Structured learning of Claude Code best practices. One topic per session.

### Progress tracking

All progress is stored in `~/.claude/experience.md`:

```markdown
# Claude Code Learning Progress

## Current Level
Beginner | Intermediate | Advanced | Master

## Completed Topics
- [x] Topic name — YYYY-MM-DD — score: X/5
- [ ] Next topic

## Schedule
Frequency: daily | weekly
Next session: YYYY-MM-DD

## Notes
Key insights the user found valuable
```

### Curriculum (from https://code.claude.com/docs/en/best-practices)

**Module 1: Foundations**
1. Writing effective prompts for Claude Code
2. Understanding the CLAUDE.md system (global vs project)
3. Using slash commands effectively
4. Managing context and conversation length

**Module 2: Coding Workflows**
5. Code editing patterns (Edit vs Write vs Bash)
6. Test-driven development with Claude
7. Debugging strategies
8. Code review and refactoring

**Module 3: Advanced Features**
9. Creating and using skills
10. Hooks and automation
11. MCP servers and integrations
12. Multi-agent workflows (subagents)

**Module 4: Mastery**
13. Memory system and persistence
14. Custom workflows and pipelines
15. Performance optimization
16. Security best practices

**Module 5+: Extended (from broader docs + community)**
- IDE integrations (VS Code, JetBrains)
- Claude Code SDK for building agents
- API integration patterns
- Community skills and extensions

### Session format

Each learning session:
1. Check `~/.claude/experience.md` for progress
2. Review the next topic
3. Fetch the relevant docs page via WebFetch
4. Present the key concept (1 main takeaway)
5. Give a mini-challenge or quiz question
6. Record completion and score
7. Tease the next topic to build excitement
8. Offer to schedule the next session

### Scheduling

After each session, offer to create a calendar event:
- Ask: daily or weekly?
- Generate a Google Calendar link with:
  - Title: "Claude Code Training: [next topic]"
  - Description: includes the command to resume: `claude "continue my Claude Code training"`
  - Duration: 15 min
- Format: `https://calendar.google.com/calendar/render?action=TEMPLATE&text=...&details=...&dates=...`

### Inspiration quotes (rotate one per session)

- "The best way to predict the future is to create it."
- "Every expert was once a beginner."
- "Small daily improvements lead to stunning results."
- "The tool is only as powerful as the person wielding it."
- "Mastery is not about perfection, it's about progression."
