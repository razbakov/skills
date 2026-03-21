# Skills

55 plug-and-play skills for Claude Code and Cursor that turn your AI assistant into a product team — coach, PM, designer, marketer, and DevOps included. Just type a slash command and go.

## Who is this for

- **Solo founders** who need a full product team but only have an AI — from idea validation to shipped product.
- **Developers** who want structured workflows (BDD, TDD, sprint planning, PR reviews) baked into their editor.
- **Content creators** who need posters, videos, QR codes, SEO audits, and viral threads without leaving the terminal.
- **Managers and coaches** who want daily reviews, weekly planning, personal coaching, and portfolio analysis on autopilot.

## Why it matters

Your AI assistant is only as good as its instructions. Without skills, you get generic responses. With skills, you get battle-tested workflows that encode real methodology — design sprints, story mapping, BDD, Sociocracy 3.0, GTD, Six Thinking Hats — into repeatable slash commands.

These skills were built through daily use across real projects. They compose well: `/startup-coach` generates a backlog, `/estimation` sizes the stories, `/developing-tickets` implements them, `/pr-review-responder` handles the review.

## What's inside

### Product & Strategy

| Skill | What it does |
|-------|-------------|
| `startup-coach` | Design-thinking coach: mission, JTBD, user journey, story map, backlog, brand, architecture |
| `project-start` | README, user journey, story map, architecture, AI context — before writing code |
| `design-sprint` | 6-phase structured sprint to validate ideas before building |
| `startup` | Generate and analyze SaaS business ideas in parallel |
| `year-review` | Level 10 Life assessment — score 10 areas, find patterns, create action plan |

### Development Workflow

| Skill | What it does |
|-------|-------------|
| `user-story` | Requirements to INVEST-compliant stories with acceptance criteria |
| `estimation` | Story point estimation with factor scoring |
| `bdd-from-ux` | BDD scenarios grounded in actual UI/UX implementation |
| `developing-tickets` | Full ticket lifecycle: fetch, plan, implement, verify |
| `thank-you-next` | Pick next story from backlog, plan it, build it — hands-free |
| `review-backlog` | Parallel quality audit of stories against INVEST principles |
| `pr-review-responder` | Fetch PR comments, fix code, reply, resolve threads |
| `workflow` | Orchestrate multi-step tasks with planning and subagents |

### Daily Operations

| Skill | What it does |
|-------|-------------|
| `daily-review` | Full daily review: browser history, AI transcripts, app usage, project sync, plan |
| `weekly-review` | Saturday review + next week planning with calendar blocks |
| `scrum` | Check status of all dispatched agents across tmux sessions |
| `inbox` | Fire-and-forget agent dispatch with tmux + worktree isolation |
| `personal-coach` | Coaching sessions: assessment, check-in, unblock, build jam, journal |

### Content & Marketing

| Skill | What it does |
|-------|-------------|
| `brand-poster` | Generate posters and social media graphics |
| `image-from-gemini` | AI image generation via Google Gemini |
| `image-from-html` | Code-first graphics from HTML/CSS, screenshotted to PNG |
| `image-from-latex` | Vector-quality graphics from LaTeX/TikZ |
| `image-to-svg` | Raster to SVG conversion via Potrace |
| `qr-code-generator` | Styled QR codes with UTM tracking, logos, and gradients |
| `video-podcast-producer` | Split recordings into clips, thumbnails, YouTube metadata, Shorts |
| `latex-pdf` | Professional PDF reports from Python-generated LaTeX |
| `content-seo-agent` | SEO audit, blog posts, content calendar, analytics reports |
| `storyteller-tactics` | Narrative craft using Pip Decks Storyteller Tactics |
| `viral-threads` | Transform content into viral social media threads |
| `transcribe-via-faster-whisper` | Local video/audio transcription via Docker |

### Integrations

| Skill | What it does |
|-------|-------------|
| `atlassian` | Jira + Confluence from the terminal |
| `google-drive` | Gmail, Calendar, Drive, Docs, Sheets via `gog` CLI |
| `export-chat-history` | Export AI chat history for the current project |

### Business & Analysis

| Skill | What it does |
|-------|-------------|
| `sales-bizdev-agent` | Lead pipelines, outreach, deal tracking, CRM, pipeline reports |
| `portfolio-hiring-analysis` | Skill gap analysis across projects, role recommendations, job descriptions |
| `analyze` | Six Thinking Hats analysis with 5 parallel agents |
| `dependency-vuln-report` | Dependency vulnerability scan with remediation priority |

### Skill Tooling

| Skill | What it does |
|-------|-------------|
| `improve-skill` | Rewrite a SKILL.md using prompt engineering best practices |
| `meta-skill` | Decompose a skill into child skills and orchestrate them |
| `large-skill` | Design and refactor complex skills with decision trees |

## Skill Packs

Pre-built combinations for specific roles. Install a pack to get a curated set of skills:

| Pack | Skills | Use case |
|------|--------|----------|
| `frontend.json` | agent-browser, dogfood, figma-implement-design | Frontend development with Figma and browser testing |
| `mission-control.json` | atlassian, project-start, user-story | Project management with Jira/Confluence |
| `ommax-dev.json` | atlassian, developing-tickets, estimation, workflow, and more | Full dev workflow with Jira integration |
| `project-management.json` | atlassian, developing-tickets, estimation, google-drive, and more | PM toolkit with Google Workspace |

## How to install

### With skill-mix

Install the entire collection:

```bash
npx -y skill-mix https://github.com/razbakov/skills
```

Install a single skill:

```bash
npx -y skill-mix https://github.com/razbakov/skills/startup-coach
```

### With skills.sh

```bash
# Add the entire skills repo
npx skills add razbakov/skills

# Or add just one skill
npx skills add https://github.com/razbakov/skills --skill startup-coach
```

### Install a skill pack

Download a pack file and use it as your project's skill manifest:

```bash
curl -O https://raw.githubusercontent.com/razbakov/skills/main/frontend.json
```

## How to use

Once installed, invoke any skill by name in Claude Code or Cursor:

```
/startup-coach
/daily-review
/estimation
```

Skills trigger automatically when your prompt matches their description — or call them explicitly with a slash command.

## Contributing

Each skill lives in `skills/<name>/` and contains a `SKILL.md` with the full prompt. Use `/improve-skill` to refine existing skills or `/meta-skill` to decompose complex ones.

## License

This collection of skills is provided as-is for use with AI coding assistants.
