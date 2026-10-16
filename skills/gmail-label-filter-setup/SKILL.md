---
description: "Reset and rebuild a Gmail label taxonomy and wire auto-filing filters via the `gog` CLI so the inbox self-maintains. Use whenever the user wants to clean up, reorganize, or restructure their Gmail labels, start their labels fresh, stop recurring email noise from flooding the inbox, auto-file mail by sender, or set up Gmail filters — even if they only say 'my labels are a mess' or 'my inbox keeps filling up with junk'."
user_invocable: true
---

# Gmail Label & Filter Setup

Rebuild a messy Gmail label system into a small, intentional taxonomy and wire filters that
auto-label the mail that matters and auto-archive the noise — so the inbox stays clean on its
own instead of needing manual sweeps.

The core idea: **labels alone don't keep an inbox clean — filters do.** A label is just a
tag; a filter is the rule that applies it (and can skip the inbox) automatically on incoming
mail. Most label sprawl happens because labels were created by hand and never auto-applied, so
they accumulate and go stale. This skill fixes both halves: a lean label set + the filters
that feed it.

## Prerequisites

- The `gog` CLI, authenticated to the target Gmail account (`gog auth list` shows it).
- Verify first: `gog gmail labels list -p` should return the account's labels.

## When to use

- "My Gmail labels are a mess / clean up my labels / start fresh"
- "My inbox keeps filling with junk / stop the noise / auto-file my mail"
- "Set up Gmail filters", "organize my email by project/sender"

## Key facts to hold (these prevent mistakes)

- **Deleting a label is mildly destructive.** The emails survive (they stay in All Mail /
  are still searchable); only the *tag* is lost. But any **filter that applies that label
  breaks**. So delete labels before rebuilding filters, not after.
- **Filters apply to *incoming* mail only** — they are **not retroactive**. Wiring a filter
  today does not touch what's already in the inbox; it keeps *future* mail sorted. Say this
  to the user so they don't expect the current backlog to move (they clear that once, by
  hand or with an archive sweep).
- **Do not trust label message counts.** `gog gmail labels get <id>` can report `0` for
  every label even when they clearly hold mail (a known API/index quirk). Decide keep-vs-kill
  from label *names* and the user's knowledge, not from counts.
- **Deletion is a judgment call the user owns.** Never bulk-delete labels without an explicit
  go-ahead and a backup first. Integration-managed labels (e.g. `[Notion]`, `[Imap]`, anything
  a connected app created) should be preserved unless the user specifically says otherwise —
  deleting them can break the integration.

## Workflow

### 1. Survey and back up

List the current labels and save the user-label names to a backup file first, so anything
deleted can be recreated:

```bash
gog gmail labels list -p                        # ID, NAME, TYPE  (type=user vs system)
gog gmail labels list -p | awk -F'\t' '$3=="user"{print $2}' > labels-backup-$(date +%F).txt
```

Show the user the current user-labels grouped into buckets — **stale** (dated/past-event
labels, obvious one-offs), **duplicates** (mergeable), **integration** (preserve), **keep**.
This grouping is the proposal they approve.

### 2. Agree the target, then confirm deletes

Propose a **small** taxonomy — a handful of labels, not dozens. Sprawl is the disease; the
cure is few labels that each earn their place. A good default shape:

- `Finance` — bank, tax, invoices, receipts (one home for money)
- `People` — real humans, so personal mail never drowns in notifications
- `Projects/<Name>` — nested, one per active project that actually generates mail
- `@Action` — one manual tag the user applies when something needs them (sorts to the top)

Get explicit approval before deleting anything. If the user says "delete all / start fresh,"
still preserve integration labels and confirm that blanket scope once.

### 3. Delete (clean slate or targeted)

Delete by ID (names work too, but IDs are unambiguous). `-y` skips the confirm prompt:

```bash
gog gmail labels delete <labelId> -y
```

To wipe all user labels except integration ones, iterate the list and skip names that belong
to a connected app (e.g. those starting with `[`). Report what was deleted and what was kept.

### 4. Create the new set

Nesting uses a `/` in the name — Gmail auto-creates the parent:

```bash
gog gmail labels create "Finance"
gog gmail labels create "People"
gog gmail labels create "@Action"
gog gmail labels create "Projects/WeDance"
```

### 5. Wire the filters (the part that keeps it clean)

Two filter shapes do almost all the work:

**Auto-label, keep in inbox** — for mail the user wants to see *and* have tagged:

```bash
gog gmail filters create --from "bank-domain.com" --add-label "Finance"
gog gmail filters create --from "someone@gmail.com" --add-label "People"
```

**Auto-archive noise — skip inbox + mark read** — for recurring senders the user never needs
to act on (marketing, social, CI/deploy bots, receipts they don't read):

```bash
gog gmail filters create --from "marketing.example.com" --archive --mark-read
```

Match options: `--from`, `--to`, `--subject`, `--query` (full Gmail search syntax, e.g.
`--query 'from:(a.com OR b.com) -is:starred'`), `--has-attachment`. Actions: `--add-label`,
`--remove-label`, `--archive` (skip inbox), `--mark-read`.

**Where the sender list comes from:** derive it from the user's actual mail — the senders they
just triaged, the noise that keeps reappearing, the people/projects they named. Do **not**
hardcode a personal sender list into this skill; it stays generic. If the user recently swept
their inbox, the senders they archived are the exact noise-filter candidates.

Prefer domain-level matches (`linkedin.com`) over single addresses when a whole domain is
noise — one filter covers all of it.

### 6. Verify

```bash
gog gmail filters list -p        # confirm each filter landed
gog gmail labels list -p         # confirm the new taxonomy
```

Report back: labels created, filters wired (split into auto-label vs auto-archive), the backup
file path, and the two caveats the user must remember — **filters are forward-only** (the
existing backlog won't move; clear it once) and **any filter referencing a since-deleted label
is dead**.

## Notes

- If the user's inbox has a large existing backlog, this skill sets up the *future* hygiene;
  clearing the current backlog is a separate one-time sweep (`gog gmail archive <ids...>` or
  select-all → Archive in the Gmail UI, which is more reliable for very large counts).
- Keep a record of the taxonomy + filter rules somewhere durable (the user's ops notes) so the
  system is reproducible and the next cleanup starts from a known baseline.
