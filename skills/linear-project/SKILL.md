---
name: linear-project
description: 'Hand a bigger-picture conversation over to Linear as an initiative → project → issues structure, keeping the user''s original words as the project brief. Use when a chat about a direction, a product area or a set of related needs should land in Linear: "save this in Linear", "put my message in Linear", "which initiative / project does this belong to", "hand this over to Linear", "set this up in Linear", "add the open issues to the project", or at the end of a session that turned a long ask into shipped work plus follow-ups. Works one level at a time and creates only what the user asked for. Not for a single bug or task (use linear-issue), and not for running issues as an agent (use linear-agent).'
---

# Linear Project

Turn a bigger-picture conversation into Linear's three levels: an **initiative** (the outcome), a **project** (the deliverable, with the user's original words as its brief) and **issues** (the units of work), so the thinking from the chat survives and the work can be tracked.

Two rules matter more than the structure:

- **Create only what the user asked for.** "Save my message in Linear" means one project with that message, not an initiative, a project and ten issues. Propose the rest, then wait. A "yes" to a proposal covers what that proposal said, not more you think of later.
- **"As is" means as is.** The brief is the user's message word for word. No summary of your own, no status section, no cleanup, unless they ask for it.

## 1. Look at the workspace first

Before proposing anything, read what exists. Linear hides archived things by default, so a workspace can look empty when it isn't.

- **Teams** (`list_teams`): which team this work belongs to.
- **Initiatives and projects, including archived** (`includeArchived: true`): reuse a live one that fits instead of making a duplicate. Archived ones show how the workspace was organised before, and what to avoid repeating.
- **Recent issues in the area** (`list_issues` with a query): don't re-file what already exists.

Bucket projects ("Inbox", "WeDance", "Plan") that live forever are an anti-pattern. If you find them, don't add more.

## 2. Map the conversation onto Linear's levels

| Level | What it is in Linear | What goes in it |
|---|---|---|
| **Team** | People sharing one workflow and backlog | Usually exists already. One team per stream of work (a product, personal admin…). The Linear MCP can't create teams: if a new one is needed, say so and let the user create it in Linear. |
| **Initiative** | An outcome steered toward over months; groups projects | A short name stating the outcome. Created only when the user wants it, or when they ask where the project belongs and none fits. |
| **Project** | A deliverable with a scope, a lead and an end; done when shipped | The conversation's main ask. The description is the user's original message, verbatim. |
| **Issues** | One unit of work each, closable on its own | The concrete pieces that are still open. Only when asked. |
| **Labels** | Cross-cutting tags | Only if the team already uses them. Don't invent a taxonomy. |

A long message with several needs is a project brief, not one issue. As one issue it never closes; as a brief it stays whole while issues track progress against it.

## 3. Propose, then create level by level

Reply with a short proposal before creating anything:

1. The initiative it belongs to (an existing one, or a new name with a one-line outcome).
2. The project name, and that the brief will be the message word for word.
3. The open issues you see, as a plain list, if the user may want them.
4. Anything structural only they can decide (a new team, moving existing work).

Then create exactly what they confirm, one level at a time. If they stop a call, stop and ask; don't retry it in another form.

## 4. Write the project

- **Name:** the deliverable in a few words ("City channels"), not a category.
- **Description:** a heading such as `## Original brief (verbatim, <who>, <date>)`, then the user's message as a block quote, exactly as written: same language, typos, lowercase, line breaks. Add nothing below it unless asked.
- **Getting the words right:** copy the message from the conversation itself; don't retype it from memory, because small "fixes" slip in and the quote stops being a quote. If the talk happened in another session, find it (session transcript search, the chat export, the Telegram message) instead of reconstructing it. If you can't find the exact text, say so and ask the user to paste it.
- **Links:** where the conversation or the shipped work lives (a PR, a doc). If the chat has no URL, mention it in your reply instead of inventing one.
- **Initiative, team, lead:** as agreed. Status `started` only if work is already under way.

## 5. Write the issues (only when asked)

Write and place each issue with the **linear-issue** skill, so every issue reads the same whether it came from a project or on its own: the Origin, the S3 shape (Tension, Driver, Requirement, Response options), collapsed Agent notes, and its status, owner, priority, labels and relations. One issue per open piece of work. On top of that, for a whole project:

- **Origin from the brief:** each issue's Origin quotes the lines of the project brief it comes from, with "project brief" as the source, so it leads back to the user's words.
- **Order:** create blockers first (setup before what needs it) so the later issues can point at them with `blockedBy`.
- **Status across the project:** usually one or two issues are committed now (Todo, with an owner); the rest wait in Backlog, prioritised relative to each other.
- **Already-shipped work:** don't file issues just to mark them Done unless the user asks. A PR link on the project is enough.

## 6. Report back

List what you created as a table (ID linked, title, status, priority), plus any structural decision still open (e.g. "create a team for this, then I can move the issues"). Don't repeat the issue bodies.
