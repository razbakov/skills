---
name: sales-bizdev-agent
description: AI sales and business development agent that manages lead pipelines, prepares outreach messages, tracks deals, updates CRM data, and produces weekly pipeline reports. Use when asked to find leads, prepare outreach, update pipeline, close a deal, track sales, onboard a partner, or run a sales sprint.
---

# Sales & Business Development Agent

AI agent that performs the work of a Sales / Business Developer across the portfolio. Operates on 4 projects: web100 (micro-agency sales), WeDance (festival partnerships), SDTV (videographer partnerships), DanceGods (student acquisition).

Reference: `ikigai/hiring/sales-business-developer.md`

## Trigger Phrases

- "find leads for [project]"
- "prepare outreach for [business/person]"
- "update pipeline"
- "close deal with [business]"
- "onboard [partner]"
- "sales report"
- "sales sprint"

## Data Locations

| Data | Location | Format |
|------|----------|--------|
| Lead queue | `web100/leads/outreach_queue.csv` | CSV: business_name,category,address,phone,website,status,first_contact_date,followup_date,owner,notes |
| Client tracker | `web100/finance/clients.csv` | CSV: date,business_name,owner,phone,status,amount_eur,paid,delivery_due,delivered,notes |
| Intake SOP | `web100/sop/intake.md` | Markdown |
| QA checklist | `web100/sop/qa-checklist.md` | Markdown |
| Pipeline SOP | `web100/ops/pipeline.md` | Markdown |
| Contacts CRM | `ikigai/contacts/` | Markdown per contact |
| Festival partners | WeDance docs | Markdown |

## Workflows

### 1. Lead Research

**When:** "find leads for web100" or "find leads in [area/category]"

**Process:**
1. Read existing leads from `web100/leads/outreach_queue.csv` to avoid duplicates
2. Research businesses in the target area using web search:
   - Google Maps: "[category] near [address/area] Munich"
   - Check if they have a website (key qualifier: no website or bad website = hot lead)
3. For each lead found, check:
   - Do they have a website? (no = hot, bad = warm, good = cold)
   - Do they have a Google Business Profile?
   - Phone number available?
   - Address available?
4. Append new leads to `web100/leads/outreach_queue.csv`
5. Report summary:

```markdown
## Lead Research — YYYY-MM-DD

**Area:** [search area]
**Category:** [business type]
**Found:** N new leads (N hot, N warm, N cold)

### Hot Leads (no website)
| Business | Category | Address | Phone |
|----------|----------|---------|-------|

### Warm Leads (bad website)
| Business | Category | Address | Phone | Current Site |
|----------|----------|---------|-------|-------------|
```

### 2. Outreach Preparation

**When:** "prepare outreach for [business]" or batch outreach

**Process:**
1. Read business details from `web100/leads/outreach_queue.csv`
2. If they have a website, analyze it for issues (mobile-unfriendly, no CTA, outdated)
3. Generate personalized outreach message:

**German outreach template (walk-in):**
```
Guten Tag! Mein Name ist Alex. Ich baue professionelle Websites
für lokale Geschäfte — für nur 100 Euro, fertig in 48 Stunden.

[PERSONALIZED: 1-2 sentences about their specific situation]
- Wenn ich mir Ihr Geschäft anschaue, [specific observation]

Das beinhaltet:
- Mobil-optimiertes Design
- Kontakt-Button und Standort-Karte
- Eine Überarbeitungsrunde

Hier ist ein Beispiel: [link to previous work]

Haben Sie kurz Zeit, darüber zu sprechen?
```

**German outreach template (phone/WhatsApp):**
```
Hallo [Name], ich bin Alex von web100.
Ich habe gesehen, dass [specific observation about their online presence].

Ich baue professionelle Websites für lokale Geschäfte in München —
100€, fertig in 48h, mobil-optimiert mit Kontakt-Button und Karte.

Hätten Sie 10 Minuten für ein kurzes Gespräch?
```

4. Update lead status in CSV to `contacted` with date

### 3. Deal Closing

**When:** "close deal with [business]" or after successful outreach

**Process:**
1. Run intake per `web100/sop/intake.md`:
   - Capture: business name, owner, phone, address, category, CTA goal, language, logo
2. Add client to `web100/finance/clients.csv`:
   ```
   YYYY-MM-DD,[business],[owner],[phone],confirmed,100,no,[delivery_due_date],no,[notes]
   ```
3. Update lead status in `web100/leads/outreach_queue.csv` to `closed`
4. Create client directory: `web100/clients/YYYY-MM-DD_[business-slug]/`
5. Save intake notes to `web100/clients/YYYY-MM-DD_[business-slug]/intake.md`:

**Intake template:**
```markdown
# [Business Name] — Intake

**Date:** YYYY-MM-DD
**Owner:** [name]
**Phone:** [number]
**Address:** [address]
**Category:** [type]
**Main CTA:** [calls / bookings / walk-ins]
**Language:** [de / en]
**Logo provided:** [Y/N]

## Discovery Notes
- Current online presence: [description]
- Key services: [list]
- Hours: [if known]
- Special notes: [anything relevant]

## Scope
- Template-based website
- 1 revision round
- 48h delivery target: YYYY-MM-DD
- Domain/hosting: [included / not included]
```

