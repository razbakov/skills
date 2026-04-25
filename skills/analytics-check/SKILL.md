---
description: "Check PostHog analytics — DAU report across all projects or a single project. Use when the user asks about DAU, traffic, pageviews, analytics, or says 'DAU report'. Covers both portfolio-wide summaries and per-project deep dives."
user_invocable: true
---

# Analytics Check

Query PostHog analytics for DAU (Daily Active Users) across all tracked projects or a single project.

## Trigger

- "DAU report" → portfolio-wide report (all projects)
- "analytics for <project>" → single project
- Part of daily/weekly review when analytics check is needed

## Configuration

PostHog has two instances. API keys are in `~/.zshrc`:

| Instance | Env Var | Host |
|----------|---------|------|
| EU | `POSTHOG_READ_API_KEY` | `eu.i.posthog.com` |
| US | `POSTHOG_READ_US_API_KEY` | `us.i.posthog.com` |

The project registry (PostHog IDs, instances, URLs) lives in the project's CLAUDE.md under "PostHog Analytics". Read it to get the current list — don't hardcode project IDs in this skill.

PostHog MCP (`mcp__posthog__*`) is scoped to a single project (WeDance US). For cross-project queries, always use the curl API.

## Process: Portfolio DAU Report

### 1. Load config

```bash
source ~/.zshrc 2>/dev/null
```

Read the PostHog Analytics table from the project CLAUDE.md to get project names, IDs, and instances. Skip projects with `-` as PostHog ID (no tracking set up).

### 2. Query all projects

Use the PostHog Query API (`/api/projects/<id>/query/`) with a TrendsQuery. The legacy `/insights/trend/` endpoint is deprecated and returns 403.

```bash
curl -s --max-time 20 "https://${instance}.i.posthog.com/api/projects/${project_id}/query/" \
  -H "Authorization: Bearer ${api_key}" \
  -H "Content-Type: application/json" \
  -d '{"query":{"kind":"TrendsQuery","series":[{"event":"$pageview","math":"dau"}],"dateRange":{"date_from":"-7d"}}}'
```

Response structure: `results[0].labels` (date strings) and `results[0].data` (DAU counts).

EU PostHog can be flaky (503 "no healthy upstream"). If a project fails, retry once after a short pause. If it still fails, mark as UNAVAILABLE and continue — don't block the whole report.

Query projects sequentially (not in parallel) to avoid overwhelming the API. Use `--max-time 20` to avoid hanging on unresponsive endpoints.

### 3. Present as summary table

Format all projects in a single table sorted by 7-day average DAU (highest first):

| Project | Apr 2 | Apr 3 | ... | Apr 9 | 7d Avg |
|---------|-------|-------|-----|-------|--------|
| WeDance v3 | 20 | 21 | ... | 39 | **23** |

### 4. Signals

After the table, surface signals — not just observations, but routable findings. The point of this step is that a list of numbers is barely useful; what's useful is a short interpretation that someone could act on tomorrow.

- **Top performer**: which project carries the portfolio (% of total DAU). If one project dominates >50%, that's worth naming — it means a "portfolio" framing isn't yet visible in traffic.
- **Anomaly spikes**: any single day >2× a project's 7-day baseline. Name the day, name the magnitude, and ask what was published/shared. If the cause is obvious (weekend, launch day, known event), say so.
- **Tracking gaps**: any project with 0 events for 7 days running, OR fewer active days than expected for a project that's claimed to be live. These are likely SDK/wiring problems, not user behavior. Flag them clearly so they don't get read as "no traffic".
- **OKR/target gap**: if the project has a stated traffic or DAU target (check the project's CLAUDE.md, OKRs, README, or the user's stated goals), compute the gap. "X DAU vs target Y = Zx short." Skip this bullet if there's no stated target.
- **Unavailable projects** (API failures): list separately so they're not confused with zero-traffic.

### 5. Action items (only if invoked from a review or with "save")

End the report with a small action list — one bullet per non-trivial signal, with a clear owner. Owners come from the project/org context (read the project's CLAUDE.md for the agent team or roles); don't hardcode names. Typical mappings:

- Tracking gaps → engineering / CTO role
- Content or traffic spikes worth replicating → content / growth role
- Event-driven spikes → community / events role
- Target-vs-reality gaps → strategy / business role

If the project has no agent team defined, leave the owner as "TBD" or address it to the user.

### 6. Save snapshot (optional)

If the user said "save", or this skill was invoked from a daily/weekly review, persist the full report so other agents can reference it later. Read the project's CLAUDE.md to find the conventional sessions/snapshots directory (commonly `ops/sessions/` or `sessions/`). Filename:

```
<sessions-dir>/YYYY-MM-DD-portfolio-dau-snapshot.md
```

Use today's date. Include the per-day matrix, per-project averages, signals, and action items.

## Process: Single Project

When the user asks about a specific project:

1. Look up the project in the CLAUDE.md PostHog table
2. Query just that project using the same curl approach
3. Present the 7-day DAU table
4. Calculate 7-day average (exclude partial today if it's early in the day)
5. Note trend direction (up/down/stable)
6. If PostHog MCP is available for that project, also check test account filters and link to the insight

## Troubleshooting

- **503 / "no healthy upstream"**: PostHog instance is having issues. Retry once, then mark unavailable.
- **"Legacy insight endpoints are not available"**: You're using the old `/insights/trend/` endpoint. Switch to `/query/` with `TrendsQuery`.
- **Empty JSON response**: The curl request timed out silently. Increase `--max-time`.
- **All zeros for a project**: Either no traffic, tracking not installed, or the PostHog project ID is wrong. Suggest the user verify the tracking snippet is on the live site.
