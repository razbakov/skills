---
name: form-signup-recovery
description: >
  Recover lost registrations after a signup/lead form has been silently broken — diagnose via the Resend email log,
  classify real users vs tests, re-submit missing contacts to HubSpot via the public Forms API (no auth token needed),
  and produce a personal follow-up list. Use when the user says "backfill dropped signups", "the registration form was
  broken", "we lost signups", "check what registrations came through", "recover lost leads", or any variation where a
  form-to-CRM pipeline has been failing and needs reconciliation. Also use proactively after fixing any registration
  form bug to check whether real users were lost before the fix.
user_invocable: true
---

# Form Signup Recovery

When a registration form silently breaks, the CRM is the wrong place to look first — if the bug is in the CRM submission path itself, the CRM will be empty precisely because the form was broken. The highest-fidelity audit log is almost always the **admin notification email** sent by the server handler after a successful submission. Resend is the most common outbound provider for these — its `/emails` API returns the full list with HTML bodies, which contain the structured name/email/phone/referrer fields.

This skill reconstructs the real signup list from Resend, separates real users from tests, re-submits them to HubSpot via the public Forms API (which requires only portalId + formGuid — no auth token), and produces a follow-up action list.

## Trigger

- "backfill dropped signups"
- "the form was broken, what did we lose"
- "recover lost leads / signups / registrations"
- "check if real users registered while X was broken"
- Proactively after fixing any registration form bug, before declaring the fix complete

## Prerequisites

1. **Resend API key** — usually in the project `.env` as `RESEND_API_KEY` or `NUXT_RESEND_API_KEY`. Read the file to find it.
2. **Server handler** that sends an admin notification email with structured fields (name/email/phone/source/referrer). If the handler doesn't send admin emails, this skill can't recover — fall back to server logs / function invocation logs instead.
3. **HubSpot portal ID + form GUID** — in project `.env`, usually `NUXT_HUBSPOT_PORTAL_ID` and `NUXT_HUBSPOT_FORM_GUID`. These are public values (the frontend ships them to the browser), so no auth is needed to re-submit.

Do NOT rely on a HubSpot access token for this flow. Access tokens expire silently; the Forms API submission endpoint is unauthenticated by design.

## Process

### Step 1 — Locate credentials

Read the project's `.env` file to find Resend key, HubSpot portal ID, and form GUID. If values are named differently, grep for `RESEND` / `HUBSPOT` to find them. Never paste secrets into the response — use them only in curl commands.

### Step 2 — Pull the Resend email log

List all outbound emails (this endpoint returns up to 100 per page, usually enough for recent recovery):

```bash
curl -s "https://api.resend.com/emails?limit=100" \
  -H "Authorization: Bearer $RESEND_API_KEY"
```

Filter for admin notifications — they typically have subjects like `New signup:`, `New lead:`, `New submission:`. Extract the IDs.

### Step 3 — Fetch each email body

The list endpoint only returns metadata. To get the HTML body (which contains the structured fields), fetch each email by ID:

```bash
for id in $IDS; do
  curl -s "https://api.resend.com/emails/$id" \
    -H "Authorization: Bearer $RESEND_API_KEY"
  printf '\n'
done > /tmp/signups-raw.jsonl
```

### Step 4 — Parse structured fields

The admin email HTML usually contains a table like:

```html
<tr><td>Name</td><td>John Doe</td></tr>
<tr><td>Email</td><td><a href="mailto:...">john@example.com</a></td></tr>
<tr><td>Phone</td><td><a href="tel:...">+491234567890</a></td></tr>
<tr><td>Referrer</td><td>https://...</td></tr>
```

Parse with a short Python script. A robust regex that handles both plain text and `<a>`-wrapped values:

```python
def grab(label, html):
    m = re.search(r'>'+label+r'</td><td[^>]*>(?:<a[^>]*>)?([^<]+?)(?:</a>|</td>)', html)
    return m.group(1).strip() if m else ''
```

Extract: date (from `created_at`), name, email, phone, source, medium, campaign, referrer.

### Step 5 — Classify real vs test

Test signups typically have one or more of:

- Email on a domain the user owns (check for `@razbakov.com`, `@<project>.com`, etc. — read the project CLAUDE.md if unsure which domains are "internal")
- Email matches the user's own address or known team members
- Name is obviously placeholder: "Test User", "Alex Test", "Max Musterman" (German John Doe), "John Doe", "Foo Bar"
- Phone is an obvious test value (`+4900000000`, all same digits)

