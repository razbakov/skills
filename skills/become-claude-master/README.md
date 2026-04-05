# Become a Claude Master

Guided onboarding and structured learning program for Claude Code. Three phases take you from zero to power user.

## What it does

1. **Setup** (~5 min) -- Creates `~/.claude/CLAUDE.md` with starter rules for instant rule creation, lesson extraction, skill creation, and browser automation
2. **Skill Installation** (~10 min) -- Interviews you about your work and recommends skills from the [razbakov/skills](https://github.com/razbakov/skills) collection
3. **Learning Program** (ongoing) -- 16-topic curriculum covering prompting, coding workflows, hooks, MCP servers, multi-agent patterns, memory, and security

## Usage

```
/become-claude-master
```

Or say: "set up Claude Code", "onboard me", "continue my Claude Code training"

## Learning Curriculum

| Module | Topics |
|--------|--------|
| Foundations | Prompting, CLAUDE.md system, slash commands, context management |
| Coding Workflows | Edit patterns, TDD, debugging, code review |
| Advanced | Skills, hooks, MCP servers, multi-agent workflows |
| Mastery | Memory system, custom pipelines, performance, security |

## Progress Tracking

Progress is saved to `~/.claude/experience.md` with:
- Current level (Beginner / Intermediate / Advanced / Master)
- Completed topics with dates and scores
- Assessment results identifying gaps
- Schedule for next session

## Quick Assessment

The skill includes a quick assessment that identifies your gaps before starting. It checks:
- Prompting strategies
- Hooks familiarity
- Memory system usage
- Multi-agent workflow experience

Then tailors the curriculum to fill your specific gaps rather than re-teaching what you already know.

## Install

```bash
claude install-skill https://github.com/razbakov/skills/tree/main/skills/become-claude-master
```
