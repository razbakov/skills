---
name: sprint-release
description: Use when releasing staging to main, preparing release notes, creating a release branch, or updating Jira release versions. Use when the user says "release", "prepare release", "release notes", "merge staging to main", or "sprint release".
---

# Prepare release notes

### 1. Gather Changes from git

- see commit messages
- see file changes

### 2. Write Release Notes

Add to `CHANGELOG.md`.

**Format rules:**
- Audience is stakeholders/PM, not developers
- Group by product area, not by change type
- Use plain language describing user-facing impact
- Include ticket ID inline: `**Feature name** (PROJ-123) — description`
- Separate internal/infra work into its own section
- No commit log, no file stats, no technical jargon
