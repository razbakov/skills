# Template: Chat output

Present the story directly in the conversation as formatted markdown. No files are created.

Use the same heading structure and formatting rules from the skill, but without YAML frontmatter.

## When to use

- Quick drafts or brainstorming
- Discussions where the story may change before being finalized
- Projects that do not track stories as files

## Example

```markdown
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
