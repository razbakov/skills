---
name: year-review
description: "Level 10 Life assessment — score 10 life areas (1-10), compare to previous assessment, identify patterns, pick 3 focus areas, create action plan. Use when the user says /year-review, 'let's do an assessment', 'L10L', 'level 10', or it's been 4+ weeks since the last assessment."
---

# Level 10 Life Assessment

Structured quarterly life assessment using Hal Elrod's Level 10 Life framework. Walk through 10 areas one at a time, score each, identify patterns, pick focus areas, create an action plan.

## Trigger

User says "assessment", "L10L", "level 10", "year review", or invokes `/year-review`.

## Context

- **Working directory:** `~/Projects/ikigai`
- **Previous assessments:** `assessments/` — immutable snapshots
- **Current state:** `now.md` — focus areas, goals, routine
- **Profile:** `profile.md` — personality, values, motivation patterns
- **Projects:** `PROJECTS.md` — project status
- **Sessions:** `sessions/` — recent activity

## Step 1 — Load Context (silent)

Read in parallel:

1. `profile.md`
2. `now.md`
3. All files in `assessments/` — find the latest one, note the date
4. `PROJECTS.md`
5. Recent session files in `sessions/` (last 7 days)

Do NOT announce file reads.

## Step 2 — Present Starting Point

Show:

- Date of last assessment
- Previous scores as a table
- How many days/weeks since last assessment
- 2-3 sentence summary of what's happened since (from sessions, projects, contacts)
- Current morning routine status (from `now.md`)

Ask: "Ready to go through the 10 areas?"

## Step 3 — Walk Through 10 Areas

Go through each area **one at a time, one per message**. Order:

1. Health (physical + mental/emotional)
2. Personal Growth
3. Spirituality (purpose, values, meaning)
4. Finances
5. Career
6. Romance & Relationships
7. Family & Friends
8. Fun & Recreation
9. Contribution/Giving
10. Physical Environment

**For each area:**

1. State the previous score
2. Share what you know that's changed since last time (be specific — reference projects, people, events)
3. Ask: "How would you rate this now? (1-10)" with a specific follow-up question based on what you know
4. If they ask what the area means — explain with examples from their life, not textbook definitions
5. After they score:
   - If score changed significantly (+/-2 or more): name what the change means
   - If unchanged for 2+ assessments: "Is this stable, or stagnant?"
   - If score dropped: acknowledge it without minimizing
   - If score rose: celebrate specifically (not generically)

**Style:** One area per message. Keep momentum. Warm, direct, no lectures. Use their words.

## Step 4 — Summary & Patterns

After all 10 areas scored, present:

### Comparison Table

| # | Area | Previous (DATE) | Current | Change |
|---|------|-----------------|---------|--------|
| 1 | Health | X | Y | +/-Z |
| ... | ... | ... | ... | ... |
| | **Total** | **XX/100** | **YY/100** | **+/-Z** |

### Pattern (1-2 sentences)

Name the story the scores tell. Examples:
- "Foundation rebuilt but meaning collapsed"
- "Everything moved except the thing that matters most"
- "Slow, steady progress — no breakdowns, no breakthroughs"

### Top 3 Focus Areas

Pick the 3 areas with lowest scores or biggest drops. Explain why each matters for Alex specifically (connect to ENFJ wiring, motivation patterns, ikigai hypothesis).

### Action Items (3-5 concrete actions)

Map each action to a LIFE SAVERS practice where relevant:

| Focus Area | Relevant Practice |
|------------|-------------------|
| Health | Exercise, Silence (meditation) |
| Personal Growth | Reading (10 pages/day), Scribing (journaling) |
| Spirituality | Silence, Affirmations, Visualization |
| Career / Finances | Affirmations (goals), Visualization (outcomes) |
| Any low-scoring area | Scribing (journaling for clarity) |

If 2+ focus areas map to LIFE SAVERS, suggest a personalized morning routine. Always offer the 6-minute minimum version alongside the full version.

### Habit Adoption Timeline

- Days 1-10: Resistance ("this feels weird")
- Days 11-20: Discipline ("I don't feel like it but I'll do it")
- Days 21-30: Ritual ("this is just what I do")

### Book Recommendations (optional, 1-3)

Only if relevant to focus areas. Tie each book to a specific focus area.

**Ask: "Does this summary feel accurate? Anything you'd change before I save it?"**

## Step 5 — Save

After user confirms:

1. **Create assessment file:** `assessments/YYYY-MM-DD.md`
   - Include: scores table, notes per area, pattern, focus areas, action items, book recommendations
   - This file is **immutable** — never edited after creation

2. **Update `now.md`:**
   - Replace focus areas with new ones
   - Update active goals based on new action items
   - Update coaching cadence (next assessment date: ~4-6 weeks out)
   - Update morning routine if changed

3. **Update `profile.md`:**
   - Add anything new learned about values, patterns, or themes
   - Update "Current Situation" section if life circumstances changed

4. **Add assessment to Google Calendar:**
   ```bash
   gog cal create <GOOGLE_ACCOUNT> \
     --summary "Next L10L Assessment" \
     --from "YYYY-MM-DDT10:00:00+01:00" \
     --to "YYYY-MM-DDT11:00:00+01:00" \
     --description="Level 10 Life quarterly assessment" \
     --force
   ```
   Schedule ~5 weeks from today.

## Rules

- **One area per message.** Don't dump all 10 at once.
- **His score, his decision.** You can offer your read, but he decides the number.
- **No inflation.** Don't sugarcoat low scores. Warmth and honesty aren't opposites.
- **Assessments are immutable.** Once saved, never edit. They're historical records.
- **Connect to purpose.** When discussing Spirituality, Contribution, or Career — loop back to the ikigai hypothesis.
- **Challenge stagnation.** Unchanged scores across 2+ assessments deserve a question.
- **Don't announce file operations.** Save silently after confirmation.
- **Respect autonomy.** Suggest, don't prescribe.
- **Use his language.** If he calls something "the limbo thing" or "the consumption loop" — use those words, not clinical terms.
