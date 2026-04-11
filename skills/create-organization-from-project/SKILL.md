---
name: create-organization-from-project
description: Use when a software project under ~/Projects should become a separate organization under ~/Orgs, or when governance files are mixed into a code repo and need to be split into a dedicated org workspace.
---

# Create Organization From Project

Create a dedicated org workspace from an existing project repo, without leaving governance mixed into deployable source code.

Use this when the user wants:
- "create organization" for an existing project
- a clean split between code and governance
- `~/Orgs/<OrgName>` created from `~/Projects/<project-name>`
- a dedicated org GitHub repo

Do not use this for greenfield projects with no codebase yet. Use `org-coach` directly there.

## Outcome

After this workflow:
- `~/Projects/<project-name>` contains only source code, assets, deployment config, and tests
- `~/Orgs/<OrgName>` contains governance, domains, roles, coordination, inbox, and agent definitions
- both workspaces have clear `CLAUDE.md` / `AGENTS.md` contracts
- local registries point to the correct org and code paths
- optional: the org workspace has its own GitHub repo

## Step 1: Inspect the project first

Read the project repo before moving anything:
- `README.md`
- `CLAUDE.md`
- `AGENTS.md`
- top-level tree
- any existing governance folders such as `logbook/`, `domains/`, `roles/`, `coordination/`, `inbox/`, `.claude/`

Decide whether the repo is:
- code-only already
- mixed code + org
- partially organized and needs cleanup

## Step 2: Use `org-coach` to detect the situation

Run the `org-coach` logic against the project context.

If the repo already has:
- a `CLAUDE.md` with `## Structure`
- primary driver, strategy, roles, domains, and policies

Then treat it as an **existing organization** and do a logbook review first.

If not, create the org from scratch using `org-coach` on autopilot, but still source context from the project repo.

## Step 3: Create the org workspace

Create `~/Orgs/<OrgName>` as a separate git repo.

Default shape:
- `CLAUDE.md`
- `AGENTS.md`
- `README.md`
- `.gitignore`
- `logbook/`
- `domains/`
- `roles/`
- `coordination/`
- `.claude/agents/`
- optional `inbox/`

Keep this workspace focused on governance and operations, not deployable source code.

## Step 4: Split code vs org artifacts

Move org artifacts out of the project repo into the org workspace.

Usually move:
- `logbook/`
- `domains/`
- `roles/`
- `coordination/`
- `.claude/`
- `inbox/`
- org-level `CLAUDE.md`
- org-level `AGENTS.md`

Usually keep in the project repo:
- `app/`, `src/`, `server/`, `components/`
- `public/`, `assets/`, `i18n/`
- `package.json`, lockfiles, TS config, build config
- deployment files like `vercel.json`
- tests tied to implementation
- environment files and runtime config

Rule: governance belongs in `~/Orgs`; product behavior and deployment belong in `~/Projects`.

## Step 5: Rewrite both roots

### Org workspace
Make `CLAUDE.md` and `AGENTS.md` say:
- org path
- code repo path
- structure map for governance files
- domain roles and AI agents
- working agreement: read code repo for implementation context, write org artifacts here

### Project repo
Make `README.md`, `CLAUDE.md`, and `AGENTS.md` say:
- this is the code repo
- governance lives in `~/Orgs/<OrgName>`
- this repo is source-code-only
- list code directories and deploy target

## Step 6: Add the minimum org operating layer

At minimum, map these roles in the org repo:
- **Instructor / Founder** or equivalent human owner
- **Coordinator** for cross-domain synthesis and prioritization
- **Autopilot** for approved cross-domain execution
- **Admin & Operator** for systems ownership and account continuity

Also create:
- a systems ownership map under `coordination/`
- review cadence entries for those roles and maps

## Step 7: Update registries

Update any local source-of-truth registries that route work:
- path registries in other org or ops docs
- local Codex / Claude project trust config
- any "project path registry" tables

If the user distinguishes org vs code, record both:
- `montuno-club (org)` -> `~/Orgs/MontunoClub`
- `montuno-club (code)` -> `~/Projects/montuno-club`

## Step 8: Create the org GitHub repo if requested

If the user wants a dedicated remote:
1. initialize git in `~/Orgs/<OrgName>` if needed
2. make the initial commit
3. create a separate GitHub repo, usually `<code-repo>-org`
4. add `origin`
5. push `main`

Default to **private** unless the user says otherwise, because org repos often contain governance and operational material.

## Verification

Before calling it done, verify:
- project repo top level is code-focused only
- org repo top level contains governance folders
- both roots have clear docs
- path registries point at the correct locations
- if a GitHub repo was created, `origin` exists and `main` tracks `origin/main`

## Common Mistakes

- Moving tests or deploy config into the org repo
- Leaving stale path references to the old mixed repo layout
- Treating `Coordinator` as execution instead of synthesis
- Forgetting `Autopilot`
- Creating the org repo but not pushing its default branch
- Keeping governance inside the code repo "temporarily" and never finishing the split

## Example Trigger

User: "cleanup org files from project and create clear org structure under ~/Orgs/MontunoClub. project should contain only source code."

Response pattern:
1. inspect current repo layout
2. run `org-coach` logic on the existing artifacts
3. create `~/Orgs/MontunoClub`
4. move governance folders there
5. rewrite both repo roots
6. update registries
7. optionally create `razbakov/<name>-org`
