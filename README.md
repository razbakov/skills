# Stop Vibe-Coding. Start AI-Engineering.

90+ skills that turn Claude Code into a full product team. Type a slash command, get a battle-tested workflow — not a generic AI response.

**You don't need to know how to code.** You need to know how to think clearly about what you want. These skills handle the rest: strategy, design, development, testing, marketing, and operations.

## Start here

### Never used AI before?

```bash
claude install-skill https://github.com/razbakov/skills/tree/main/skills/become-claude-master
```

Then type `/become-claude-master`. It sets up your environment, interviews you about your work, installs the right skills, and walks you through a 16-topic learning program. You'll go from zero to power user at your own pace.

### Have an idea? Build it properly.

```bash
claude install-skill https://github.com/razbakov/skills/tree/main/skills/product-coach
```

Type `/product-coach` and describe your idea. It won't just start coding — it'll help you discover the right problem first, validate the solution with real users, then dispatch AI agents (product lead, designer, engineer, marketing lead) to build it. This is what separates a weekend hack from a real product.

### Running a team (of humans or AI agents)?

```bash
claude install-skill https://github.com/razbakov/skills/tree/main/skills/org-coach
```

Type `/org-coach`. It designs governance, roles, and coordination — who decides what, what are the boundaries, how do you review. Works for a 2-person startup or a fleet of autonomous AI agents. Built on Sociocracy 3.0, the same framework used by self-organizing teams worldwide.

---

## What makes this different

"Vibe coding" is typing "build me an app" and hoping for the best. **AI-engineering** is giving your AI the same methodologies that professional teams use:

- **Design Sprints** (Google Ventures) — validate before you build
- **BDD** (Behavior-Driven Development) — define what "done" looks like before writing code
- **Story Mapping** — see the whole product, not just the next feature
- **Sociocracy 3.0** — governance that scales from solo to team
- **GTD** (Getting Things Done) — never drop a ball
- **Six Thinking Hats** — analyze decisions from every angle with parallel agents

Each skill encodes a real methodology into a repeatable command. They compose: `/product-coach` generates a backlog, `/estimation` sizes the stories, `/developing-tickets` implements them, `/pr-review-responder` handles the review. One person. Full pipeline.

---

## The full toolkit (90+ skills)

### Product & Strategy

| Skill | What it does |
|-------|-------------|
| `product-coach` | Discover the right problem, validate the solution, dispatch agents to build it |
| `org-coach` | Design governance, roles, and coordination for people or AI agents |
| `project-start` | README, user journey, story map, architecture — before writing code |
| `design-sprint` | 6-phase sprint to validate ideas before building |
| `year-review` | Level 10 Life assessment — score 10 life areas, find patterns, create action plan |

### Development Workflow

| Skill | What it does |
|-------|-------------|
| `user-story` | Requirements to INVEST-compliant stories with acceptance criteria |
| `estimation` | Story point estimation with factor scoring |
| `bdd-from-ux` | BDD scenarios grounded in actual UI/UX implementation |
| `developing-tickets` | Full ticket lifecycle: fetch, plan, implement, verify |
| `sprint-planning` | Select stories, estimate, create GitHub issues, document the sprint |
| `review-backlog` | Parallel quality audit of stories against INVEST principles |
| `pr-review-responder` | Fetch PR comments, fix code, reply, resolve threads |
| `workflow` | Orchestrate multi-step tasks with planning and subagents |

### Daily Operations

| Skill | What it does |
|-------|-------------|
| `daily-review` | Full daily review: browser history, AI transcripts, app usage, project sync, plan |
| `weekly-review` | Saturday review + next week planning with calendar blocks |
| `scrum` | Check status of all dispatched agents across sessions |
| `inbox` | Fire-and-forget agent dispatch with isolation |
| `personal-coach` | Coaching sessions: assessment, check-in, unblock, build jam, journal |

### Content & Marketing

| Skill | What it does |
|-------|-------------|
| `brand-poster` | Generate posters and social media graphics |
| `image-from-gemini` | AI image generation via Google Gemini |
| `image-from-html` | Code-first graphics from HTML/CSS |
| `logo-generator` | Logo concepts with 3x3 variation grids |
| `qr-code-generator` | Styled QR codes with UTM tracking, logos, and gradients |
| `video-podcast-producer` | Split recordings into clips, thumbnails, YouTube metadata, Shorts |
| `latex-pdf` | Professional PDF reports from LaTeX |
| `content-seo-agent` | SEO audit, blog posts, content calendar, analytics reports |
| `storyteller-tactics` | Narrative craft using Pip Decks Storyteller Tactics |
| `viral-threads` | Transform content into viral social media threads |

### Integrations

| Skill | What it does |
|-------|-------------|
| `atlassian` | Jira + Confluence from the terminal |
| `google-drive` | Gmail, Calendar, Drive, Docs, Sheets via CLI |
| `figma-implement-design` | Translate Figma designs into production code |
| `youtube-metadata-updater` | Transcribe videos, generate titles, descriptions, chapters, thumbnails |

### Business & Analysis

| Skill | What it does |
|-------|-------------|
| `sales-bizdev-agent` | Lead pipelines, outreach, deal tracking, CRM, pipeline reports |
| `portfolio-hiring-analysis` | Skill gap analysis, role recommendations, job descriptions |
| `freelance-job-hunt` | Find jobs, verify listings, draft proposals |
| `dependency-vuln-report` | Dependency vulnerability scan with remediation priority |

### Skill Tooling

| Skill | What it does |
|-------|-------------|
| `skill-creator` | Create new skills from scratch or improve existing ones |
| `improve-skill` | Rewrite a SKILL.md using prompt engineering best practices |
| `meta-skill` | Decompose a skill into child skills and orchestrate them |
| `large-skill` | Design complex skills with decision trees and routing maps |

## Install

Pick any skill and install it with one command:

```bash
claude install-skill https://github.com/razbakov/skills/tree/main/skills/product-coach
```

That's it. Replace `product-coach` with any skill name from the list above.

### Skill Packs (via skill-mix)

Curated sets of skills for specific roles — including recommended skills from other repos. Install with [skill-mix](https://github.com/nicepkg/skill-mix):

```bash
npx -y skill-mix https://github.com/razbakov/skills/frontend.json
```

| Pack | Use case |
|------|----------|
| `frontend.json` | Frontend dev with Figma and browser testing |
| `mission-control.json` | Project management with Jira/Confluence |
| `ommax-dev.json` | Full dev workflow with Jira integration |
| `project-management.json` | PM toolkit with Google Workspace |

skill-mix also lets you install the entire collection at once:

```bash
npx -y skill-mix https://github.com/razbakov/skills
```

## Use

Once installed, type the slash command in Claude Code or Cursor:

```
/product-coach     — build the right thing
/org-coach         — organize your team
/daily-review      — start your morning
/estimation        — size your stories
```

Skills also trigger automatically when your prompt matches their description.

## Contributing

Each skill lives in `skills/<name>/` with a `SKILL.md` containing the full prompt. Use `/improve-skill` to refine existing skills or `/meta-skill` to decompose complex ones.

## License

MIT. Use these skills however you want.
