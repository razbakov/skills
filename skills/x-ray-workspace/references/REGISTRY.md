# Writing `registry.json`

`registry.json` is the only hand-written file behind the dashboard. It describes one workspace and
lives in that workspace (`ops/toolsdash/registry.json` is a good home); point the server at it with
`TOOLSDASH_REGISTRY`. It holds the half of the truth
no machine can derive: who owns a tool, how it is reached, what you switch to when it dies, and what
the fix actually is. Everything else is measured — call counts and failures come from the session
transcripts, health comes from the probes declared here.

Edit the file and refresh the page. There is no build step and no restart: the server re-reads it on
every refresh.

## Shape

```json
{
  "meta": { "owner": "…", "connected_verified": "2026-10-23", "note": "…" },
  "tools": [ { …one object per tool… } ]
}
```

`meta.connected_verified` is the date somebody last checked the `connected_now` flags against a live
session's connector list. Bump it when you re-check; the page prints it so nobody mistakes a stale
flag for a live reading.

## Fields

Every field below is required except `probe_ok`. Write all of them even when the answer is "none" —
an empty `alternatives` list is a finding (single point of failure), not a gap in the data.

| Field | Type | What it is |
|---|---|---|
| `id` | string | Stable slug. Other entries point at it from `depends_on` and `alternatives[].ref`, so renaming one means fixing those. Lowercase, hyphenated. |
| `name` | string | What you would call it out loud. Shown as the card and node title. |
| `category` | enum | `mcp`, `cli`, `api`, `browser`, `automation`, `skill`, `manual`. Drives the map's filter tabs. `manual` means a human does it in a UI and no automation path exists. |
| `access` | string | The actual route, specific enough to act on: the MCP server id, the binary path, the env file, the LaunchAgent label. The map shows everything before the first `·` under the node name, so put the kind first: `"MCP connector (OAuth) · server <id> · tenant <id>"`. |
| `connected_now` | bool | Only meaningful for MCP servers: was it in the connector list a live session declared on `meta.connected_verified`? `false` on an MCP entry produces **disconnected**. For anything with a probe, the probe outranks this. |
| `owner_agent` | string | The one agent, or person, accountable for it. `"—"` for host-provided plumbing nobody owns, `"all agents"` for shared infrastructure. One owner, never a list. |
| `also_used_by` | string[] | Other agents that reach for it. Drawn as faint edges on the map, so keep it to agents that genuinely use it. |
| `usage_keys` | string[] | How the scanner finds this tool in the transcripts. Prefix-matched (see below). `[]` is valid for things that leave no trace in a transcript, like a LaunchAgent. |
| `depends_on` | string[] | Other `id`s this tool needs in order to work. Draws the amber edges, **and** downgrades this tool to degraded when one of them is broken. Hard needs only, not "related to". |
| `alternatives` | object[] | `{kind, what, state, ref?}`. See below. |
| `fix` | string | What a person does next, in enough detail to act without re-diagnosing: the command, the file, the person to ask. Not "re-authenticate" — say which command against which host. |
| `docs` | string | Where the full story lives (repo path, runbook, `CLAUDE.md` section). `""` if nowhere. |
| `notes` | string | The thing that is true but not obvious: the gotcha, the history, why the obvious fix is wrong. |
| `probe` | string \| null | A read-only shell command, see below. `null` when nothing can be checked from this machine. |
| `probe_ok` | string | Optional regex matched against the probe's combined stdout+stderr. Omit it to fall back to the exit code. |

### `alternatives[]`

```json
{ "kind": "cli", "what": "the tracker CLI, which works unattended", "state": "live", "ref": "tracker-cli" }
```

- `kind` — `mcp`, `cli`, `api`, `skill`, `web`, `repo`, `local`, `automation`, `manual`.
- `what` — the fallback itself, concrete enough to use.
- `state` — `live` (works today), `degraded`, `broken`, or `always` for a path that cannot break,
  like a human using a web UI.
- `ref` — optional `id` of another registry entry. Add it whenever the fallback *is* another entry:
  it draws the teal dashed edge on the map and makes the panel entry clickable. Without a `ref` the
  alternative is still listed, it just is not wired into the graph.

### `usage_keys`

