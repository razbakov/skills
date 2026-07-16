---
description: "Install a self-hosted / community MCP server on macOS and make it durable — clone, build (fixing stale pinned deps that break at runtime), register in BOTH Claude Code and the Claude desktop app, handle interactive auth (QR/OAuth), and if it has a long-running daemon, wrap it in a launchd service. Use when the user asks to install a local/community MCP server (e.g. a GitHub project like lharries/whatsapp-mcp), especially one with a background bridge/daemon that must survive reboots."
user_invocable: true
---

# Install a Local MCP Service

Install a self-hosted MCP server (typically a community project cloned from GitHub) and make it **durable**: registered in every Claude surface the user actually uses, authenticated, and — if it ships a long-running daemon — supervised so it survives reboots.

This is the "stdio MCP + optional background bridge" pattern. Many community MCP servers are two parts: a **server** (stdio, spawned on demand by the client) and a **bridge/daemon** (a long-running process that maintains a session and syncs state to a local DB). The server is easy; the bridge is what people forget to make durable.

**Platform**: written for **macOS** (launchd, `open`, `~/Library/Application Support/Claude/`). On Linux the shape is identical but swap launchd for a systemd user unit (`~/.config/systemd/user/`, `systemctl --user enable --now`) and drop the desktop-app config step.

## When to use

- "install `<github-owner/repo>` MCP", "set up the WhatsApp/Signal/iMessage/etc. MCP", "add a local MCP server".
- Especially when the project has a persistent bridge/daemon (a linked session, a local SQLite cache, a QR/OAuth login).

## When NOT to use

- claude.ai remote connectors (OAuth-based, added via the connector settings UI) — those aren't self-hosted.
- A one-shot `npx`-style stdio server with no auth and no daemon — just `claude mcp add` it directly; you don't need this whole procedure.

## Procedure

### 1. Check prerequisites

Read the project's README for its toolchain, then verify each is installed:

```bash
which go python3 uv node ffmpeg git 2>&1   # only the ones the README needs
```

Install missing ones with `brew` before continuing. Don't proceed on a missing toolchain — the build will fail confusingly later.

### 2. Clone and build

Clone into `~/Projects/<repo>` (code lives in Projects, per orgs-vs-projects rule). Build the server/bridge to **cache all dependencies up front** so the first real run is instant, and to surface build errors now:

```bash
cd ~/Projects && git clone --depth 1 <repo-url> && cd <repo>
# Go bridge:      go build -o <binary> main.go
# Python server:  (cd <server-dir> && uv sync)
```

### 3. Fix stale pinned dependencies (the most common failure)

**Community projects pin dependencies that rot.** The classic symptom: the build succeeds, the process starts, but the remote service **rejects the connection immediately** (e.g. a websocket `1006` close, an auth handshake failure, a `426 Upgrade Required`). This is almost always an **outdated client library** — the vendored/pinned version is months old and the server no longer speaks its protocol.

Fix: bump the offending library to latest and rebuild.

```bash
# Go example:
go get <module>@latest && go mod tidy && go build -o <binary> main.go
```

A dependency bump usually adds new required params (e.g. a `context.Context` first arg on several methods). Read the compile errors and patch each call site — they're mechanical. **Record which lib you bumped and which call sites you patched** in the durable notes (step 7) so a future rebuild doesn't silently regress to the broken pin.

Worked example — `lharries/whatsapp-mcp`: the pinned `go.mau.fi/whatsmeow` (March 2025) was rejected by WhatsApp with a `1006` handshake close and never emitted a QR. Bumping whatsmeow to latest + adding `context.Background()` to 5 call sites (`Download`, `sqlstore.New`, `GetFirstDevice`, `GetGroupInfo`, `GetContact`) fixed it.

### 4. Register in EVERY Claude surface the user uses

Register in **both** — the user's daily surface is often the desktop app, but Claude Code is where you're working:

