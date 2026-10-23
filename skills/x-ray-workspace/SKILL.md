---
name: x-ray-workspace
description: X-ray the tools an agent reaches through — every MCP connector, CLI, credential and scheduled automation — and turn them into a registry with an owner, fallbacks, dependencies, a fix and a read-only health probe per entry, served as a live local dashboard with a card view and an access map. Use when the user asks what tools or integrations they have, which connectors are broken, dead or disconnected, why a scheduled job has silently stopped working, wants an inventory or dashboard of their MCPs and credentials, or says "x-ray my workspace", "tool registry", "access map", "what's broken in my setup".
compatibility: macOS or Linux with python3 (standard library only, no pip installs). Reads Claude Code session transcripts from ~/.claude/projects. Probes run through bash. No network access required or used.
---

# X-Ray Workspace

Access does not fail loudly. It fails on the path nobody is currently looking at: the credential
that works in your shell but is missing from cron's, the connector that quietly dropped out of
the list, the scheduled job whose binary was uninstalled two months ago. You find out when a
client opens a link, or when you notice a log that has been empty since August.

This skill builds the page that would have told you. One entry per tool, with the half a machine
can measure (calls, last use, last failure and its text, from the transcripts) kept separate from
the half only a person knows (owner, route, fallbacks, dependencies, fix), and a read-only probe
per entry so the page reports the machine as it is rather than as it was documented.

Everything needed ships in this folder. Resolve it once, and decide where the registry belongs in
the workspace you are x-raying:

```bash
SK=<this skill's directory>
REG=ops/toolsdash/registry.json      # the file you are writing, in the target workspace
```

**Read [`references/REGISTRY.md`](references/REGISTRY.md) before writing a single entry.** It is the authoritative
schema: every field, how `usage_keys` match the scanner, the rules a probe must obey, and how
status is decided. This file is the procedure; that one is the format. If they ever disagree,
`references/REGISTRY.md` wins.

## When this runs

- **Bootstrap** — no registry yet. Do all five steps. Start from `assets/registry.example.json`, which
  shows the shape in three entries. It is not a starting inventory: delete them and card what the
  workspace actually has.
- **Refresh** — it exists, but connectors changed or a tool was added. Steps 1, 4 and 5, plus
  step 3 for the entries you touched. Never rewrite an entry you did not verify.

## 1. Measure before you describe

Nothing enters the registry that is not grounded in evidence. Start with what actually happened:

```bash
python3 $SK/scripts/scan.py > /tmp/usage.json
python3 - <<'EOF'
import json
t=json.load(open('/tmp/usage.json'))['tools']
for k,v in sorted(t.items(), key=lambda x:-x[1]['calls']):
    if v['calls']>=2 or v['errors']:
        print(f"{v['calls']:5d} err={v['errors']:3d} {k[:72]} last={str(v['last_used'])[:16]}")
EOF
```

That ranking is the backbone of the registry: it says which tools are real rather than
aspirational, and the error counts say which to look at first. Pull `last_error_text` for anything
failing — that is what the `fix` field has to answer.

Then enumerate what exists, used or not:

| Source | What it gives you |
|---|---|
| this session's tool list and system reminders | which MCP servers are connected **right now** → `connected_now`, `meta.connected_verified` |
| `~/.claude.json` (`projects.*.mcpServers`), `./.mcp.json` | locally configured MCP servers |
| the workspace's own `CLAUDE.md` / `AGENTS.md` | credentials, CLIs, conventions, and the fix somebody already wrote down |
| agent definition files | which agent owns what → `owner_agent` |
| `ls ~/Library/LaunchAgents` + `launchctl list`, or `systemctl --user list-timers` | automations that are supposed to be running |
| `ls ~/.config/*`, `ls ~/.local/state/*` | host-local credential and state files |

A transcript id matching no `usage_keys` is a tool nobody has carded. Check that list before
calling the registry complete; `validate.py` prints it for you.

## 2. One entry per thing that can break

Not per MCP tool. A connector with forty tools is one entry whose `usage_keys` is the server
prefix. Forty cards would be noise, and the status would mean nothing.

Split a service in two only when the halves fail **independently**: a CLI authenticated against
two hosts is two entries, because either token can expire alone. Merge when they cannot —
`docker`, `psql` and the package managers are one "local dev infra" entry.

Card dead tools too, if they still appear in the transcripts. A retired connector with its 403
recorded saves the next person from diagnosing it again.

## 3. Probe what you can, then actually run it

Write probes to the rules in `references/REGISTRY.md`: read-only, under 20s, never printing a secret value.

**Run every probe by hand before it ships.** A wrong probe is worse than no probe. It reports a
working tool as broken, or — the expensive direction — a broken one as working.

Hunt specifically for the failure this exists to catch: **a tool that works interactively while
its unattended path is dead.** An OAuth connector and a shell credential for the same service are
two entries, and discovering the second one is gone is usually the whole value of the exercise.
Check the environment with an interactive shell (`zsh -ic`, `bash -ic`), not the agent's own,
which is not the environment cron and scripts get.

## 4. Wire the graph

Two fields turn a list into a map, and both want doing in **both directions**:

- `depends_on` — ids this tool genuinely needs. A broken dependency downgrades this tool to
  degraded, which is how "the scheduled job is green but the credential it needs is gone" surfaces.
- `alternatives[].ref` — the id of a fallback that is itself an entry. If A falls back to B, check
  whether B should name A.

Write `fix` last, with the probe output and the recorded failure text in front of you. Name the
command, the host, the file. "Re-authenticate" is not a fix.

## 5. Validate, then show it

```bash
python3 $SK/scripts/validate.py "$REG" --usage /tmp/usage.json
```

It checks that the JSON parses, every field is present and correctly typed, no id repeats, every
`depends_on` and `alternatives[].ref` resolves, and every `probe_ok` compiles. It warns about the
two mistakes that actually happen: a `usage_keys` prefix matching nothing in the transcripts
(a typo, usually), and a frequently used tool that no entry covers.

Then serve it. The server reads whichever registry you point it at:

```bash
TOOLSDASH_REGISTRY="$REG" python3 $SK/scripts/server.py     # http://localhost:3523, and /map
```

Two views on the same data: **cards** at `/`, filtered by status, and an **access map** at `/map`
drawn as a left-to-right flow — you → the agent that owns the tool → the tool → what it depends
on. Dashed edges are fallbacks, solid amber are hard dependencies, and clicking a box dims
everything it does not touch. Add it to `.claude/launch.json` so it starts through the preview
tooling rather than a stray background shell.

Report by exception: the counts, then what is broken and what the fix is. A list of thirty healthy
tools is not a finding.

## Guardrails

- **Never write a probe that changes anything.** No deploy, send, delete or write, even when the
  tool's entire purpose is writing. Check that the credential authenticates, not that it works.
- **Never put a secret in the registry**, including inside a probe command. Reference the file
  that holds it, never the value. The page renders probe output verbatim.
- **Think about where the registry is committed.** It is a map of somebody's access. Keep it in
  the workspace it describes, and out of anything public or shared more widely than the access is.
- **Do not invent status.** If nothing is checkable from this machine, `probe: null`, and say why
  in `notes`. A fabricated green is the one outcome worse than having no dashboard.
- **Do not fix what you find.** Discovering that a binary is gone and a scheduled job has been
  dead for weeks is the deliverable. Reinstalling it is a separate decision, and the owner's.
