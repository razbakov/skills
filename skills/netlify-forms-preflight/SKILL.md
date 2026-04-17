---
name: netlify-forms-preflight
description: >
  Verify a Netlify-hosted form is registered and accepting submissions BEFORE distributing any offline asset
  (flyer, QR code, business card, print ad, physical signage) that points at the form. Catches the silent failure
  mode where Netlify only indexes forms seen during a build with form-detection enabled — submissions made before
  the form is registered hit the static 404 and are irrecoverable. Use this skill whenever the user is about to
  print/distribute QR codes, flyers, business cards, or any offline material that drives leads to a Netlify-hosted
  form; whenever a form "works in prod but no submissions are showing up"; whenever the user says "I enabled forms
  but can't see anything"; or proactively after merging any PR that ships a new Netlify-forms-backed lead capture
  page. Also covers verifying email notifications are wired so leads are not silently sitting in a dashboard nobody
  checks.
user_invocable: true
---

# Netlify Forms Pre-flight

Netlify Forms has a subtle failure mode that burns lead-gen launches: **forms only catch submissions after Netlify's build-time HTML scanner has seen them in a deploy with form detection enabled.** Before that moment, the form's POST target does not exist server-side — visitors' browsers send the POST, Netlify returns the static 404 page, and the submission vanishes. There is no buffer, no queue, no recovery path.

This matters most when offline assets are already in circulation. Once QR codes are printed and flyers are handed out, every scan is a one-shot chance to capture a lead. If the form isn't registered the moment the first flyer hits the street, those leads are gone.

The fix is a five-minute pre-flight check. Do it BEFORE printing. If it's too late — flyers are out — do it now and at least bound the loss to what's already been missed.

## Trigger

Invoke this skill when:

- The user says they are about to print QR codes, flyers, business cards, posters, print ads, or physical signage that drives to a form
- The user has just handed out or distributed offline assets pointing at a Netlify site and wants to check they work
- The user says a form "works in prod but submissions aren't showing up" / "I enabled forms but don't see anything" / "submitted a test and got nothing"
- A PR just merged that ships a new lead-capture page backed by Netlify Forms
- The user is debugging why Netlify Forms is returning 404 on POST
- Any mention of `data-netlify="true"`, `form-name`, or Netlify form detection in a troubleshooting context

## Prerequisites

1. **Netlify CLI authenticated.** Check with `netlify status`. If not logged in, user runs `netlify login`.
2. **Target site identifiable.** Either the Netlify site name (e.g. `my-site`) or the public URL is enough — the skill looks up the site_id.
3. **Form path and name known.** The page URL that contains the form (e.g. `/contact`), and the value of the form's `name` attribute / `form-name` hidden input.

## Process

### Step 1 — Resolve site_id

Netlify's API indexes everything by site_id (a UUID), not by site name. List the user's sites and filter:

```bash
netlify api listSites 2>&1 | python3 -c "
import sys, json
d = json.load(sys.stdin)
q = '<name-or-url-substring>'  # e.g. 'razbakov' or 'mysite.com'
for s in d:
    if q.lower() in (s.get('name','') + s.get('url','')).lower():
        print(s.get('name'), '|', s.get('id'), '|', s.get('url'))
"
```

Capture the UUID into a shell var for reuse: `SITE_ID=<uuid>`.

### Step 2 — Verify the form HTML is actually being served

Fetch the page and confirm the form markup is present in the prerendered HTML. Netlify's scanner only sees what's in the static HTML at build time — forms that only exist after client-side Vue/React hydration will not be detected.

```bash
curl -s "https://<site-domain>/<form-page>" -o /tmp/page.html
# Confirm form markup is server-rendered (not Vue/React-only):
grep -oE '<form[^>]*name="[^"]+"[^>]*>' /tmp/page.html
grep -oE 'data-netlify="[^"]*"|netlify-honeypot|name="form-name"' /tmp/page.html | sort -u
grep -oE '<input[^>]*name="[^"]+"' /tmp/page.html | sort -u
```

What to check:
- A `<form>` element with a `name=` attribute matching what the skill expects
- Either `data-netlify="true"` OR the `netlify` boolean attribute (both work)
- A hidden `<input name="form-name" value="<form-name>">` — Netlify requires this on submission so it knows which form the POST belongs to

If any of the above is missing, the form will never be detected. Fix the markup and redeploy before continuing.

### Step 3 — Check that the form is registered on Netlify

This is the step that catches the most common failure.

```bash
netlify api listSiteForms --data="{\"site_id\":\"$SITE_ID\"}" 2>&1 | python3 -c "
import sys, json
forms = json.load(sys.stdin)
if not forms:
    print('NO FORMS REGISTERED — submissions will 404')
for f in forms:
    print(f\"{f['name']:<30} submissions={f['submission_count']:<4} last={f.get('last_submission_at')} created={f['created_at']}\")
"
```

Decision tree:
- **No forms listed at all** → Forms detection is off on the site, OR the most recent deploy didn't run with detection on. Go to Step 4.
- **The expected form is missing** → Same as above, OR the form markup was not in the prerendered HTML at the time of that deploy. Verify Step 2, then trigger a new deploy.
- **Form is listed, `created_at` is recent** → Registration is fresh. Any submissions that happened before `created_at` were lost. Note this timestamp — the skill will need to report it to the user so they can estimate the loss.
- **Form is listed, `created_at` is old** → Form is live and has been for a while. Continue to Step 5.

### Step 4 — Enable Forms detection and redeploy

If the form is not registered:

