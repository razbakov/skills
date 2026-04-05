# Template: Append to story file in `docs/issues/`

Add the estimate to an existing story file. If the story does not exist as a file yet, suggest using the user-story skill with the file template first.

## Changes to the story file

1. Add or update the `estimate` field in the YAML frontmatter.
2. Append an `## Estimate` section at the end of the markdown body.

## Example

Given an existing story file `docs/issues/search-find-hotels-by-city.md`, the frontmatter gains:

```yaml
estimate: 3
```

And the following section is appended:

```markdown
## Estimate
**Points:** 3

Touches the search component and results page with a clear approach; minor uncertainty around multi-language placeholder behavior.

| Factor | Score |
|--------|-------|
| Complexity | Medium |
| Uncertainty | Low |
| Effort | Medium |
| Risk | Low |
| Dependencies | Low |
```
