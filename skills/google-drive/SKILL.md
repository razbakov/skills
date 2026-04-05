---
name: google-drive
description: Operate Google services from the terminal using gog. Use when requests involve Gmail, Calendar, Chat, Classroom, Drive, Docs, Slides, Contacts, Tasks, People, Sheets, Forms, Apps Script, Groups, or Keep workflows, including auth checks, data listing/search, file transfer, and command automation.
---

# Google Services (gog)

## Supported Services

- Top-level service commands in `gog -h`:
  `gmail`, `calendar`, `chat`, `classroom`, `drive`, `docs`, `slides`, `contacts`, `tasks`, `people`, `sheets`, `forms`, `appscript`, `groups`, `keep` (Workspace only).
- OAuth values in `gog login --services`:
  `gmail`, `calendar`, `chat`, `classroom`, `drive`, `docs`, `slides`, `contacts`, `tasks`, `sheets`, `people`, `forms`, `appscript`, plus `user` and `all`.

## Quick Start

1. Confirm CLI and service commands:

```bash
gog -h
gog drive -h
gog <service> -h
```

2. Confirm auth:

```bash
gog status
# if needed
gog login <email> --services all
```

3. Prefer stable output for automation:
- Use `-j --results-only` for JSON pipelines.
- Use `-p` for parseable plain text.

## Common Commands

```bash
# list files
gog drive ls --max 50
gog drive ls --parent <folderId> --max 100

# search
gog drive search "<query>" --max 50

# metadata
gog drive get <fileId>

# transfer
gog drive upload <localPath> --parent <folderId>
gog drive upload <localPath> --replace <fileId>
gog drive download <fileId> --out <path>

# organize
gog drive rename <fileId> "<newName>"
gog drive move <fileId> --help

# delete (trash by default)
gog drive delete <fileId>
```

## Guardrails

- Run mutating commands with `--dry-run` first when supported.
- Use `--account <email>` when multiple Google accounts are configured.
- Use `--no-input` for CI/non-interactive runs.
- Use `--permanent` only if the user explicitly requests irreversible delete.

## Troubleshooting

- If auth fails, run `gog status` then `gog login <email> --services drive`.
- If flags are unclear, run `gog drive <subcommand> -h`.
