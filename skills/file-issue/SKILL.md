---
name: file-issue
description: 'File a task, user story, or bug report as a tracker issue (GitHub Issues or Linear) with an S3 body (Tension, Driver, Requirement, Response options), one owner label, and a board entry, following the tracker routing in the user''s CLAUDE.md. Use whenever an issue or ticket should actually land in a tracker: "file an issue", "create an issue for this", "open a ticket", "log this bug", "make a story for X", "plan it", "put this in the backlog", or when a session turns up follow-up work, a bug, or a user report that someone else should pick up — even if the user doesn''t say "issue". Not for implementing an existing issue (use github-issue), and not when the user only wants a story drafted in chat or as a file without filing it (use user-story).'
---

# File Issue

Turn a tension found in conversation, code, or a user report into one well-formed tracker issue that anyone (human or agent) can pick up cold.

The format is S3 (Sociocracy 3.0): every issue says what hurts, why it matters, what done looks like, and which ways forward were considered. The value of the skill is that this shape is the same every time, no matter which session or repo files the issue.

## Step 1: Load the instance config

This skill holds no config. Read it from the CLAUDE.md chain in effect (global, org, project) and the project's own README/CLAUDE.md. Look for:

| What | Typical wording to search for |
|---|---|
| **Tracker routing**: which kind of item goes where (e.g. stories and bugs → GitHub Issues, governance or blockers → Linear) | "Issue tracker", "user stories and bug reports go to", "Tasks live in" |
| **Repo for a project**: the project's own repo | "Project Path Registry", the `git remote` of the project folder |
| **Owner labels**: label prefix and allowed values | "`agent:*`", "Ownership labels" |
| **Board**: project board number and owner, if issues must be added to one | "Control Center board", "gh project item-add" |

If the config can't be found, use these defaults and say so in the report: GitHub Issues in the repo of the project the work belongs to, no owner label, no board.

If the item belongs in a tracker other than GitHub (e.g. Linear), use that tracker's tool, but keep the same S3 body and the same steps below.

## Step 2: Pick the repo and check for duplicates

1. Find the repo the **change** belongs to, not the repo you're sitting in. A bug in a web app goes to the web app's repo even when found from an ops folder. If the fix spans two repos, file one issue per repo and link them to each other.
2. Search before filing:
   ```bash
   gh issue list -R <owner>/<repo> --state all --search "<2-4 key words>" --limit 10
   ```
   If a matching open issue exists, add a comment with the new information instead of filing a duplicate. If a matching closed one exists, link it from the new issue.

## Step 3: Ground it in reality

Before writing, read what the issue is about: the relevant source files, routes, tables, the page that misbehaves, the user's report. Use the real names (file paths, function names, page names, UI labels, handles) in backticks. An issue that says "the feed is missing events" is weaker than one that names `profileFeedEvents` in `server/utils/profileFeed.ts` and the column it ignores.

For a **bug from a user report**, reproduce it (or at least find the code path that explains it) with the reporter's data before filing. If you can't reproduce it, say so in the Tension.

## Step 4: Write the issue

**Title:** `<Topic>: <what changes>`. The topic is where the change lives (a page, a feature, a component). A reader should be able to sort the issue from the title alone.
Example: `Profile feed: include events where the profile is in the line-up`

**Body** (write it to a temp file; inline text on the command line breaks on quotes and multi-byte characters):

```markdown
## Tension
What hurts or is off, observed and concrete. Who is affected and where they see it.
For a bug: steps to reproduce, what happens, what should happen, a link to the page.

## Driver
The underlying need: why this matters now, which goal or user need it serves.

## Requirement
What done looks like, as checkable bullets. Include what must keep working.
For a story: acceptance criteria. Name the test that will prove it, if any.

## Response options
1. <option> (chosen: <one-line reason>)
2. <option> (rejected: <one-line reason>)
```

Rules for the body:

- **One tension per issue.** If the request holds several unrelated problems, file several issues.
- **Requirement is the outcome, not the plan.** Implementation detail belongs in Response options.
- **Response options:** at least one. If a direction was already decided in the conversation, mark it `chosen` with the reason; otherwise mark the recommended one and leave the decision open.
- **Plain language, short sentences.** The reader may be a non-engineer. Explain jargon once.
- **No secrets, tokens, or personal data** (emails, phone numbers) in the body. Refer to a person by role or public handle.
- If the user wants a classic user story too, add the "As a … I want … so that …" line at the top of Tension. Use the `user-story` skill when a full INVEST story with detailed acceptance criteria is asked for.

## Step 5: Create it

```bash
BODY="$(mktemp)"
cat > "$BODY" <<'EOF'
## Tension
...
EOF
gh issue create -R <owner>/<repo> --title "<Topic>: <change>" --body-file "$BODY" --label "<prefix>:<owner>"
```

- **Exactly one owner label** when the config defines them. Dispatch loops and digests pick up work by this label, so an issue with none sits unowned, and one with two gets picked up twice or by nobody. Check it exists first (`gh label list -R <owner>/<repo> --search <prefix>`); if it doesn't, create it with `gh label create` rather than dropping the label.
- **Board:** if the config names a board, add the issue: `gh project item-add <number> --owner <board-owner> --url <issue-url>`.
- Create issues one at a time. Some trackers (Linear especially) silently drop writes under parallel load while still returning success.

## Step 6: Verify and report

```bash
gh issue view <url> --json title,labels,url
```

Confirm the title, label, and (if used) board membership actually landed. Then report to the user:

- the **full issue URL** (raw, not a bare `#123`),
- the repo and owner label,
- one line on which response option was chosen or left open,
- any duplicate you linked or commented on instead.

## Example

Filed from a session about a profile website showing no workshops:

> **Profile feed: include events where the profile is in the line-up** · label `agent:engineering`
>
> **Tension:** A profile's feed (`profileFeedEvents` in `server/utils/profileFeed.ts`) lists only events the profile hosts or organises. An artist mostly appears in other people's events, named in their line-up (`events.artists`), so the artist's site shows an empty "upcoming workshops" placeholder even when booked.
>
> **Driver:** Profile websites use the feed as their schedule. For artists it has to include the events they teach or play at.
>
> **Requirement:**
> - The feed also lists published, upcoming events whose `artists` contains the handle, case-insensitive.
> - Host and organiser events still list; an event matching twice appears once.
> - Covered by a DB test.
>
> **Response options:**
> 1. Widen the `where` in `profileFeedEvents` with an `exists` over the artists array (chosen: one query, works for every profile type).
> 2. A separate artist-only query merged in JS (rejected: two queries and a sort for the same result).