Present BOTH lists to the user before proceeding: "I found N real signups and M tests. Here they are — confirm before I submit to the CRM?" The user may recognize someone you flagged as a test, or vice versa.

### Step 6 — Re-submit to HubSpot Forms API

Use the **public** Forms API endpoint — same path the frontend uses:

```bash
PORTAL=<portal_id>
FORM=<form_guid>
URL="https://api.hsforms.com/submissions/v3/integration/submit/$PORTAL/$FORM"

curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d '{"fields":[
    {"name":"email","value":"..."},
    {"name":"firstname","value":"..."},
    {"name":"phone","value":"..."}
  ]}'
```

Success response: `{"inlineMessage":""}` (empty string). HubSpot dedupes by email, so re-submitting an existing contact is safe (it updates, doesn't duplicate).

**Field names are handler-specific.** The `email`/`firstname`/`phone` above are what *most* handlers pass, but the form schema in HubSpot determines which field names are valid. If re-submission fails with a validation error, read the original server handler source to see what field names it uses, or check the HubSpot form definition directly.

**Do NOT** re-submit through the project's own `/api/subscribe` handler (or equivalent) — that would trigger N admin-notification emails to the user's inbox and N welcome emails to the recovered contacts, which is usually bad UX (a delayed automatic welcome email looks worse than no email).

### Step 7 — Produce a personal follow-up list

The recovered contacts need a **personal message**, not an automated welcome — especially if real time has passed. Draft a template that:

- Acknowledges the silence explicitly ("sorry about the delay, our welcome email was broken")
- Repeats the key event/offer details
- Asks for a short yes/no reply (easier to respond to than a generic CTA)

Save the list + template to a backlog item or session note in the project, so the user can work through them 1-by-1. Flag high-signal referrers (organic hits from specific sites, social traffic sources) for follow-up questions — these people are channel research gold.

### Step 8 — Write up findings

Create a session note in the project's ops/sessions directory (`YYYY-MM-DD-signup-backfill.md`) with:

- What you did and which sources you checked
- Total signups found, broken down by real vs test
- Table of real signups with date, name, email, phone, referrer
- Which were successfully re-submitted to HubSpot
- Signals from referrers worth investigating
- Open follow-ups (HubSpot token rotation, welcome email investigation, etc.)

Link from the related engineering ticket (the "fix registration form" task) so the backfill is discoverable from the bug that caused it.

## Gotchas

- **Resend list endpoint is capped at 100 results per call.** If the broken period is long enough that more than 100 outbound emails happened (welcome emails + admin notifications + any other traffic from the same API key), recent signups will push older ones off the page. If you need older data, check the Resend dashboard directly or use their pagination cursors — but for typical recovery windows (days to weeks), 100 is usually enough.
- **HubSpot access tokens expire silently.** If someone asks you to "check HubSpot contacts", don't assume the token in `.env` works — test it first with a `GET /crm/v3/objects/contacts?limit=1`. If expired, fall back to Resend + re-submission rather than rotating the token mid-task.
- **The admin-email-fired-therefore-HubSpot-succeeded assumption** depends on the handler's error handling. In a typical Nitro/Express handler: `await hubspotCall(); await resendCall();` — if HubSpot throws, Resend never fires, so admin emails are a reliable proxy for HubSpot success. But if the code has try/catch around the HubSpot call, Resend could fire even when HubSpot failed. **Read the handler source** before assuming.
- **Welcome emails may have been silently failing** for real signups even when admin notifications worked. The admin-email path is user → Resend → user (same domain), while welcome is user → Resend → customer (external). A Resend domain verification issue can break the second while leaving the first working. Check Resend for bounce/failure events on the welcome-email side.
- **Names split on whitespace for `firstname`** — e.g. "Charles David Heyburn" → `firstname=Charles`. Don't try to parse last names; HubSpot's Forms API doesn't require `lastname` and guessing will be wrong.
- **Phone number formatting** — don't normalize. Submit exactly what the user typed. HubSpot accepts free-form phone strings.
- **Don't silently proceed** — show the classification (real vs test) to the user before submitting. Recovery actions are visible (the user will get notification emails if the handler pings them on re-submission) and partly irreversible (you can't un-add a contact without manual CRM work).

## Output

1. A session note file in the project (`ops/sessions/YYYY-MM-DD-signup-backfill.md`).
2. A backlog item for personal follow-up (in the appropriate domain — usually brand-and-content or sales).
3. Update to the related engineering "fix registration form" ticket with root cause and backfill findings.
4. A short summary to the user: N real signups recovered, M submitted to CRM, highest-signal referrers, recommended next action.