1. Tell the user to enable Forms in the site settings: `https://app.netlify.com/sites/<site-name>/settings/forms` → toggle "Form detection" on.
2. Trigger a new deploy (pushing an empty commit is the quickest way):
   ```bash
   cd <project-dir>
   git commit --allow-empty -m "chore: trigger rebuild for Netlify form detection"
   git push
   ```
3. Wait for the deploy to complete, then re-run Step 3. The form should appear.

Alternative without a git push: the user can click "Trigger deploy → Deploy site" in the Netlify dashboard.

### Step 5 — Verify the POST path actually works end-to-end

The form is registered — but there's one more thing that can go wrong: the POST URL. Netlify forms POST to `/` by default (or to the form's `action` URL). If the site is behind redirects, edge functions, or a custom router that swallows root POSTs, submissions still die.

Test with a real POST using an obviously-test payload:

```bash
TS=$(date +%s)
curl -sS -o /tmp/resp.html -w "HTTP %{http_code}\n" \
  -X POST "https://<site-domain>/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "form-name=<form-name>&<field1>=preflight-probe-$TS&<field2>=...&bot-field="
```

What to expect:
- `HTTP 200` → submission accepted. Go to Step 6 and verify it arrived.
- `HTTP 303` or `302` → also normal; Netlify often redirects to a success page.
- `HTTP 404` → form is NOT handled at this URL. Either the `action` attribute points somewhere else, or a redirect rule is eating the POST. Fix and retry.
- `HTTP 400` → Netlify's spam filter blocked it. Look less suspicious (don't put "debug" / "test" in the payload), or proceed — real submissions with normal content will pass.

Include a `bot-field=` empty value in the POST if the form has `data-netlify-honeypot="bot-field"` — the honeypot expects that field to exist but be empty.

### Step 6 — Confirm the submission landed

```bash
netlify api listSiteSubmissions --data="{\"site_id\":\"$SITE_ID\"}" 2>&1 | python3 -c "
import sys, json
subs = json.load(sys.stdin)
print(f'total: {len(subs)}')
for s in subs[:5]:
    print(s.get('created_at'), '|', s.get('form_name'), '|', json.dumps(s.get('data', {}), ensure_ascii=False)[:200])
"
```

The probe submission should appear at the top with a timestamp matching the POST from Step 5. If it does, the form is fully wired: server accepts POSTs, registers them against the right form, stores the data.

If the submission is NOT there despite a 200 from Step 5, something is eating it between Netlify's edge and the form processor. This is rare — most likely a site redirect rule or an overly aggressive spam filter. Check the Netlify deploy logs for a "form submission" line.

### Step 7 — Configure email notifications

Form submissions default to dashboard-only visibility. If the user doesn't check the Netlify dashboard every day, leads rot there. Before declaring the form ready:

1. Navigate to `https://app.netlify.com/sites/<site-name>/forms`.
2. Click the form → "Settings & usage" → "Form notifications".
3. Add an email notification targeting the user's primary email (ask them — don't assume).
4. Optionally, add a Slack or webhook notification if the user's ops surface is elsewhere.

This step is not API-automatable via the public `netlify` CLI — it's a dashboard-only action. Hand it to the user with the exact URL.

### Step 8 — Report

Produce a concise status report:

```
Netlify Forms pre-flight — <site-name>

Form: <form-name> (id <form-id>)
Registered: <created_at>  → submissions before this timestamp were lost
Submission count: <n>
Probe POST (Step 5): HTTP <code>, arrived in dashboard: yes/no
Email notifications: configured / NOT YET — user action required
Dashboard: https://app.netlify.com/sites/<site-name>/forms

Ready to distribute: YES / NO
Blockers: <list>
```

If distribution has already happened and registration is recent, explicitly state the loss window:

> Flyers distributed before <created_at> scanned into a 404. Submissions from that window are not recoverable.

## Anti-patterns

- **Do not assume a form works just because the page renders.** The form markup being visible in the browser does not mean Netlify has registered it.
- **Do not skip the real POST test.** Checking the dashboard after registering a form still leaves the POST path untested. Sites with custom redirect rules can silently drop POSTs while the form registration looks healthy.
- **Do not use the word "test" or "debug" in probe payloads.** Netlify's spam filter is aggressive; obvious test submissions return 400 and muddy the diagnosis.
- **Do not distribute before Step 7.** A form with no notifications is a form that captures leads nobody acts on — functionally equivalent to a lost lead if response time matters.

## When this skill does NOT apply

- Form is backed by something other than Netlify Forms (Formspree, serverless function, third-party — use the provider's equivalent pre-flight).
- Static site hosted on Vercel/Cloudflare Pages with a Netlify subdomain mirror. If the canonical domain resolves to not-Netlify, form POSTs go nowhere regardless of Netlify configuration. Verify hosting with `curl -sI <url> | grep -iE 'server|cache-status'` — Netlify Edge hits show up in `cache-status`.
- Form is a single-page-app component with client-side submission (fetch to an API route). Netlify Forms doesn't apply — this is a regular API endpoint and needs its own health check.

## Redundancy recommendation

For any lead-gen form that drives from offline assets (where failure is especially costly), instrument a second source of truth alongside Netlify Forms:

- **Analytics event** — fire a `posthog.capture('form_submit', {...})` (or GA equivalent) on client-side form submit, before the POST. If Netlify silently breaks, analytics still shows the intent.
- **Email copy** — configure a separate email notification provider (Resend, Postmark) via a server handler so the lead arrives via email independent of the Netlify pipeline.

This is not part of the pre-flight check itself — it's a hardening recommendation to make the next failure recoverable (see the `form-signup-recovery` skill for how to back-fill from a Resend email log).
