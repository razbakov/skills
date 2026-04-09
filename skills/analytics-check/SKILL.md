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

### 4. Add highlights

After the table, note:
- Which project has most traffic
- Any notable spikes or dips (and possible explanations if dates correlate with weekends, events, launches)
- Projects with zero traffic (may indicate broken tracking or no deployment)
- Any projects that were unavailable

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
