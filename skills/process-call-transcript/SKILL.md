---
name: process-call-transcript
description: Process a meeting or call transcript into structured project artifacts — session notes, contact profiles, action items routed to the right destination (markdown / Google Calendar / Google Doc / Notion), and doc updates. Use when the user pastes a call transcript, meeting notes, or conversation log with speaker names and timestamps. Also trigger for "process this call", "extract from meeting", "save call notes", or when a transcript with speaker labels appears in the conversation.
---

# Process Call Transcript

Transform a raw meeting/call transcript into structured project artifacts: session notes, contact profiles, and action items routed to the destination that fits their type.

## Trigger

When the user shares text that looks like a transcript — speaker names with timestamps, conversation turns, or explicitly says "process this call/meeting".

## Process

### Step 1: Parse the transcript

Identify from the raw text:
- **Participants**: names, roles (who asked questions vs who answered)
- **Date**: from timestamps or context
- **Topic**: the main subject of the call
- **Duration**: from first to last timestamp

### Step 2: Extract structured information

Read through the entire transcript and categorize everything into:

- **Decisions** — agreements, confirmations ("we'll do X", "let's go with")
- **Action items** — tasks, promises, deadlines ("I'll send you", "by tomorrow")
- **New contacts** — participants or people mentioned who aren't in the system
- **Ideas** — new concepts, features, approaches ("what if we")
- **Key facts** — numbers, dates, constraints, specs
- **Issues / blockers** — problems, concerns, broken things

### Step 3: Determine the target project

Based on the call topic, identify which project/org the artifacts belong to. Check the Project Path Registry in the org/project CLAUDE.md. All artifacts go into that project's structure.

### Step 4: Save session notes

Create `ops/sessions/YYYY-MM-DD-<topic>.md` in the target project:

```markdown
# Call: [Topic] — [Date]

**Participants:** [Name 1] (role), [Name 2] (role)
**Duration:** [start] - [end]
**Context:** [How they met, why the call happened]

## Key Decisions
- [Decision 1]

## Action Items
- [ ] [Task] — [Owner] — [Deadline if mentioned] — [→ routed to: gcal / gdoc / notion / local]

## Ideas
- [Idea with context]

## Key Facts
- [Fact 1]

## Issues
- [Issue description]

## Notes
[Important context or quotes that don't fit above]
```

### Step 5: Create/update contacts

For each new person, create `contacts/<firstname-lastname>/contact.md`:

```markdown
---
name: [Full Name]
type: [collaborator/freelancer/partner/lead]
projects: [relevant projects]
location: [if mentioned]
contact: [telegram/email/phone if shared]
status: active
met: [how they connected]
---

## Context
[Role, what they do, relationship to the project]

## Preferences & Boundaries
[Only if explicitly stated: comms channels they use/avoid, group chat preferences, themes/styles they dislike, scheduling constraints]

## Notes from [Date]
[Key points about this person from the call]
```

Preferences matter — people told you how they want to be worked with. Capture it.

### Step 6: Route action items to the right destination

Do NOT dump every action item into a markdown backlog. Classify each one and route it:

| Type of action item | Destination | How |
|---|---|---|
| **Reminder at a specific time** ("remind me Monday", "next week", date-bound) | **Google Calendar event** | `gog cal create primary --summary "..." --from "YYYY-MM-DDTHH:MM:SS+02:00" --to "..." --description="..."` |
| **Living checklist** ("at event todo", "packing list", "pre-launch checklist" — a list that gets edited repeatedly) | **Google Doc** | `gog docs create "Title" --file <seed.md>` then replace the local md with a pointer to the doc URL |
| **Agent-dispatchable task** (needs research, code, content — someone else should execute it) | **Notion Control Center card** | Create card with S3 analysis, assign agent |
| **Small atomic todo** owned by Alex, no specific time | **Keep as markdown checkbox** in the session notes (or local project backlog) | inline |
| **Open question** (unresolved, needs more info) | Mark clearly in session notes under "Issues" or "Open Questions" | inline |

Ask once if the category is genuinely ambiguous. Otherwise pick the obvious destination and report what you chose.

**Defaults that matter:**
- Time-bound reminders → Google Calendar (NOT scheduled-tasks, NOT local markdown)
- Living checklists → Google Doc (local md becomes a one-line pointer to the doc URL)
- Never create a "backlog item" for something that's really just a calendar reminder

### Step 7: Update existing docs

Check if the call introduced information that should update existing project docs:
- Content strategy / campaign docs
- Product docs / business model
- Brand guidelines
- Technical specs

Make targeted edits — don't rewrite entire docs.

### Step 8: Cross-reference

All created artifacts should link to each other:
- Session notes link to contact files, calendar events (URLs), Google Docs (URLs), Notion cards
- Contact files link back to the session notes
- Updated docs note the source session

### Step 9: Report

Summarize what you created and where each action item went. Example:

> - Session notes → `ops/sessions/...`
> - Contact → `contacts/.../contact.md`
> - Reminder "Add Michael to admin group" → Google Calendar Mon 09:00 [link]
> - At-event todo → Google Doc [link] (local md is now pointer)
> - Open question: Cuba donation channel — flagged in session notes

## Important Guidelines

- **Write in the project's language** — check CLAUDE.md for language rules
- **Don't invent information** — only extract what's actually in the transcript
- **Preserve tone and nuance** — hesitant vs enthusiastic should survive the extraction
- **Multi-topic calls** — create artifacts in each relevant project
- **Never silently dump action items** — every item must have an explicit destination
- **Route, don't hoard** — a 15-item markdown checklist nobody will reopen is worse than a 1-line calendar event that will fire
