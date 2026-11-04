---
name: file-issue
description: 'Write a clear, self-contained issue for a task, user story, or bug, in S3 form (Tension, Driver, Requirement, Response options), so that anyone can pick it up cold. Use whenever something should become an issue or ticket: "file an issue", "create a ticket", "log this bug", "make a story for this", "plan it", "put it in the backlog", or when a session turns up follow-up work, a bug, or a user report that someone else should handle, even if the user does not say "issue". Focuses on what the issue says, whichever tracker it goes into. Not for implementing an existing issue, and not for a full INVEST story with detailed acceptance criteria (use user-story for that).'
---

# File Issue

Turn a problem found in conversation, in a user report, or during other work into one issue that a person or agent can pick up without having been there.

The issue uses the S3 (Sociocracy 3.0) shape: what hurts, why it matters, what done looks like, and which ways forward were considered. The shape stays the same every time, so issues read alike no matter who wrote them.

This skill is about the **content** of the issue. Where it gets filed (which tracker, project, labels, board) comes from the user's own setup. Follow that if it exists. If it doesn't, give the user the finished issue and ask where it should go.

## 1. Understand the tension first

Before writing, be able to answer these in one sentence each:

- **Who** is affected (a user role, a team, a process)?
- **What** do they experience, observably? (what happens, where, when)
- **What** should happen instead?
- **Why** does it matter now?

If one of these is unknown, find out (ask the user, read the report, look at the thing that misbehaves). For a bug, reproduce it or find out what explains it before filing. If you can't, say so in the issue. Guessing a cause and writing it as fact sends whoever picks the issue up in the wrong direction.

Check whether an issue for the same tension already exists. If so, add the new information there instead of filing a duplicate.

## 2. Describe behaviour, not code

Write the issue in terms of what people see and need, not in terms of the implementation:

- Name the **page, screen, feature, or step** a user would recognise, not the file, function, or table behind it.
- Describe **what happens and what should happen**, not which line is wrong.
- Leave the **solution open** unless it was already decided. The person who picks it up will read the code themselves. A premature implementation detail in the issue anchors them to it and goes stale as the code changes.

Implementation hints are allowed in one place only: **Response options**, phrased as options, not instructions.

## 3. Write it

**Title:** `<Topic>: <what changes>`. The topic is where the change lives, in the words a user would use. A reader should be able to sort the issue from the title alone.

Good: `Checkout: show the total price before the payment step`
Weak: `Fix bug in price calculation`

**Body:**

```markdown
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
```

How to fill it well:

- **One tension per issue.** If the request holds several unrelated problems, write several issues and say they are related.
- **Tension is observation, not diagnosis.** "Customers don't see app orders in their order history" beats "the query is missing a join".
- **Driver answers "so what?"** If you can't name the need, the issue probably isn't worth filing yet. Say that instead of inventing a driver.
- **Requirement is the outcome, not the plan.** Each bullet should be verifiable from the outside: "an order placed in the app appears in the order history", not "add a condition to the query".
- **Response options: at least one.** If the conversation already settled a direction, mark it `chosen` with the reason. Otherwise mark one `recommended` and leave the decision open.
- **Plain language, short sentences.** The reader may not be an engineer. Explain any term a newcomer wouldn't know, once.
- **No secrets or personal data** (passwords, tokens, emails, phone numbers). Refer to people by role.
- If a classic user story helps, put "As a … I want … so that …" as the first line of Tension.

## 4. Hand it over

- If the user's setup says where issues go and how they are labelled or assigned, follow it. Give the issue exactly one owner when the setup uses owners: with none, nobody picks it up; with two, both or neither do.
- Otherwise show the finished title and body to the user and ask where to file it.
- After filing, read the issue back from the tracker to confirm the title, body, and owner actually landed. Then report the link, or the place it was filed, and which response option was chosen or left open.

## Example

From a session where a customer reported that a recent order was missing from their account:

> **Order history: show orders placed through the mobile app**
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
