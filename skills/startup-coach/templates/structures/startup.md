# Workspace Structure: Startup

Full product lifecycle — strategy, design, marketing, and engineering in one workspace.

```
<project>/
├── README.md                           # Mission, vision, status, OKRs
├── CLAUDE.md -> README.md              # AI context symlink
├── AGENTS.md -> README.md              # AI context symlink
├── .bin/
│   └── link-readmes.sh                 # Creates AI symlinks
├── product/                            # Strategy & planning
│   └── <product>/
│       ├── strategy.md                 # Business strategy
│       ├── jtbd.md                     # Jobs to Be Done — user research
│       ├── user-journey.md             # First user experience
│       ├── story-map.md                # Visual journey × priority map
│       ├── backlog.md                  # All stories grouped by epic
│       └── scenarios/                  # BDD feature files (playwright-bdd)
│           └── <slug>.feature
├── design/                             # Brand & visual assets
│   ├── brand.md                        # Colors, fonts, logo rules
│   ├── logos/                          # SVG + PNG variants
│   └── styles/                         # Visual style definitions
│       └── <style-name>.md
├── marketing/                          # Campaigns & content
│   └── <product>/
│       ├── campaign.md                 # Launch playbook
│       ├── content-plan.md             # Weekly content calendar
│       └── posters/                    # Poster briefs
│           └── <poster-name>.md
└── engineering/                        # Application code
    ├── architecture.md                 # System architecture
    ├── decisions/                      # Architecture Decision Records
    │   └── <NNN>-<slug>.md
    └── <app>/                          # App source code
        ├── plan.md                     # Website strategy + design system
        ├── content.md                  # All copy: headlines, body, CTAs
        └── src/                        # Source code
```

## Applicable phases

All phases (0–12).

## When to use

- New startup or product idea
- Side project with branding and marketing needs
- Any product that needs the full lifecycle from strategy to deployment
