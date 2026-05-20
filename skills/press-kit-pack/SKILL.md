---
name: press-kit-pack
description: "Build a complete press kit for an event, product launch, or campaign — in multiple languages — and publish it as a shareable Google Drive folder ready to send to journalists, partners, or a delegate. Produces press releases (typically DE/EN/ES, or configurable), uploads press photos and flyers, creates an Overview document for at-a-glance briefing, and creates a Handover document with pending tasks, contacts, risks, and decisions so press distribution can be delegated. Use when the user says 'I need a press release', 'create a press kit', 'press release in X languages', 'set up a Drive folder for press', 'handover doc for someone else to run press', or has an upcoming announcement that needs to be sent to media. Trigger generously: even partial requests (just a press release, just a flyer folder) typically evolve into the full kit."
---

# Press Kit Pack

Build a press kit for an event or announcement, publish it as a shared Google Drive folder, and hand it off so anyone can pick up press distribution.

## Why this skill exists

Press distribution is a workflow, not a single asset. A solo organizer who's never done press will spend a weekend reinventing structure (press release format, photo selection, contact list, handover protocol). This skill bakes the structure in, produces all the assets, and leaves a Drive folder you can hand to a journalist, a delegate, or a teammate with one URL.

The "delegate-ready" part is the differentiator. Most press kit guides stop at "send the release." This one closes the loop with an Overview doc (event facts) + a Handover doc (status, pending tasks, contacts, risks, open decisions) so someone other than the organizer can run distribution without ten clarifying questions.

## Trigger

Use when the user:
- Says "I need a press release" (singular or plural)
- Has a public event coming up and wants media coverage
- Asks for a press kit, media kit, or "the press folder"
- Asks for press copy in multiple languages
- Wants to delegate press distribution to a teammate
- Mentions PR / outreach / journalists in any event context

Even if the user only asks for one piece (just a press release; just a Drive folder; just a handover doc), build the full kit — partial press kits get sent half-finished.

## Requirements

