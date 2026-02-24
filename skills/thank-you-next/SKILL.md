---
name: thank-you-next
description: 'Use when the user wants prompt-only backlog progression: select the next not_started story from docs/backlog.yaml, mark it in_progress, write a plan, and implement it.'
---

# Thank You Next

## Overview

Run a single "next story" delivery loop in prompt-only mode:

1. pick the next story
2. mark it `in_progress`
3. create a feature branch
4. write a plan
5. implement the plan
6. prepare a pull request

Use this for hands-off backlog progression in repos that have `docs/backlog.yaml`.

## Requirements

- Run from the repository root.
- `docs/backlog.yaml` must exist and include `phases[].stories[].status`.
- `source.stories_path` should point to the original story files.
- Do not use Python or custom helper scripts.

## Workflow

### Step 1: Select next story and set status to in_progress

Open `docs/backlog.yaml` and find the first story in phase order where:

- `status: not_started`

Update:

- selected story `status` -> `in_progress`
- parent phase `status` -> `in_progress` when phase is `proposed`, `not_started`
- top-level backlog `status` -> `in_progress` when backlog is `proposed` or `not_started`

If no story is found, stop and report that the backlog is exhausted.

### Step 2: Create a feature branch

Create and switch to a new branch from `main`:

`git checkout -b feature/<id>-<story-key>`

The branch name combines the story id and key (e.g. `feature/TYN-001-add-login-page`).

### Step 3: Load the selected story

Resolve story file path from:

`<source.stories_path>/<story-key>.md`

Then extract:

- user story
- acceptance criteria
- implementation constraints

Treat acceptance criteria as the contract.

### Step 4: Write a plan

Create:

`docs/plans/<story-key>.md`

Plan rules:

- explicit files to create/modify
- test strategy first
- verification commands
- rollout/risk notes for high-impact changes

### Step 5: Implement the plan

Execute the plan end-to-end in the current session.

- do not stop at plan-only mode unless blocked
- implement and verify
- run project checks required by the story (tests/typecheck/build)

### Step 6: Prepare a Pull Request

When you finish you need to create pull request under `docs/pull-requests/<story-key>.md`, which should include information on how to test and follow PR best practices

In Summary also include started, finished, time spent and original estimate, i.e.:
- Started: 2026-02-24 16:00
- Finished: 2026-02-24 17:00
- Time spent: 1h 00m
- Estimate: 5

Calculate time spent by checking time of creation of the `docs/plans/<story-key>.md` and current time.

Keep backlog status as `in_progress` unless the user explicitly asks to mark it `done`.
