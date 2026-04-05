---
description: Check PostHog analytics for a project — DAU, test account filters, traffic quality. Use when the user asks about analytics, DAU, traffic, pageviews, or PostHog metrics for any project.
user_invocable: true
---

# Analytics Check

Query PostHog analytics for a project and verify data quality (test account filtering).

## Trigger

- User asks about DAU, traffic, pageviews, or analytics for a project
- Part of daily/weekly review when analytics check is needed
- `/analytics-check` or `/analytics-check <project>`

## Context

- **PostHog MCP:** Available via `mcp__posthog__*` tools
- **Projects with PostHog:** razbakov.com (project 44610), dancegods
- **Note:** API key may be scoped to a single project — `projects-get` and `switch-project` may fail

## Process

### 1. Find existing DAU insight

Search for an existing DAU insight to avoid creating duplicates:

```
mcp__posthog__insights-get-all({ search: "DAU", limit: 5 })
```

If found, use the existing insight ID. If not, create one.

### 2. Query DAU data

Run the existing insight query to get fresh data:

```
mcp__posthog__insight-query({ insightId: "<id>" })
```

### 3. Present last 7 days as table

Format the results as a markdown table:

| Date | DAU |
|------|-----|
| Mar 16 | 20 |
| ... | ... |

Include:
- 7-day average (exclude partial today)
- Note any spikes or dips
- Flag if today is partial data

### 4. Verify test account filters

Check the HogQL in the query response to see what filters are actually applied. Look for:
- `localhost` / `127.0.0.1` exclusion
- Email exclusion (e.g., user's email from CLAUDE.md)
- IP exclusion

If `filterTestAccounts: true` is on but the HogQL doesn't show IP/email filters, warn the user.

### 5. Check filter coverage

If filters look incomplete:
1. Get current public IP: `curl -s ifconfig.me`
2. Recommend adding missing filters at: `https://us.posthog.com/settings/project#internal-user-filtering`
3. Suggest filtering by:
   - `$ip` does not equal `<current IP>`
   - `person.properties.email` does not equal `<user email>`

### 6. Re-query if filters changed

If the user updated filters, re-run step 2 and compare before/after. Note: results may be cached — check `last_refresh` timestamp. If cached, note this.

## Output

Present a concise summary:
- DAU table (last 7 days)
- 7-day average
- Trend observation (up/down/stable)
- Test account filter status (what's filtered, what's missing)
- Link to PostHog insight for full view