- `gog` CLI installed and authenticated for Google Docs + Drive (`brew install gog` or see https://github.com/razbakov/gogcli). Required for steps 2–4.
- If `gog` isn't available, fall back to manual uploads via Drive web UI — explain the steps to the user but you cannot automate them.

## Inputs needed (gather if missing)

1. **Event facts:** name, date (ISO), venue (full address), capacity, format (concert / launch / festival / workshop / etc.)
2. **What's special:** the news angle (first time in years, anniversary tour, major guest, milestone)
3. **Key people:** headliner / instructor / speaker — name, credentials, short bio
4. **Pricing tiers** (if ticketed)
5. **Tickets URL:** the canonical landing URL (prefer organizer's own domain that redirects to the platform, not the platform's URL directly)
6. **Press contact:** name (legal name, not nickname), email (preferably custom domain), phone
7. **Languages:** default DE/EN/ES, or whichever the audience needs
8. **Press photos:** ask the user for paths to hi-res photos (Drive, local, or web). If only headshots of the organizer exist, ask for photos of the headliner.

## Workflow

### Step 1 — Draft press releases in target languages

For each language, write a markdown file at `ops/<event-slug>/press-release-<lang>.md` using this skeleton (translate the section labels to the target language — the example below shows DE labels in parentheses, but English / Spanish / French / etc. follow the same shape with localized terms):

```markdown
# <Press Release | Pressemitteilung | Nota de Prensa> — <Event> in <City>

**<FOR IMMEDIATE RELEASE | FÜR DIE SOFORTIGE FREIGABE | PARA SU INMEDIATA PUBLICACIÓN>**
**<Date | Datum | Fecha>:** <ISO>

---

## <Headline — newsworthy framing, ≤ 12 words, name + venue + date hook>

**<City>, <Date>** — <Lede: who, what, when, where, why-it-matters, in one paragraph. Include the band/person, the tour name if relevant, the venue, the day-of-week or holiday-weekend hook.>

<Optional paired-program paragraph: workshops, opening act, special context.>

> "<Quote from organizer about why this matters for the city/community.>"
>
> — *<Name>, <role>, <city>*

### <About | Über | Sobre> <headliner>
<Background paragraph — founding year, hits, scale, current tour context.>

### <About co-headliner / special guest> (if relevant)
<Background paragraph.>

### <Key facts | Eckdaten | Datos clave> (table)
| | |
|---|---|
| Concert | <Date>, <start time> |
| Doors | <time> |
| <segments> | <time ranges> |
| Venue | <full address> |
| Tickets | <URL> |
| Organizer | <legal name + city> |

### <Press contact | Pressekontakt | Contacto de prensa>
**<Legal name>**
Email: <email>
Mobile: <international phone>
<Press photos, interviews, accreditation on request — translate>

###
```

**Critical formatting rules:**
- Use **legal name** in press releases (matches organizer line on tax/legal docs). Nicknames stay for social media.
- Use **organizer's own domain** for tickets URL (e.g. `montuno.club`), not the ticket platform's URL. Set up a redirect on that domain. Press links to your brand, not your platform.
- Use **custom-domain email** for press contact (e.g. `alex@yourorg.com`), not personal Gmail.
- Schedule entries in 24h format with en-dash for ranges: `19:00–21:00`.
- Each press release must end with `###` (the journalistic end-marker).

### Step 2 — Convert markdown to Google Docs

For each language:

```bash
gog docs create "<Event Name> — <Press Release language> (<LANG>)" \
  --file <path-to-press-release-lang>.md \
  -p
```

Capture each doc's URL and ID — needed for the Overview / Handover refs.

### Step 3 — Create the shared Drive folder

```bash
gog drive mkdir "<Event Name> — Press Kit" -p
```

Capture the folder ID.

### Step 4 — Move docs + upload assets into the folder

```bash
# Move each Google Doc into the folder
gog drive move <doc-id> --parent=<folder-id>

# Upload press photos
gog drive upload <photo-path> --parent=<folder-id>

# Upload flyers
gog drive upload <flyer-path> --parent=<folder-id>
```

Aim for 6–10 files: 3+ press releases, 3–4 hi-res photos of headliner/instructor, 2–3 flyers (IG Story + Feed + variant).

### Step 5 — Write the Overview document

Save as `ops/<event-slug>/overview.md`, then create as Google Doc in the folder:

Sections:
- **Event in one paragraph** — for a journalist needing 10 seconds to understand
- **Headline facts** (table: date, doors, schedule, venue, capacity, pricing tiers, URL)
- **Workshop / programme schedule** (if relevant)
- **Who's involved** — headliner bio, co-headliner bio, venue, organizer, core team
- **Press kit contents** (table mapping each file in folder to its purpose)
- **Press contact**
- **Tickets** (URL + platform note)
- **Use this folder for** — short list of intended audiences

### Step 6 — Write the Handover document

Save as `ops/<event-slug>/handover.md`, then create as Google Doc in the folder:

Scale the section count to the event's complexity. A small launch with no team and no money picture needs sections 1, 2, 5, 6 only. A complex multi-stakeholder event (live touring band, foreign artists, multiple promoters, complex P&L) needs all 11. Use judgment — don't pad.

Sections:
1. **TL;DR** — what / when / where / capacity / status today / financial reality / biggest risks (3–5 bullets)
2. **Project documents** — links to all docs in the kit
3. **Money picture** — real cost vs spreadsheet, revenue scenarios table, conclusion
4. **Critical decisions only the principal can make** — visa, tax, bonus structure, insurance, etc. List with "do not delegate" annotation.
5. **What's done — do not redo** — green-checkmark list of completed work
6. **Open issues — by owner** — table per role with task / why / deadline
7. **Contacts** — core team, external, promoters
8. **Press distribution** — outlet list per language with email contacts, tactical guidance (when to send, subject lines, BCC vs individual)
9. **Open decisions** — items waiting on principal input
10. **Source-of-truth references** — pointers to local research files
11. **How to reach the principal** — channels, what gets routed where

The Handover doc is what makes this kit delegate-ready. Without it, every press question gets escalated back to the principal.

### Step 7 — Report links + flag user-only steps

Final message to user must include:
- Folder URL
- Each press release Google Doc URL
- Overview doc URL
- Handover doc URL
- A "what you still need to do" section listing:
  - **Set folder sharing** (cannot be done by Claude — explicit-permission action)
  - Confirm organizer's email mailbox is live
  - Confirm tickets-URL redirect is set up
  - Replace any `[placeholder]` left in docs (e.g. phone number)

## Format conventions

**Headline structure (DE example):**
*"Kubanische Timba-Legenden Charanga Habanera erstmals seit Jahren in München — 35-Aniversario-Welttour macht Halt am Pfingstwochenende"*

Pattern: `[Headliner archetype] [Headliner name] [news hook] in [city] — [tour/anniversary context] [date hook]`

**Schedule table — fixed shape:** Concert / Doors / Pre-Party / Live segment / After-Party / Venue / Workshops / Tickets / Organizer. Even if some lines are blank, keep the shape — it makes the structure scannable.

**Quote — one quote, from organizer, ≤ 50 words.** Quote anchors the "why now in this city" angle. No promotional adjectives ("incredible", "amazing", "unmissable"). Journalists strip those.

**Hashtags — never in press releases.** Only in social captions. Press releases are for journalists, not algorithms.

## What this skill does NOT do

- Does NOT send the press releases to journalists — that's manual outreach, with personalization
- Does NOT change Google Drive folder permissions — user must set sharing themselves
- Does NOT register the organizer's domain or set up redirects — user does this in their DNS/hosting
- Does NOT design flyers — use `event-flyer-pack` or `image-from-gemini` first, then this skill consumes those flyers

## Related skills

- `image-from-gemini` — generate the hero photos and flyers used in the press kit
- `event-flyer-pack` — produce a complete print + IG flyer pack with QR
- `event-poster-bundle` — IG-ready event-list poster
- `concert-burndown` — track sales velocity once press goes out

## Tactical reminders to include in the user-facing report

When delivering the final folder, always include these reminders in the chat message:

- **Send German release Wednesday morning ~09:00 local.** Most Kultur desks plan weekend coverage Wed–Thu. Friday is too late.
- **Send individually, not BCC.** A 1-line personal intro increases the response rate 5–10×.
- **Have press tickets ready.** Typical ask from a Kultur desk is 2 comp tickets.
- **Don't link bare URLs in pitch emails.** Link to the Drive folder instead — journalists prefer "everything in one place."
