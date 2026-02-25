---
name: sprint-release
description: Use when releasing staging to main, preparing release notes, creating a release branch, or updating Jira release versions. Use when the user says "release", "prepare release", "release notes", "merge staging to main", or "sprint release".
---

# Sprint Release

Prepare and publish a sprint release from staging to main.

**REQUIRED:** Use the **atlassian** skill for all Jira operations.

## Procedure

Execute steps in order. Use TodoWrite to track progress.

### 1. Gather Changes

```bash
git log main..staging --oneline --no-merges
git diff main..staging --stat | tail -3
```

Extract unique ticket IDs from commit messages matching the project's ticket pattern.

### 2. Cross-Check with Jira

Use the **atlassian** skill to search for tickets with the pre-release status (e.g. "On Staging") in the project.

Compare the two lists. Flag:
- Tickets in git but not in pre-release status — check their actual Jira status
- Tickets in pre-release status but missing from git — investigate before proceeding

Report the comparison to the user and confirm alignment before continuing.

### 3. Write Release Notes

Save to `docs/releases/YYYY-MM-DD.md`.

**Format rules:**
- Audience is stakeholders/PM, not developers
- Group by product area, not by change type
- Use plain language describing user-facing impact
- Include ticket ID inline: `**Feature name** (PROJ-123) — description`
- Separate internal/infra work into its own section
- No commit log, no file stats, no technical jargon

### 4. Create Release Branch

```bash
git checkout staging
git checkout -b release/YYYY-MM-DD
```

### 5. Update Jira Release Version

Use the **atlassian** skill to:

1. **Find or create the version** named `YYYY-MM-DD` in the project with the release date set
2. **Set the version description** — a one-line summary per product area condensing the release notes
3. **Link all tickets** to the fix version by updating each ticket's `fixVersions` field

### 6. Release Hub Rich Text (manual)

The "Give this section a name" area on the Jira release hub page has no public REST API. Provide the user with ready-to-paste content and instructions:

1. Open the release page URL
2. Click "Give this section a name" → type **Release Notes**
3. Paste the formatted content into the text area

Format the paste-ready content grouped by area with bullet points (same structure as the markdown release notes but without markdown syntax).

### 7. Summary

Present to the user:
- Release branch name
- Link to Jira release page
- Number of tickets linked
- Any discrepancies found in step 2
- Reminder to paste release notes into the release hub (step 6)
