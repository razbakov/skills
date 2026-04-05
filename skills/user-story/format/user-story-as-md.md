# Template: Markdown file in `docs/issues/`

Save the story as a standalone markdown file with YAML frontmatter. Create the `docs/issues/` directory if it does not exist.

## Filename

Kebab-case derived from the title, e.g. `docs/issues/1.1-search-find-hotels-by-city.md`.

## YAML frontmatter fields

- `title` — the full ticket title (Topic: Action)
- `type` — Story, Task, or Bug

The markdown body starts immediately after the frontmatter closing `---`.

## Example: Rules-oriented story

```markdown
---
title: "Search: Find Hotels by City, Name, or Street"
type: Story
---

As a user, I want to use a search field to type a city, name, or street, so that I can find matching hotel options.

## Acceptance Criteria
- The search field is placed on the top bar.
- Search starts once the user clicks "Search".
- The field contains a placeholder with grey-colored text: "Where are you going?"
- The placeholder disappears once the user starts typing.
- Search is performed if a user types in a city, hotel name, street, or all combined.
- Search is in English, French, German, and Ukrainian.
- The user can't type more than 200 symbols.
- The search doesn't support special symbols (characters). If the user has typed a special symbol, show the warning message: "Search input cannot contain special symbols."
```
