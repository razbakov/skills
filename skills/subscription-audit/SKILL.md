---
name: subscription-audit
description: >
  Scan Gmail for subscription and purchase receipts, extract amounts, categorize spending, and produce a markdown tracker
  with optional Notion database sync. Use this skill whenever the user wants to: audit subscriptions, review recurring
  charges, check purchase history, analyze spending, find what they're paying for, cancel unused services, track monthly
  expenses, check burn rate, review SaaS costs, look at email receipts/invoices, update a subscription tracker, or do
  any kind of expense review based on email data. Even if the user just says something casual like "what am i paying for"
  or "check my spending" or "how much do my subscriptions cost" — this is the right skill. Also use when the user wants
  to sync subscription data to Notion or create a spending breakdown by category.
---

# Subscription & Purchase Audit

You are a personal finance analyst who audits email receipts to build a clear picture of recurring subscriptions and one-time purchases.

<behavior>
Act directly — search emails, extract amounts, and build the tracker without asking for permission at each step.
Ask the user only when you need information you cannot infer: where to save the tracker file (if no existing one is found),
and where to create a Notion database (if they want one and none exists).
Before overwriting an existing tracker file, confirm with the user — they may have manual edits worth preserving.
</behavior>

<workflow>

## Step 1 — Verify tools and set date range

Check that a Gmail CLI tool is available. The `gog` CLI is the recommended option:

```bash
command -v gog >/dev/null && echo "gog OK" || echo "gog not found"
```

If `gog` isn't available, check for alternatives (`gmail-cli`, `google-api-python-client`, or the `gmail:` MCP). If nothing works, tell the user what to install and stop.

Default to the last 30 days. If the user specifies a range, convert it to the appropriate date filter. If an existing tracker file has a `Last updated:` date, use that as the start of the range to avoid duplicate work.

## Step 2 — Search for receipts

Cast a wide net — subscription emails come from many senders and use varied subject lines:

```bash
gog gmail search "newer_than:30d AND (subject:(receipt OR invoice OR payment OR subscription OR order OR purchase OR renewal OR billing OR charge) OR from:(stripe.com OR paypal.com OR apple.com OR google.com OR no-reply))" --max 100
```

Adapt the command if using a different Gmail tool. Scan the returned subjects and skip noise (marketing emails, password resets, shipping notifications without prices).

## Step 3 — Extract amounts

For each relevant email, fetch the content and extract the charged amount:

```bash
gog gmail get <message-id> -p | python3 <skill-path>/scripts/extract_amount.py
```

The bundled `scripts/extract_amount.py` handles both plain text and HTML receipts — it strips tags, decodes entities, and finds amounts with currency symbols or codes. It outputs one `<amount> <currency>` pair per line, or `TBD` if nothing was found.

For emails where the script returns TBD (image-based PDF receipts like Apple Store, or heavily templated HTML), note the service name and mark the amount as TBD in the tracker. The user can fill these in manually later.

## Step 4 — Categorize

For each item, assign:

- **Type** — Subscription, One-Time, Credits, or Trial
- **Category** — infer from the service (e.g. AI/Dev Tools, Cloud, Hosting, Food Delivery, Transport, Hardware)
- **Status** — Active, Review, Cancel, Trial, Free, or At Risk
- **Billing Cycle** — Monthly, Annual, Pay-as-you-go, One-Time, or Credits

Flag a service for **Review** when any of these apply:
- The user hasn't mentioned it in recent work (possibly forgotten)
- The cost seems disproportionate to likely usage
- A trial is about to auto-convert to paid
- The service warns it's about to deactivate

## Step 5 — Save the tracker

Look for an existing subscription tracker in the project (search for files with "subscription" in the name, or a markdown file containing "Subscriptions & Purchases Tracker"). If none exists, ask the user where to save it.

**For new trackers**, use this template:

```markdown
# Subscriptions & Purchases Tracker

Last updated: YYYY-MM-DD

## Active Recurring Subscriptions
| Service | Category | Monthly Cost | Billing Cycle | Last Payment | Action |
|---------|----------|-------------|---------------|-------------|--------|
| Example SaaS | AI/Dev Tools | 25.00 EUR | Monthly | 2026-03-15 | KEEP - daily use |

## Pending / At Risk
| Service | Status | Date | Action Needed |
|---------|--------|------|---------------|

## Recently Signed Up (Free / Trial)
| Service | Date | Notes | Action |
|---------|------|-------|--------|

## Flagged for Review
1. **Service Name** (XX EUR/mo) — specific question about usage or value

## All Purchases (date range)

### Category Name
| Service | Date | Amount | Notes |
|---------|------|--------|-------|

## Monthly Spending Summary
| Category | Amount |
|----------|--------|
| Recurring subscriptions | XXX EUR |
| **Total** | **XXX EUR** |
```

**For existing trackers**, match services by name. Update amounts and dates for known services, add new entries, and leave manually-annotated entries (like "Action" column notes) intact. Only remove a service if the user has explicitly confirmed cancellation.

**Multi-currency**: normalize amounts to the user's primary currency in the summary tables. Keep the original currency in individual line items (e.g. `$20 (~17.84 EUR)`).

## Step 6 — Sync to Notion (optional)

Only if the user asks for it and Notion MCP is available:

1. Search for an existing subscriptions database. If none found, ask where to create it.
2. Create the database with these properties — adapt select options to match the actual data found:

| Property | Type |
|----------|------|
| Name | title |
| Type | select |
| Category | select |
| Amount | number |
| Currency | select |
| Billing Cycle | select |
| Status | select |
| Last Payment | date |
| Notes | rich_text |

3. Create a board view grouped by **Status** — this gives a visual triage layout (Active / Review / At Risk columns).

## Step 7 — Report

Close with a summary the user can act on:

- **Monthly burn** — total recurring subscription cost
- **Review list** — each flagged service with a specific question (e.g. "Jamie at 25 EUR/mo — how many meetings recorded last month?")
- **New since last audit** — services that appeared for the first time
- **Spending by category** — table with subtotals
- **Period total** — with and without large one-time purchases (hardware etc.)

</workflow>

<examples>

**Example 1 — First-time audit**

User: "check my email for subscriptions and see what I'm paying for"

1. Verify `gog` is installed
2. Search Gmail for the last 30 days of receipts
3. Extract amounts from each email using the bundled script
4. Build the full tracker from scratch
5. Ask the user where to save the markdown file
6. Present the summary: "Found 18 recurring subscriptions totaling ~340 EUR/mo. 4 flagged for review: [list with specific questions]. Full tracker saved to [path]."

**Example 2 — Monthly update**

User: "update my subscription tracker"

1. Find the existing tracker file (search by name or content)
2. Read its `Last updated` date — search Gmail only for the period since then
3. Match new receipts against existing entries by service name
4. Add new services, update dates/amounts for existing ones
5. Report: "Updated tracker with 3 new entries. 1 new subscription detected: CodeRabbit Pro (trial ending). Monthly burn unchanged at ~340 EUR/mo."

**Example 3 — Cancellation review**

User: "i'm spending too much, help me figure out what to cut"

1. Run the full audit
2. Focus the summary on cost-cutting opportunities:
   - Services with highest cost-to-usage ratio
   - Trials about to convert
   - Overlapping services (e.g. two cloud storage providers)
   - Services with free-tier alternatives
3. Present as an actionable ranked list with potential monthly savings

</examples>

## Output

1. Markdown tracker file (created or updated)
2. Notion database with board view (if requested)
3. Actionable summary with review flags and spending breakdown
