---
name: weekly-review
description: "Saturday weekly review + planning. Reviews the past week (sessions, calendar, projects), updates PROJECTS.md, reflects on focus areas, then plans next week with calendar blocks. Use when the user says /weekly-review, 'weekly review', 'weekly planning', or it's Saturday."
---

# Weekly Review + Planning

Saturday ritual (10:00-11:00). Two parts: **Review** (what happened) then **Planning** (what's next). Runs from the ikigai project directory.

## Trigger

User says "weekly review", "weekly planning", or invokes `/weekly-review`. Also trigger if it's Saturday and user starts a session.

## Context

- **Working directory:** `~/Projects/ikigai`
- **Google account:** From CLAUDE.md Personal Info
- **Calendar tool:** `gog cal`
- **Current state:** `now.md` — focus areas, goals, routine
- **Profile:** `profile.md` — motivation patterns, values
- **Projects:** `PROJECTS.md` — all projects with status
- **Sessions:** `sessions/` — daily browser + AI logs
- **Contacts:** `contacts/` — people and commitments
- **Assessments:** `assessments/` — latest L10L scores

## Part 1 — Review (what happened this week)

### Step 1 — Gather the week's data

Run in parallel:

1. **Calendar:** `gog cal ls --from "YYYY-MM-DD" --to "YYYY-MM-DD"` (Monday through today)
2. **Session files:** Read all `sessions/` files from this week (browser history + AI sessions)
3. **Project READMEs:** For each project in PROJECTS.md with a workspace path, read its README.md to get current status
4. **Analytics:** Run `/analytics-check` — pull DAU from PostHog for projects with analytics (razbakov.com, dancegods). Capture 7-day DAU table, trend, and any filter issues.

### Step 2 — Present the review

Show:

```
## This Week (Mon DATE — Sat DATE)

### What happened
- <bullet summary of each day, drawn from sessions + calendar>

### Projects touched
| Project | What changed | Time spent |
|---------|-------------|------------|
| ... | ... | ~Xh |

### Focus areas progress (from now.md)
| Focus Area | Score | Movement this week |
|------------|-------|--------------------|
| Spirituality | 3 | <what happened related to purpose> |
| Family & Friends | 3 | <social reach-outs, meetings> |
| Fun & Recreation | 3 | <playful activities, creation vs consumption> |

### Analytics (PostHog)
| Project | Avg DAU | Trend | Notable |
|---------|---------|-------|---------|
| razbakov.com | ~22 | stable / up / down | <spikes, dips, filter issues> |

### Commitments check
- <partner promises, deadlines from contacts>

### Morning routine adherence
- <did it happen? how many days?>
```

### Step 3 — Reflect

Ask three questions (one at a time):

1. **What went well this week?** (acknowledge wins)
2. **What was hard?** (don't fix — just hear it)
3. **What's the one insight from this week?** (pattern, realization, or shift)

### Step 4 — Sync PROJECTS.md

Update PROJECTS.md with current status from each project's README:
- Sync status and next actions
- Flag stale deadlines
- Mark completed items
- Only update fields that changed

## Part 2 — Planning (what's next week)

### Step 5 — Next week's calendar

1. Read next week's calendar: `gog cal ls --from "YYYY-MM-DD" --to "YYYY-MM-DD"` (next Mon-Sun)
2. Check contacts for upcoming deadlines or commitments
3. Check PROJECTS.md for deadlines in the next 2 weeks

### Step 6 — Suggest weekly plan

Present:

```
## Next Week (Mon DATE — Sun DATE)

### Existing events
<from calendar>

### Priorities
1. <highest priority — deadline or OKR-aligned>
2. <second priority>
3. <third priority — max 3 projects per week>

### Focus area actions
- Spirituality: <one concrete action>
- Family & Friends: <one concrete action>
- Fun & Recreation: <one concrete action>

### Proposed week

| Day | Focus | Key tasks |
|-----|-------|-----------|
| Mon | Project A | - task 1, task 2 |
| Tue | Project B | - task 1 |
| Wed | ... | ... |
| Thu | ... | ... |
| Fri | ... | ... |
| Sat | Review + Planning | This ritual |
| Sun | Rest + Salsa | Buenavista |
```

**Prioritization rules:**
- Deadlines first (what's due soonest?)
- OKR alignment (does it move a key result?)
- Partner commitments (promises to people)
- Focus area actions (at least one per week)
- Max 3 projects per week — context switching kills momentum
- Sunday is rest + salsa, not work

Ask: "Does this plan work, or do you want to adjust?"

### Step 7 — Save and schedule

Once approved:

1. **Create calendar blocks** for each day's focus using `gog cal create`:
   ```bash
   gog cal create <GOOGLE_ACCOUNT> \
     --summary "<Project/Activity>" \
     --from "YYYY-MM-DDTHH:MM:00+01:00" \
     --to "YYYY-MM-DDTHH:MM:00+01:00" \
     --description="<tasks>" \
     --force
   ```

2. **Update `now.md`** if goals or priorities shifted

3. **Save review** to `reviews/YYYY-MM-DD-weekly-review.md` with:
   - Week summary
   - Reflection answers
   - Next week's plan
   - Any insights or pattern changes

## Rules

- **Review before planning.** Never plan next week without understanding this week.
- **Max 3 projects per week.** Context switching kills momentum.
- **One focus area action per week minimum.** Don't let life OS items starve.
- **Sunday is sacred.** Rest + Buenavista salsa. No work blocks.
- **Be honest about capacity.** Vacation weeks, heavy work weeks — adjust accordingly.
- **Flag stale commitments.** If something was promised 2+ weeks ago and hasn't moved, surface it.
- **Connect to OKRs.** Every priority should trace back to a key result or a partner commitment.
- **Don't over-schedule.** Leave buffer. Real life doesn't follow time blocks perfectly.