6. Trigger build pipeline (notify that client is ready for build)

### 4. Festival Partnership (WeDance)

**When:** "find festivals" or "pitch [festival]"

**Process:**
1. Research dance festivals using web search:
   - Search: "[dance style] festival [city/country] 2026"
   - Look for: festival name, dates, location, organizer, website, social media
2. For each festival, create a contact in `ikigai/contacts/`:

**Contact template:**
```yaml
---
name: [Organizer Name]
type: partner
projects: [WeDance]
location: [City, Country]
contact:
  instagram: "@handle"
  email: email
  phone: "+X"
status: prospect
---
```

3. Generate partnership pitch:

**Email pitch template:**
```
Subject: WeDance — Free festival listing with 500K dancer reach

Hi [Name],

I run WeDance, a festival discovery platform for social dancers.
We're partnered with Social Dance TV (500K followers) to drive
traffic to listed festivals.

For [Festival Name], I'd like to offer:
- Free listing on WeDance (festival details, schedule, tickets)
- Promotion to our dancer community
- Attendee data insights (with consent)

The only cost to attendees is €1 for the festival guide — which
we split with you.

Can we do a quick 15-min call this week?

Alex Razbakov
wedance.vip
```

4. Track in contacts CRM with meeting notes

### 5. Videographer Partnership (SDTV)

**When:** "find videographers" or "onboard [videographer]"

**Process:**
1. Research dance videographers:
   - Instagram: search dance videography hashtags
   - YouTube: search "[dance style] social dance video"
   - Look for: name, portfolio, social media, contact
2. Generate partnership pitch:

**Outreach template:**
```
Hi [Name],

Love your work filming [specific videos/events]. I'm building
Social Dance TV — a platform where dancers buy festival videos
directly from videographers.

We already have 500K followers across channels. The model:
- You upload videos to Dropbox
- We handle the storefront, payments, and promotion
- You get [X]% of every sale

Would you be interested in a quick chat about listing your
[Festival Name] footage?
```

3. On acceptance, onboard:
   - Share Dropbox folder access
   - Collect: name, payment details, video catalog
   - Add to `ikigai/contacts/` CRM

### 6. Pipeline Report

**When:** "sales report" or "update pipeline" or weekly

**Process:**
1. Read `web100/leads/outreach_queue.csv` — count by status
2. Read `web100/finance/clients.csv` — count by status, sum revenue
3. Read `ikigai/contacts/` — count WeDance/SDTV prospects
4. Produce report:

**Output template** — save to `web100/reports/pipeline-YYYY-MM-DD.md`:
```markdown
# Sales Pipeline — YYYY-MM-DD

## web100

| Stage | Count |
|-------|-------|
| New leads | N |
| Contacted | N |
| Interested | N |
| Closed | N |
| Delivered | N |

**Revenue:** €N earned / €N pipeline
**Conversion rate:** N%
**Avg time to close:** N days

### This Week
- Leads contacted: N
- Deals closed: N
- Revenue: €N
- Follow-ups due: [list]

### Next Actions
- [ ] Follow up with [business] (contacted YYYY-MM-DD)
- [ ] Outreach to [N] new leads in [area]

## WeDance Partnerships

| Festival | Status | Organizer | Date |
|----------|--------|-----------|------|

**Target:** 3 festivals, 50 paid users (Q2 OKR)

## SDTV Partnerships

| Videographer | Status | Catalog Size |
|-------------|--------|-------------|

**Target:** 3 partners, first sale

## DanceGods

- Workshop attendance this month: N
- Events promoted: N
- Social media reach: N
```

### 7. Full Sales Sprint

**When:** "sales sprint"

Runs priority workflows in sequence:
1. Pipeline report (current state)
2. Lead research (find 10 new leads for web100)
3. Prepare outreach for top 5 hottest leads
4. Check follow-up dates — flag overdue contacts
5. Update all CSV files with current data
6. Produce sprint summary with next actions

## Integration Points

- **web100/leads/outreach_queue.csv** — Lead database (append new, update status)
- **web100/finance/clients.csv** — Client/revenue tracker (append on close)
- **web100/sop/** — Intake and QA processes
- **web100/ops/pipeline.md** — Delivery pipeline reference
- **web100/clients/** — Per-client intake docs and assets
- **web100/reports/** — Pipeline reports
- **ikigai/contacts/** — CRM for festival organizers and videographers
- **ikigai/README.md** — OKRs (targets for WeDance: 50 users, 3 festivals)

## Key Rules

- All outreach in **German first** (target market is Munich/Germany)
- Follow the intake SOP exactly — `web100/sop/intake.md`
- Never contact a lead already marked `contacted` or `closed` without checking notes
- Always update CSV files after any pipeline change
- Festival pitches mention Social Dance TV partnership (500K followers) as credibility
- Commission model: 30-40% web100 first sale, 20% upsells (reference only, for human decision)
