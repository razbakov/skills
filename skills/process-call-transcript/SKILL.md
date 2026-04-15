---
name: process-call-transcript
description: Process a meeting or call transcript into structured project artifacts — session notes, contact profiles, action items routed to the right destination (markdown / Google Calendar / Google Doc / GitHub issue), and doc updates. Fetches from Jamie (meetjamie.ai) automatically when the user references a recent call they recorded. Use when the user pastes a call transcript, says "process the last Jamie call", "process my call", "extract from meeting", or when a transcript with speaker labels appears in the conversation.
---

# Process Call Transcript

Transform a raw meeting/call transcript into structured project artifacts: session notes, contact profiles, and action items routed to the destination that fits their type.

## Trigger

When the user shares text that looks like a transcript — speaker names with timestamps, conversation turns — or says "process this call/meeting", "process the last Jamie call", "get the last transcript", or similar.

## Process

### Step 0: Fetch the transcript (if not pasted)

Skip this step if the user already pasted the transcript into the conversation.

If the user references a call they recorded (Jamie, Otter, Fireflies, Granola, etc.) without pasting anything:

1. **Identify the source.** Ask which tool if it's ambiguous. If the user says "Jamie" or "my usual recording tool", assume Jamie (meetjamie.ai).

2. **Find the most recent meeting.** Jamie sends a "Summary Ready" email for every processed call. Search Gmail:
   ```bash
   gog gmail list "from:jamie newer_than:2d" --max 10 -p
   ```
   Pick the most recent "Summary Ready" subject. Each email body contains a `View Summary https://app.meetjamie.ai/meetings/<id>` link — extract the URL.

3. **Open in the authenticated browser.** Use `mcp__Claude_in_Chrome__tabs_context_mcp` to connect to the user's existing Chrome (Jamie requires login), then `navigate` to the meeting URL. **Track every tab you open** so you can close it with `mcp__Claude_in_Chrome__tabs_close_mcp` at the end of the run — including on partial failure. Never leave Jamie tabs behind in the user's browser; only close tabs you opened.

4. **Pull the Summary first** (landing tab) — this gives you the auto-generated executive summary and topic buckets. Use `get_page_text`.

5. **Pull the Transcript.** Click the "Transcript" tab. Note: `find` + `computer left_click` may target the wrong tab selector — the reliable path is a JS click:
   ```js
   [...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='Transcript').click()
   ```
   Wait ~800ms, then read `document.body.innerText` in chunks (substring slices — 2000+ chars at a time) because the transcript is long and the MCP response is truncated. Paginate through `0..end` until you have the full text.

6. **Proceed to Step 1** with the fetched transcript.

Same pattern applies to other tools if the user uses them — find the email/API that exposes the transcript URL, open in the authenticated browser, pull the text.

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
- [ ] [Task] — [Owner] — [Deadline if mentioned] — [→ routed to: gcal / gdoc / gh-issue / local]

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
| **Agent-dispatchable task** (needs research, code, content — someone else should execute it) | **GitHub issue** on the org's Control Center board | `gh issue create --repo <owner>/<project-repo> --title "..." --label "agent:<name>" --body "<S3 body>"` then `gh project item-add <board-number> --owner <owner> --url <issue-url>`. Project board number and per-agent labels live in the org CLAUDE.md. |
| **Small atomic todo** owned by the user, no specific time | **Keep as markdown checkbox** in the session notes (or local project backlog) | inline |
| **Open question** (unresolved, needs more info) | Mark clearly in session notes under "Issues" or "Open Questions" | inline |

Ask once if the category is genuinely ambiguous. Otherwise pick the obvious destination and report what you chose.

**Defaults that matter:**
- Time-bound reminders → Google Calendar (NOT scheduled-tasks, NOT local markdown, NOT a GitHub issue)
- Living checklists → Google Doc (local md becomes a one-line pointer to the doc URL)
- Agent-dispatchable work → GitHub issue on Control Center board with an `agent:*` label and an S3 body (Tension / Driver / Requirement / Response options)
- Never create a "backlog item" for something that's really just a calendar reminder
- Every GitHub issue must have exactly one `agent:*` label so it routes to an owner, and must be added to the org's project board after creation

#### Cross-repo linking

