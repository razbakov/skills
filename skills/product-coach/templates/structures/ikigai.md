# Workspace Structure: Ikigai

Personal life OS — mission, vision, portfolio oversight, relationship management, and daily reflection in one workspace. For people who want to align their life around purpose, not just ship products.

```
<name>/
├── README.md                           # Mission, vision, OKRs, status, lessons, rules
├── CLAUDE.md -> README.md              # AI context symlink
├── AGENTS.md -> README.md              # AI context symlink
├── profile.md                          # Personality, strengths, motivation patterns, ikigai hypothesis
├── PROJECTS.md                         # All projects inventory with status and next actions
├── contacts/                           # CRM — people you work with
│   └── <firstname-lastname>/
│       ├── contact.md                  # Profile with frontmatter (name, type, projects, status)
│       ├── meetings/                   # Meeting transcripts + summaries
│       │   ├── README.md
│       │   └── YYYY-MM-DD-topic.txt
│       └── chats/                      # Chat history by day and platform
│           ├── YYYY-MM-DD-platform.txt
│           └── YYYY-MM-DD-platform/    # Attachments (voice transcripts, media)
├── sessions/                           # Daily logs and session transcripts
│   ├── YYYY-MM-DD-topic.md            # Check-ins, working sessions, planning
│   ├── YYYY-MM-DD-browser.md          # Browser history (imported from Chrome)
│   └── YYYY-MM-DD-ai-sessions.md      # AI transcript summary with raw paths
├── assessments/                        # Self-assessments, reviews, retrospectives
├── decisions/                          # Life and career decision records
│   └── <NNN>-<slug>.md
├── .inbox/                             # Staging area for unprocessed information
├── .archive/                           # Retired or migrated content
└── .bin/                               # Helper scripts
    └── link-readmes.sh                 # Creates AI symlinks
```

## Key concepts

### Profile (`profile.md`)

Your ikigai hypothesis — the intersection of what you love, what you're good at, what the world needs, and what you can be paid for. Also includes personality type, motivation patterns, values, and coaching preferences.

### Projects (`PROJECTS.md`)

Portfolio-level view of all active projects. Each project has its own workspace elsewhere — this file is a cache for prioritization and status tracking. Sync regularly; project READMEs are the source of truth.

### Contacts (`contacts/`)

Lightweight CRM. Each person gets a directory with a `contact.md` (frontmatter: name, type, projects, location, contact info, status) and subdirectories for meetings and chats.

### Sessions (`sessions/`)

Daily activity logs — AI working sessions, browser history, check-ins, planning notes. The raw material for weekly reviews and pattern recognition.

### Decisions (`decisions/`)

Non-obvious life and career choices recorded as decision records (context, decision, consequences). Not every decision — only the ones you'll want to revisit.

## Applicable phases

Phases 0–4 (Understand block). Phases 5–7 (Validate) and 8–15 (Commit) apply only if individual projects within the portfolio use the startup structure.

## When to use

- Personal development and life planning
- Portfolio management across multiple projects
- Anyone who wants a structured "life OS" with mission, vision, and OKRs
- Solopreneurs managing relationships, projects, and daily routines from one hub
