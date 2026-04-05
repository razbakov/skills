# Trip Planner

Plan and book a trip end-to-end: research event schedule, find transport + accommodation, book everything, update calendar, resolve conflicts.

## Trigger

- User mentions an upcoming trip, festival, conference, or travel
- User says `/trip-planner`
- User says "plan my trip to X", "book travel for X"

## Inputs

- Event name or destination
- Travel dates (or derive from event schedule)
- Home city (default: Munich)

## Process

### 1. Gather event details

- Search Gmail for event-related emails (confirmations, info emails, schedules)
- Read full email body with `gog gmail thread get <id> --full`
- Extract: dates, venues, schedule, ticket info, important notes (cash only, dress code, etc.)
- Download PDF attachments if schedule is attached

### 2. Check calendar constraints

- `gog cal list primary --from <start> --to <end>` — find conflicts
- Check recurring events (work, classes, socials) that overlap with trip dates
- Ask user about conflicts: skip, reschedule, or work remotely?
- Check work schedule (OMMAX) — can they work remotely from destination?

### 3. Decide travel plan

Present the key decisions:
- When to arrive (before first event)
- When to return (after last event vs. earlier for conflicts)
- What to skip if conflicts exist
- Remote work option if it extends the trip

### 4. Research transport

Spawn a subagent to research ALL options in parallel:
- Train (ÖBB/DB/Westbahn) — door-to-door time, price range, booking links
- Bus (FlixBus) — time, price
- Flight — door-to-door time including airport transfers
- Car — distance, fuel, tolls, parking at destination
- Rideshare (BlaBlaCar) — availability, price

**Output:** Comparison table with door-to-door time, round trip price, flexibility, comfort rating.

### 5. Research accommodation

Spawn a subagent to research options:
- Event partner hotel (check event email for recommendations)
- Hotels near main venue (walking distance)
- Airbnb near venue (good for remote work — kitchen + desk)
- Budget options (hostels with private rooms)

**Prioritize:** proximity to venue > price > wifi quality (if remote work needed) > breakfast included.

**Output:** Top 3 recommendations with total cost, distance to venue, and why.

### 6. Book

Open booking pages in browser for user to complete payment:
- Transport: navigate to checkout page with pre-filled route/dates
- Hotel: navigate to booking page with pre-filled dates

User must enter payment details themselves (prohibited action).

After booking, **immediately** verify actual booked times:

1. Check Gmail for confirmation emails: `gog gmail search "after:YYYY/MM/DD (ÖBB OR FlixBus OR Booking.com OR hotel name)" --max 5`
2. If email doesn't contain departure/arrival times (common with ÖBB Standard-Tickets), check Chrome browser history: `sqlite3 /tmp/chrome_hist.db "SELECT url, title FROM urls WHERE url LIKE '%oebbtickets%' OR url LIKE '%booking%' ORDER BY last_visit_time DESC LIMIT 20"` — basket URLs contain timestamps (e.g., `/ticket/person/2026-03-26T09:28:00.000Z`)
3. Extract: booking references, confirmation numbers, **exact departure/arrival times**, check-in/check-out times, cancellation policy, total costs

**Critical:** Never leave placeholder times in the calendar. The calendar event MUST be updated with actual booked times before the booking step is considered complete.

### 7. Update calendar

Use `gog cal` commands (always use `primary` as calendarId):

```bash
# Create events
gog cal create primary --summary "..." --from "YYYY-MM-DDTHH:MM:SS+TZ" --to "..." --location="..." --description="..." --force

# Update existing events
gog cal update primary <eventId> --summary "..." --force

# Cancel single occurrence of recurring event (use full ID with _YYYYMMDDTHHMMSSZ suffix)
gog cal delete primary "<recurringEventId_YYYYMMDDTHHMMSSZ>" --force
```

Calendar must include:
- Travel events (outbound + return) with ticket numbers in description
- Accommodation (all-day event with check-in/check-out times, confirmation number)
- Event schedule (workshops, parties, concerts — from event email)
- Meals for each day (use `/meal-suggestion` for home days, note venue food options for travel days)
- Remote work blocks if working from destination
- Cancel/skip conflicting recurring events for trip dates

### 8. Save trip summary

Save to `sessions/YYYY-MM-DD-trip-<destination>.md` with:
- Booking confirmations (references, ticket numbers)
- Full schedule
- Venue addresses and transport info
- Important notes (cash, dress code, weather)
- Total trip cost breakdown

## Anti-patterns

- Never assume train times — check ÖBB/DB for actual schedule
- Never fabricate event details — always read from email or event website
- Never enter payment details — navigate to checkout, user completes
- Never delete recurring events entirely — only cancel the specific occurrence
- Never skip checking calendar conflicts — MontunoClub, work, etc.
- Don't assume "work on Monday" means office — check what's actually on the calendar
- Always use `primary` as first arg for `gog cal` commands
- Always use `--force` flag to skip confirmations

## Lessons

- `gog cal create primary` — `primary` is required as first arg (not optional)
- `gog cal update primary <eventId>` — same pattern
- Recurring event occurrences have IDs like `<baseId>_YYYYMMDDTHHMMSSZ`
- Email body often truncated — use `gog gmail thread get <id> --full` for complete text
- `gog gmail search "<query>" --max N` for finding emails (no `--from`/`--to` date flags)
- PDF attachments in emails often contain the detailed schedule — download if needed
- DST changes affect event times (e.g., Meneate Saturday party ends 3am = 4am with DST)
- Festival emails contain gold: venue addresses, transport tips, food options, cash requirements
- When travel dates span DST change, double-check all times after the switch
- ÖBB Standard-Ticket confirmation emails don't include departure times — only "valid: date range". Check Chrome history basket URLs which encode the departure timestamp in the URL path (e.g., `/ticket/person/2026-03-26T09:28:00.000Z`). Never assume the pre-booking placeholder time is still correct.
- After user completes payment, the booking step is NOT done until calendar events are verified against actual booked times. A placeholder calendar event with estimated times is a bug.
