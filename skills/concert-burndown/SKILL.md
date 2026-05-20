---
name: concert-burndown
description: "Track ticket sales for a live event (concert, festival, conference, workshop) with daily snapshots, generate a burndown chart comparing actual sales to ideal-linear targets and tier-cumulative milestones, and report whether the event is on pace. Use when the user asks how sales are going, wants to know if their event will sell out, asks for a daily sales report, wants to set up sales tracking for an upcoming event, or asks about ticket pace / velocity / projection. Trigger generously: phrases like 'how is concert sales going', 'burndown for my event', 'are we going to sell out', 'sales velocity', 'daily ticket chart', 'how many tickets do we need to sell', or any case where the user has a ticketed event with a fixed sales window and wants visibility on pacing."
---

# Concert Burndown — Daily Ticket-Sales Tracking + Chart

A burndown chart, adapted from scrum, applied to ticket sales for a one-off event. Plots actual sales vs ideal-linear and tier-milestone lines. Computes velocity, projection, and the daily pace needed to hit the target. Updates daily.

## Why this skill exists

A ticketed event with a fixed sale window (concert, festival, conference, ball, workshop) has the same structural problem as a sprint: limited time, fixed scope, need to know if you'll land. The same tool that works for scrum — a burndown chart — works for ticket sales.

Without this skill, organizers stare at their ticketing platform's order count, do mental math, and guess. With it: one chart per day, same shape every day, sees drift the moment it starts.

## Trigger

Use when the user:
- Asks how sales are going for their event ("how is concert sales going", "where are we on tickets")
- Has set up a ticketed event and wants visibility on pacing
- Wants to know if a target (sellout, break-even, minimum) is realistic
- Asks for a daily sales report or projection
- Mentions "burndown" / "velocity" / "are we on pace" in any event context

Do NOT use for:
- Mass-market events with no sales window (free RSVPs)
- Subscriptions / recurring revenue (use a different metric)
- Post-event analysis (different problem)

## Inputs needed (gather from user if missing)

1. **Event facts:** name, date, venue, capacity
2. **Sales window:** when did sales open (launch date)
3. **Ticket tiers:** name, price, hide_after date, quantity per tier
4. **Target:** minimum (break-even number) and stretch (sellout number)
5. **Ticket platform:** Ticket Tailor / Eventbrite / Eventix / manual

If platform has an MCP (e.g. Ticket Tailor MCP), pull sales programmatically. Otherwise ask the user to paste current sales manually each day.

## Requirements

- `uv` (the script uses inline PEP 723 deps — installs matplotlib on first run)
- Python 3.11+ (provided by `uv` if missing)
- A ticket platform you can pull from (Ticket Tailor MCP recommended; manual CSV input is the fallback)

## Workflow

### Step 1 — Set up the burndown configuration

Create `burndown-config.json` in your event ops directory (`ops/<event-slug>/` if you follow the ikigai-team layout; otherwise wherever you track event docs):

```json
{
  "event_name": "<full event name>",
  "event_date": "YYYY-MM-DD",
  "launch_date": "YYYY-MM-DD",
  "min_target_paid": 250,
  "stretch_target_paid": 450,
  "tier_milestones": [
    {"date": "YYYY-MM-DD", "cumulative_target": 50, "tier": "<tier name>"},
    {"date": "YYYY-MM-DD", "cumulative_target": 150, "tier": "+ <next tier>"},
    {"date": "YYYY-MM-DD", "cumulative_target": 250, "tier": "+ <next tier>"},
    {"date": "YYYY-MM-DD", "cumulative_target": 450, "tier": "+ <regular> — full venue"}
  ],
  "venue_capacity_paid": 450,
  "financing_gap_eur": 0,
  "csv_path": "sales-log.csv",
  "output_png": "/absolute/path/to/burndown/latest.png"
}
```

`csv_path` is resolved relative to the config file's directory if relative, or used as-is if absolute. `output_png` should be absolute — typically outside the git repo (large binary).

### Step 2 — Initialize the sales log

Create `ops/<event-slug>/sales-log.csv` with header:

```
date,paid_tickets,revenue_eur,<tier1>,<tier2>,...,vip_comps,notes
```

Bootstrap with the launch-day snapshot (`<launch_date>,0,0.00,...,launch`).

### Step 3 — Daily snapshot

Once per day (cron, scheduled task, or manual), pull sales from the platform and append a new CSV row.

**If the platform has an MCP** (e.g. Ticket Tailor):

```
Use mcp__tickettailor__event_by_id_get to fetch current event state.
Extract: total_issued_tickets (excluding VIP comps), revenue, ticket_types[].quantity_issued.
Append a row to sales-log.csv with today's date and the snapshot.
```

**If manual:** ask the user to paste current numbers from their platform dashboard. Be specific: "How many paid tickets sold? Current revenue? Any new notes (price tier change, ad campaign, etc.)?"

Example row:

```
2026-05-04,32,1659.00,24,0,0,5,3,7,first Group-of-5 bundle sold; SEB at 24/50; promoter codes live
```

Include a `notes` field with anything noteworthy (price tier expired, ad campaign started, etc.). This becomes the timeline annotation.

### Step 4 — Generate the chart

Run the included Python script (uv inline, self-contained):

```bash
~/.claude/skills/concert-burndown/scripts/burndown.py /path/to/burndown-config.json
```

This produces:
- `<output_png>` — dark-theme chart with:
  - Dashed cyan line: ideal-linear path to min target
  - Dotted purple line: ideal-linear path to stretch
  - Solid amber line with markers: tier-milestone cumulative path
  - Solid red line with markers: actual sales (annotated with current count)
- Dated copy alongside latest.png
- Text summary printed to stdout (paid, revenue, ideal pace, recent pace, needed pace, projection)

### Step 5 — Report to user

After generation, deliver in chat:
- Headline (date, T-X days, paid count)
- Sold / target ratio
- Recent velocity vs needed velocity
- Tier-milestone reality check (e.g. "you're 7 short of the 50 by Sunday milestone")
- Open the folder via `open <output_dir>` for visual review
- Read the PNG inline using the Read tool so the user sees the chart

### Step 6 — Schedule daily delivery (optional)

If the user wants automation: use `mcp__scheduled-tasks__create_scheduled_task` with cron `0 9 * * *` and a prompt that pulls fresh data, regenerates the chart, posts to Telegram via their org's bot, and updates the CSV.

## Format conventions

**Daily summary line** (for Telegram / digest):

```
<Event> burndown — YYYY-MM-DD (T-X days)
  Sold: <N> paid · €<R> revenue
  Min target: <N>/<T> (<%>) · Stretch: <N>/<T> (<%>)
  Ideal pace to min: <X>/day · expected today: <Y> · actual/expected: <ratio>x
  Recent pace (<d>d): <X>/day · projected at min: <Y>
  Needed pace from today: <X>/day to hit min target
```

**Chart aesthetic:** dark background (#0e1116), white/cyan typography, amber/red accent lines. Always include the date and T-X days in the title for at-a-glance currency.

## What this skill does NOT do

- Does NOT make sales decisions (pricing changes, code activation) — that's strategy, not tracking
- Does NOT pull data from platforms it doesn't have an MCP for — fall back to manual CSV input
- Does NOT do post-event analytics (channel attribution, refund analysis) — different problem

## Related skills

- `event-flyer-pack` — print-ready flyer pack for a specific event
- `event-poster-bundle` — IG-ready event-list poster + caption
- `press-kit-pack` — full press kit with releases + Drive folder
