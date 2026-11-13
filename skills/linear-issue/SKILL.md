---
name: linear-issue
description: 'Write a clear, self-contained issue for a task, user story, or bug, in S3 form (Tension, Driver, Requirement, Response options) with an Origin that quotes the original ask, links its source, and marks it as an idea, agreement, or promise, so that anyone can pick it up cold. Use whenever something should become an issue or ticket: "file an issue", "create a ticket", "log this bug", "make a story for this", "plan it", "put it in the backlog", or when a session turns up follow-up work, a bug, or a user report that someone else should handle, even if the user does not say "issue". Focuses on what the issue says, whichever tracker it goes into. Not for implementing an existing issue, and not for a full INVEST story with detailed acceptance criteria (use user-story for that).'
---

# Linear Issue

Turn a problem found in conversation, in a user report, or during other work into one issue that a person or agent can pick up without having been there.

The issue opens with its **origin**: the ask in the requester's own words, where it was said, and whether it is an idea, an agreement, or a promise. Then comes the S3 (Sociocracy 3.0) shape: what hurts, why it matters, what done looks like, and which ways forward were considered. The shape stays the same every time, so issues read alike no matter who wrote them.

This skill is about the **content** of the issue. Where it gets filed (which tracker, project, labels, board) comes from the user's own setup. Follow that if it exists. If it doesn't, give the user the finished issue and ask where it should go.

## 1. Understand the tension first

Before writing, be able to answer these in one sentence each:

- **Who** is affected (a user role, a team, a process)?
- **What** do they experience, observably? (what happens, where, when)
- **What** should happen instead?
- **Why** does it matter now?

If one of these is unknown, find out (ask the user, read the report, look at the thing that misbehaves). For a bug, reproduce it or find out what explains it before filing. If you can't, say so in the issue. Guessing a cause and writing it as fact sends whoever picks the issue up in the wrong direction.

Check whether an issue for the same tension already exists. If so, add the new information there instead of filing a duplicate, including the new source in its Origin.

## 2. Read the docs and the code before you write

A request says what someone wants. It rarely says what the product does today, and an issue that only restates the request leaves the reader to find that out alone. Before structuring anything, establish the current state:

- **Bring the source up to date first** (`git fetch`, check the branch is not behind). A stale checkout makes fixed behaviour look broken.
- **Read the project's docs** for the area: README, feature docs, decision records, the project's notes or profile. They say what the feature is meant to do and what was already decided.
- **Read the code behind the screen or step the request names.** Find what is shown, where the data comes from, and what is missing. This is how you find out that a field "doesn't exist" because nothing stores it, or that a view exists on one page but not another.
- **Look at related issues**, open and closed, for decisions and earlier attempts.

Use what you find to write a Tension that states **what happens today**, not only what was asked. If the request rests on a wrong assumption (it asks for something that already exists, or misreads where data comes from), say so plainly in the Tension: that is often the real answer. If you could not reach the code or docs, say that too instead of guessing.
## 3. Record the origin

The rest of the issue is rewritten for whoever picks it up. The Origin keeps the way back: to the exact words, to the conversation, and to anyone who is waiting on the result.

- **Quote the original ask word for word**, in its original language, keeping typos and punctuation. Trim it to the part that matters, mark cuts with `…`, and never reword, translate or tidy it. A paraphrase is already an interpretation, and the quote is what lets anyone check later that the issue still matches what was asked.
- **Name the source**: the channel (Telegram, email, meeting, WhatsApp, user report, PR comment, chat session), the date, and who asked. **Link it** when a link exists: a message link, an email thread, a meeting note, a comment URL. If there's no link, write "no link" and say where to look (for example "desktop chat, 2026-11-07").
- **Mark the kind, exactly one,** seen from the side of whoever owns the backlog (the user and their team), not the person who wrote the message:
  - **idea**: the user's own, or a suggestion someone made that nobody committed to. Nobody is waiting on it.
  - **agreement**: decided together with someone. Name who.
  - **promise**: the user or their team told someone it will be done. Name who, what was promised, and by when if a date was given.
- **Don't guess the kind.** If the source doesn't make it clear whether someone was promised something, ask. Calling an idea a promise turns it into an obligation; missing a real promise means someone ends up let down.
- **Several sources** (for example merged duplicates): quote and link each one. If any of them is a promise, the issue is a promise.

## 4. Describe behaviour, not code

Write the issue in terms of what people see and need, not in terms of the implementation:

- Name the **page, screen, feature, or step** a user would recognise, not the file, function, or table behind it.
- Describe **what happens and what should happen**, not which line is wrong.
- Leave the **solution open** unless it was already decided. Give the reader the facts about today's behaviour (step 2), not the fix. A premature implementation detail in the issue anchors them to it and goes stale as the code changes.

Implementation hints are allowed in two places only: **Response options**, phrased as options, not instructions; and an optional closing **What the code and docs say** section, which lists the facts from step 2 with their file or doc paths so the reader can check them. Keep code references out of Tension, Driver and Requirement.

## 5. Write it

**Title:** `<Topic>: <what changes>`. The topic is where the change lives, in the words a user would use. A reader should be able to sort the issue from the title alone.

Good: `Checkout: show the total price before the payment step`
Weak: `Fix bug in price calculation`

**Body:**

```markdown
## Origin
> <the original ask, verbatim, trimmed with …>

- **Source:** <channel>, <date>, <who asked> · <link, or "no link: where to look">
- **Kind:** idea | agreement (with <who>) | promise (to <who>: <what>, by <when>)

## Tension
What hurts or is off, observed and concrete. Who is affected and where they notice it.
For a bug: steps to reproduce, what happens, what should happen, where to see it.

## Driver
The underlying need: why this matters, which goal or user need it serves.

## Requirement
What done looks like, as checkable bullets someone could verify by using the product.
Include what must keep working.

## Response options
1. <option> (recommended / chosen: one-line reason)
2. <option> (rejected / alternative: one-line reason)

## What the code and docs say (optional)
- <fact about today's behaviour> (`path/to/file`, `docs/feature.md`)
```

How to fill it well:

- **Fill the Origin every time** (step 3). When the issue came up in your own work with no requester, quote nothing, set the source to where you found it ("found while fixing the checkout page"), and the kind to idea.
- **One tension per issue.** If the request holds several unrelated problems, write several issues and say they are related.
- **Tension is observation, not diagnosis.** "Customers don't see app orders in their order history" beats "the query is missing a join".
- **Driver answers "so what?"** If you can't name the need, the issue probably isn't worth filing yet. Say that instead of inventing a driver.
- **Requirement is the outcome, not the plan.** Each bullet should be verifiable from the outside: "an order placed in the app appears in the order history", not "add a condition to the query".
- **Response options: at least one.** If the conversation already settled a direction, mark it `chosen` with the reason. Otherwise mark one `recommended` and leave the decision open.
- **Plain language, short sentences.** The reader may not be an engineer. Explain any term a newcomer wouldn't know, once.
- **No secrets or personal data** (passwords, tokens, emails, phone numbers), in the quote too: cut them with `…`. Refer to people by role, or by first name where the Origin needs to say who asked or who was promised something.
- If a classic user story helps, put "As a … I want … so that …" as the first line of Tension.

## 6. Hand it over

- If the user's setup says where issues go and how they are labelled or assigned, follow it.
- Otherwise show the finished title and body to the user and ask where to file it.
- Make a **promise** visible without opening the issue: add a `promise` label if the tracker has labels (create it if it's missing and the setup allows), otherwise start the title with `[Promise]`. Open promises should be listable in one view.
- Give the issue exactly one owner when the setup uses owners: with none, nobody picks it up; with two, both or neither do.
- After filing, read the issue back from the tracker to confirm the title, body, and owner actually landed. Then report the link, or the place it was filed, its kind (idea, agreement, or promise and to whom), and which response option was chosen or left open.

## Example

From a session where a customer reported that a recent order was missing from their account:

> **Order history: show orders placed through the mobile app**
>
> **Origin:**
> > "I ordered on the app last Tuesday and it's not in my account … I need the invoice for my company."
>
> - **Source:** support email from a customer, 2026-03-12 · link to the support ticket
> - **Kind:** promise (to the customer: support replied "we'll fix the order history and send you the invoice", no date given)
>
> **Tension:** A customer's order history shows only orders placed on the website. Orders placed in the mobile app are missing, although they were paid for and delivered. Customers who look for an invoice or want to reorder think the order was lost, and some contact support.
>
> **Driver:** Order history is where customers go for invoices, returns, and reorders. If it's incomplete, they lose trust and support gets tickets that shouldn't exist.
>
> **Requirement:**
> - An order placed in the mobile app appears in the customer's order history, with the same details as a website order.
> - Website orders still appear. No order appears twice.
> - Cancelled orders show as cancelled, same as today.
>
> **Response options:**
> 1. Show orders from both channels in one list (recommended: customers don't care where they ordered).
> 2. Add a "Mobile orders" tab (alternative: quicker, but customers have to know where to look).
