# Skills

A collection of reusable Cursor skills for structured workflows and methodologies.

## Overview

This repository contains specialized skills that extend Cursor's capabilities with domain-specific knowledge, workflows, and best practices. Each skill is a self-contained guide that helps you work more effectively on specific types of tasks.

## Available Skills

### [analyze](analyze/SKILL.md)

**Six Thinking Hats Analysis** - Perform structured multi-perspective analysis using Edward de Bono's Six Thinking Hats technique. Launches parallel agents to explore different viewpoints simultaneously (facts, emotions, risks, benefits, creativity, and synthesis).

Use when: analyzing topics, evaluating decisions, brainstorming, or examining subjects from multiple perspectives.

### [app](app/SKILL.md)

**Documentation-First, Test-Driven Development** - A structured workflow for building applications following a documentation-first, test-driven approach. Guides through phases: vision, architecture, data modeling, integration tests, unit tests, and implementation.

Use when: starting new features, implementing functionality, or following structured development processes.

### [research](research/SKILL.md)

**Research Documentation** - Conduct and document research with consistent file organization. Saves findings to `research/YYYY-MM-DD-title.md` format with structured summaries, key findings, and sources.

Use when: researching topics, gathering information, or investigating subjects.

### [website](website/SKILL.md)

**Content-First, Mobile-First Website Creation** - A comprehensive methodology for creating modern websites. Guides through content strategy, design systems, technical architecture, and implementation with a focus on mobile-first, accessible, and performant web experiences.

Use when: starting any new website project.

## Usage

These skills are automatically available to Cursor when placed in your skills directory (typically `~/.cursor/skills/` or `~/.codex/skills/`). Cursor will detect and use them when relevant to your requests.

To use a skill manually, reference it in your conversation with Cursor, and it will follow the workflow defined in the skill file.

## License

This collection of skills is provided as-is for use with Cursor AI.
