# Template: Markdown file in `docs/issues/`

Save the story as a standalone markdown file with YAML frontmatter. Create the `docs/issues/` directory if it does not exist.

## Filename

Kebab-case derived from the title, e.g. `docs/issues/search-find-hotels-by-city.md`.

## YAML frontmatter fields

- `type` — Story, Task, or Bug
- `title` — the full ticket title (Topic: Action)
- `status` — always `draft` when first created

The markdown body starts immediately after the frontmatter closing `---`.

## Example: Rules-oriented story

```markdown
---
type: Story
title: "Search: Find Hotels by City, Name, or Street"
status: draft
---

# Search: Find Hotels by City, Name, or Street

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

## Example: Scenario-oriented story

```markdown
---
type: Story
title: "Sign In: Forgot Password"
status: draft
---

# Sign In: Forgot Password

As a user, I want to be able to recover the password to my account, so that I will be able to access my account in case I forgot the password.

## Scenario: Forgot password
- Given: The user navigates to the login page.
- When: The user selects "Forgot password" option.
- And: Enters a valid email to receive a link for password recovery.
- Then: The system sends the link to the entered email.
- Given: The user receives the link via the email.
- When: The user navigates through the link received in the email.
- Then: The system enables the user to set a new password.
```