**Claude Code** (user scope, so it's available in all projects):

```bash
claude mcp add <name> -s user -- <command> <args...>
claude mcp get <name>    # verify it shows Connected
```

**Claude desktop app** — merge into `~/Library/Application Support/Claude/claude_desktop_config.json`. **Read it first and add to the existing `mcpServers` object** (never clobber existing servers). This file is strict JSON that the app parses on launch — a stray comma or a missing brace silently disables **every** MCP server in the desktop app, so keep the edit surgical and re-read to confirm it still parses. A desktop-app restart is required for it to pick up; Claude Code picks up user-scope servers in any new session with no restart.

Command shape for a `uv`-run Python server:
`command`: absolute path to `uv` (`which uv`), `args`: `["--directory", "<abs server dir>", "run", "main.py"]`.

### 5. Handle interactive auth (QR / OAuth login)

If the bridge needs a one-time login, the user usually can't read a terminal-rendered QR. **Render it as a scannable image and open it:**

- Patch the bridge to also print the **raw** auth-code string (many only draw terminal half-blocks).
- Capture it from the bridge log, generate a PNG (`uvx segno "<code>" --output=<path>.png --scale=10 --border=3`), and `open` it.
- These codes **rotate** (~20-30s) and the pairing window **times out** (~3 min). Write a small resilient helper that keeps the PNG refreshed with the latest code **and auto-restarts the bridge if the window expires**, exiting when the log shows a success line. Save it as `<repo>/<name>-link.sh` so re-auth later is one command. (See `assets/qr-link.sh.example` for the shape.)
- Detect success from the bridge log AND verify in the DB (e.g. a session/device row exists) — a log-pattern match alone can lie.

For OAuth-based local servers, the flow is browser-based; just run the server's documented `login` command and let the user complete it.

### 6. Make a long-running bridge durable (launchd)

If there's a persistent daemon, a manually-started process dies on reboot and stops syncing. Wrap it in a **launchd user agent**:

- Write `~/Library/LaunchAgents/<label>.plist` with `KeepAlive=true`, `RunAtLoad=true`, a `ThrottleInterval` (~30s so a crash loop doesn't hammer the remote), `WorkingDirectory` set to the bridge dir (bridges often use **relative** DB paths), and `StandardOutPath`/`StandardErrorPath` to a log.
- Keep a **source copy of the plist in the org repo** (`<org>/.bin/`) so it's versioned.
- **Stop the manual process first** (two writers on one SQLite file corrupts it), then `launchctl bootstrap gui/$(id -u) <plist>` and `launchctl kickstart -k` it. Confirm it reconnected **without** re-auth (the session persists in the local store).
- **Document the job** in the user's scheduled-automations inventory (the canonical table in their private CLAUDE.md) — an undocumented background job is invisible when it later misbehaves. Include the re-auth command and the dependency-bump note from step 3.

### 7. Verify end-to-end and record durable notes

- Call an actual MCP **read** tool and confirm it returns real data (not just "Connected" — a server can spawn fine but return nothing because the bridge isn't authed/synced).
- If it syncs history, note that initial sync is often **partial** (only recent/active data); don't promise full backfill.
- Leave the durable notes (bumped lib, patched call sites, re-auth command, log path, ToS caveat if it's a reverse-engineered client) in the automations inventory or the org CLAUDE.md.

## Caveats to surface to the user

- **ToS**: reverse-engineered clients (WhatsApp, iMessage, etc.) violate the vendor's ToS. Low practical risk for personal use, but say so.
- **The lethal trifecta**: a local MCP with private data + tool access + exposure to untrusted content can exfiltrate. Flag it for servers that read untrusted messages.
- **Interactive steps stay with the user**: the QR scan / OAuth grant is theirs to do.

## Inputs / Outputs

- **Input**: a GitHub repo (or local path) for an MCP server; the user's confirmation for any auth step.
- **Output**: the server registered + Connected in Claude Code and the desktop app; the bridge (if any) running under launchd and documented; a one-command re-auth helper; an end-to-end read verified.