The session file usually lives in the org logbook repo (e.g. `<owner>/<org-logbook-repo>`), but the GitHub issue is created in the project code repo (e.g. `<owner>/<project-code-repo>`). Relative markdown links like `../../../<org-logbook>/...` **will not resolve** on GitHub — they only work locally.

Rules:

1. Commit and push the session file to its repo **before** creating the issue, so the URL exists.
2. In the issue body, link to the session with an **absolute** GitHub URL: `https://github.com/<owner>/<logbook-repo>/blob/<branch>/ops/sessions/YYYY-MM-DD-<topic>.md`.
3. If you forget and use a relative path, fix it with `gh issue edit <n> --repo <repo> --body "$(cat <<'EOF' ... EOF )"` — don't leave broken links.

### Step 7: Update existing docs

Check if the call introduced information that should update existing project docs:
- Content strategy / campaign docs
- Product docs / business model
- Brand guidelines
- Technical specs

Make targeted edits — don't rewrite entire docs.

### Step 8: Cross-reference

All created artifacts should link to each other:
- Session notes link to contact files, calendar events (URLs), Google Docs (URLs), GitHub issues (absolute URLs)
- Contact files link back to the session notes
- Updated docs note the source session
- GitHub issues link back to the session file using absolute `https://github.com/...` URLs (see "Cross-repo linking" under Step 6)

### Step 9: Mark the source as processed

Leave a visible marker on the original recording so the user can see at a glance which calls are done. For Jamie: rename the meeting title to `[x] <searchable summary>`.

- The `[x] ` prefix is the processed marker (scans like a checked checkbox in the meeting list).
- Replace the auto-generated Jamie title with a terse, **searchable** summary: lead with the other participant's first name, then the key topics joined by `+`. Example: `[x] Egor sync — Mafia Friday invite + DE/RU/ES expansion + Figma testing + process reminder`. This is the index the user will scan later — optimise it for ⌘F, not grammar.
- How to rename: `mcp__Claude_in_Chrome__find` for "meeting title editable textbox", then `form_input` with the new value, then press `Tab` to blur and trigger save. Verify with `document.title` — Jamie mirrors the meeting title into the tab title, so a matching tab title confirms the save landed.
- If the tab navigated away between fetch and rename, `navigate` back to the meeting URL and re-find the title element.

Equivalent markers for other tools: append a tag, move to a "processed" folder, or whatever the tool supports. The principle is the same — future-you must be able to tell at a glance which recordings are done.

### Step 10: Report

Open the report with a **Topics discussed** table of contents — a numbered list of every distinct topic the call touched, in order. This is the user's mental index of the conversation; without it they can't navigate back to anything that didn't become a structured artifact, and a lot of what makes a call valuable lives in the threads that don't. Include tangents, personal asides, philosophy detours, and "by the way" moments — those are often exactly what the user wants to revisit. The default failure mode is reporting only what produced files; resist that. If the call was short and only covered one thing, the ToC still has one entry — write it anyway.

Then list what you created and where each action item went. Example:

> **Topics discussed:**
> 1. Camera buying advice (Sony A7 IV, eBay sourcing, fixed-aperture lenses)
> 2. SDTV admin migration freeze until Apr 20
> 3. WeDance Instagram monetization pivot (€10 paid post or lottery)
> 4. Croatia festival logistics
> 5. Esoteric/spiritual tangent (Tibet, chakras, reincarnation-as-agents)
> 6. Hiring approach for Egor (JP) and Ash (IN)
>
> **Artifacts created:**
> - Session notes → `ops/sessions/...` (committed + pushed)
> - Contact → `contacts/.../contact.md`
> - Reminder "Add Michael to admin group" → Google Calendar Mon 09:00 [link]
> - At-event todo → Google Doc [link] (local md is now pointer)
> - Strategy issue → razbakov/mystery-games#3 (on Control Center board, labeled `agent:marco`)
> - Open question: Cuba donation channel — flagged in session notes
> - Jamie meeting renamed to `[x] <summary>` (marked processed)

## Important Guidelines

- **Write in the project's language** — check CLAUDE.md for language rules
- **Don't invent information** — only extract what's actually in the transcript
- **Preserve tone and nuance** — hesitant vs enthusiastic should survive the extraction
- **Multi-topic calls** — create artifacts in each relevant project
- **Never silently dump action items** — every item must have an explicit destination
- **Route, don't hoard** — a 15-item markdown checklist nobody will reopen is worse than a 1-line calendar event that will fire
