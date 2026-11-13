---
name: linear-issue
description: 'File a Linear issue the way Linear recommends: one concrete task with a clear outcome, a short title that states the task, a description with only what the task needs, the original ask quoted word for word with a link to where it came from, and the right team, status, owner, priority and relations. Use whenever something should become a Linear issue or ticket: "file an issue", "create a ticket", "log this bug", "put it in Linear", "add it to the backlog", or when a session turns up follow-up work, a bug or a user report someone else should handle, even if the user does not say "issue". Not for setting up an initiative or project from a bigger-picture conversation (use linear-project), and not for implementing an existing issue.'
---

# Linear Issue

File one issue that a person or agent can pick up without having been there, following the Linear Method ([linear.app/method](https://linear.app/method)):

- **Issues, not user stories.** Linear calls user stories an anti-pattern. An issue describes the task in plain language; the user experience is discussed in the project, not in each task.
- **Short and direct.** The title states the task. The description holds only what the task needs, or nothing when the title says it all.
- **Quote, don't summarise.** Feedback and requests are quoted directly, with a link to the conversation, so more context is one click away.

Filing goes through the Linear MCP tools (`list_teams`, `list_projects`, `list_issues`, `list_issue_labels`, `save_issue`, `get_issue`). If they aren't connected, give the user the finished title and description and say what to set when they file it.

## 1. Is it one issue?

An issue is **a task with a clear, defined outcome**: someone can do it and tell when it's done. Exploratory work counts when it's framed as a task ("Explore layouts for the city page", "Write the spec for city channels").

- **Too big** (several deliverables, or more than a few days' work): break it into smaller, tangible pieces. Steps of one change become sub-issues of a parent; a bigger body of work with its own brief is a project (linear-project).
- **Not a task** (an opinion, a vague wish, a discussion): don't file it. Say so and suggest where it belongs: a project brief, a doc, or a question back to the user.
- **Already there:** search first (`list_issues` with a `query`, including done and canceled ones). Add new information to an open issue as a comment instead of filing a duplicate. If a closed one comes back, file a new issue that links to it and says why it returned.

## 2. Know what happens today

A request says what someone wants, not what the product does now. Before writing, find out enough that the issue doesn't send the reader the wrong way:

- Update the source (`git fetch`) and read the code and docs behind the screen or step the request names.
- For a bug, reproduce it or find what explains it. If you can't, say so in the issue rather than guessing a cause.
- If the request rests on a wrong assumption (it asks for something that already exists), say that plainly: it's often the real answer.

## 3. Write it

**Title:** short and plain, stating the task, easy to scan in a list. Lead with the area only when the project doesn't already name it.

- Good: `Show orders placed in the mobile app in order history`
- Weak: `Order history bug`, `As a customer I want to see all my orders…`

**Description:** only what the task needs, in this order, dropping any part that adds nothing:

```markdown
> <the ask, quoted word for word, trimmed with …>

<who asked, where, when> · <link to the message, ticket or call notes>

<What happens today and what should happen instead: a few short sentences. For a bug: steps, what happens, what should happen.>

**Done when** <the outcome, checkable from the outside>

+++ Agent notes

- <file paths, commands, data to check, gotchas>

+++
```

- **The quote:** copy it from the source, word for word, in its original language with its typos. Never reword, translate or tidy it: a paraphrase is already an interpretation, and the quote is how anyone can check later that the issue still matches what was asked. Leave the quote out when the issue came from your own work; say where it came from instead ("found while fixing checkout").
- **The source line:** always a link when one exists. Without one, say where to look ("desktop chat, 2026-11-07").
- **Someone waiting:** if the user or their team promised this to someone, say so on the source line ("promised to the customer by support, no date"). Don't guess: ask when it's unclear. A promise also gets a due date when one was given, and the team's `promise` label if it has one.
- **Problem, not solution,** when someone else will do the work: describe what's wrong and let the assignee propose the fix. Write the solution only when it's already decided.
- **Plain language, short sentences, one term per concept.** The reader may not be an engineer.
- **Agent notes:** technical detail for an agent goes in the collapsed section at the end (`+++ Agent notes` … `+++`; Linear stores and shows it as `>>>`). Skip it when there's nothing technical to say.
- **No secrets or personal data** in the issue or the quote (passwords, tokens, emails, phone numbers): cut them with `…`. Use `@name` only for a real Linear user you mean to notify.

## 4. Place it

Read the workspace before choosing; don't invent structure.

- **Team** (`list_teams`): the team whose backlog the work belongs to. If none fits, ask; teams can't be created through the MCP.
- **Project** (`list_projects`): the live project it moves forward, if any. Standalone issues are fine.
- **Status:**
  - **Triage** for reports from outside the team (users, other teams, integrations), when the team uses triage. The team accepts, declines or merges them there.
  - **Todo** for work someone has committed to now. Linear may pull it into the current cycle; say so when it happens.
  - **Backlog** for everything else.
- **Owner:** one assignee, and ideally the person who will do it, since Linear's practice is that people write their own issues. No owner until someone commits.
- **Priority:** what moves things forward this week or this month goes high: unblocking others, fixing what's blocking users. Set it relative to the team's other open work, or leave it unset rather than guess.
- **Estimate:** only if the team estimates, on its own scale.
- **Labels** (`list_issue_labels`): only labels the team already uses. Ask before creating one.
- **Relations:** `blockedBy` / `blocks` when one can't start before another (create the blocker first to get its ID); `parentId` for sub-issues; `relatedTo` for siblings; `duplicateOf` rather than a second copy. Mentioning an issue ID in the description also links it as related.

## 5. File it and check it landed

1. Show the user the title, description and placement, unless they asked you to file it right away.
2. Create it with `save_issue` (no `id` when creating).
3. Read it back (`get_issue`) to confirm the title, description, project and owner landed and the Agent notes collapsed.
4. Report the issue ID as a link with its status and owner, and anything still to decide.

## Example

A customer wrote to support that a recent order was missing; support promised to fix it. Filed in the Shop team, project "Order history", Todo, assigned to the developer taking it, priority High:

> **Show orders placed in the mobile app in order history**
>
> > "I ordered on the app last Tuesday and it's not in my account … I need the invoice for my company."
>
> Customer, support email, 2026-03-12 · link to the ticket · support promised a fix and the invoice, no date
>
> Order history shows only orders placed on the website. Orders from the mobile app are missing, although they were paid and delivered, so customers can't find invoices and think the order was lost.
>
> **Done when** app orders appear in order history with the same details as website orders, with no order shown twice.
>
> *(collapsed)* **Agent notes:** order history reads only the web orders table (`api/orders/history.ts`); app orders are stored by the mobile checkout service (`services/mobile-checkout`).