Prefix-matched against the ids the scanner produces. Everything that matches is summed into one
tool's call count, and the most recent match sets "last used" and "last failure".

| Id shape | Comes from | Example key |
|---|---|---|
| `mcp__<server>__<tool>` | any MCP call | `"mcp__<server-id>__"` — the trailing `__` matters, it catches every tool on that server |
| `cli:<name>` | a Bash command matching a pattern in `scan.py`'s `CLI_PATTERNS` | `"cli:terraform"` |
| `skill:<name>` | a `Skill` invocation | `"skill:daily-review"` |
| `agent:<type>` | an `Agent` / `Task` call | `"agent:Explore"` |
| a bare tool name | any built-in | `"Skill"`, `"WebFetch"` |

For a CLI the dashboard does not know about yet, add the pattern to `CLI_PATTERNS` in
[scan.py](scan.py) first — a `usage_keys` entry alone will never match. The pattern is a regex run
against the whole Bash command, so anchor it with `\b` to avoid catching substrings.

Two entries may share a key: `gh` against github.com and `gh` against a company Enterprise host
both watch `cli:gh`. They will report the same call count, because the transcript cannot tell which
host a `gh` invocation targeted; their probes still separate them. Say so in `notes` when you do
this.

## Writing a probe

The probe is what makes the page live rather than a document. Rules, in order of importance:

1. **Read-only.** It runs unattended on every refresh, up to 12 at a time. Never write, deploy,
   send, or delete. Prefer checking that a credential *exists and authenticates* over using it.
2. **Fast.** Hard-killed at 20s. Keep network calls to an auth check, not a data fetch.
3. **Quiet about secrets.** Print lengths and names, never values: `tok=${#TOKEN}`, not `$TOKEN`.
   The output is rendered on the page.
4. **Say something useful on success.** The output is shown verbatim in the card and the panel, so
   `tracker --version` beats `echo ok`.
5. **Fail loudly.** End with `|| echo FAIL` when the command might succeed-with-nothing.

It runs through `bash -c` with the repo root as the working directory.

```json
"probe": "GH_HOST=git.example.com gh auth status 2>&1 | grep -m1 'Logged in to git.example.com' || echo FAIL",
"probe_ok": "Logged in"
```

```json
"probe": "zsh -ic 'print -r -- \"tok=${#SERVICE_API_TOKEN}\"' 2>/dev/null | tail -1",
"probe_ok": "tok=(?!0\\b)\\d+"
```

That second one is the pattern worth copying: an interactive shell is the only way to see what the
environment actually holds — the agent's own environment is not the one cron and scripts get — and
the regex insists on a non-zero length, so an unset variable fails instead of matching `tok=0`.
Remember the JSON escaping: `\\b` in the file is `\b` in the regex.

A probe that cannot exist is `null`, not a fake. An OAuth MCP connector has nothing checkable from
the shell; it reports on `connected_now` plus its transcript history, and that is honest.

## How status is decided

In order, first match wins:

1. a probe ran and failed → **broken**
2. `connected_now: false` → **broken** if it also has a probe, otherwise **disconnected**
3. the most recent call failed, or it fails at least half the time → **degraded**
4. never called, but a probe passed → **healthy**; never called and no probe → **idle**
5. otherwise → **healthy**

Then one pass over the whole set: anything healthy or idle whose `depends_on` names a broken or
disconnected entry is downgraded to **degraded**, with the dependency named in the reason.

## Adding a tool, end to end

1. If it is a CLI the scanner does not recognise, add a regex to `CLI_PATTERNS` in `scan.py`.
2. Append an object to `tools`. Fill every field; write `fix` as if for somebody who has never
   seen the tool.
3. Wire the graph: give it `depends_on` ids, and add `ref` to any alternative that is another entry.
   Check the reverse direction too — if your new tool is somebody's fallback, add the `ref` there.
4. Refresh the page. Confirm the probe output says what you expected, and that the call count is
   not zero if you know the tool has been used (a zero means `usage_keys` is not matching).

## What does not belong here

Secrets, obviously, including inside probe commands — reference the file that holds them
(`~/.config/<service>/env`), never the value. And check where the registry gets committed before
naming employers, clients or engagements in it. It is a map of somebody's access: useful to them,
and useful to anyone else who reads it.
