---
name: envoy-connect
description: Connect a Telegram bot to any Claude Code agent for collaborative group chats. Use when the user wants to set up a Telegram chat where external people (co-founders, partners, clients) can interact with an AI agent. Triggers include "connect bot to agent", "set up group chat with agent", "add person to agent chat", "envoy connect", or when creating collaborative Telegram groups with AI agents.
---

# Envoy Connect — Link Any Claude Code Agent to a Telegram Chat

Connect a Telegram bot to any Claude Code agent, enabling collaborative group chats where multiple people interact with an AI agent that has full access to the project.

## Concept

A single Telegram bot serves as a universal gateway to your agent system:

- **Agent Mode**: Any chat (group or private) can be linked to a Claude Code agent running in a specific project directory, with a per-chat allow list controlling who can interact.
- **Envoy Mode** (optional): Outbound agenda-driven conversations with external contacts via deep links.

Both modes coexist on the same bot.

## Prerequisites

Before running this skill, ensure the user has:

1. A **Telegram bot** created via [@BotFather](https://t.me/BotFather) with its token stored in an env file
2. An **org/project directory** with Claude Code agent definitions in `.claude/agents/`
3. **Claude Code CLI** (`claude`) installed and available in PATH
4. **tmux** installed (`brew install tmux` or equivalent)
5. Python packages: `python-telegram-bot`, `anthropic`, `python-dotenv`

## Setup

### Step 1: Check if the Envoy bot infrastructure exists

Look for the bot script and send script. The bot needs two components:

1. **Bot script** — long-running process that receives Telegram messages and routes them to Claude Code agent sessions via tmux
2. **Send script** — small CLI that agents use to reply back to Telegram chats

Check for these in the project's `.bin/` or scripts directory. If they don't exist, create them using the architecture below.

### Step 2: Check environment configuration

The bot needs these environment variables (typically in `~/.config/telegram/.env` or project-level `.env`):

```
BOT_TOKEN=<telegram bot token from BotFather>
OWNER_TELEGRAM_ID=<admin user's Telegram ID>
```

To find a Telegram user ID:
- Ask the person to message `@userinfobot` — it replies with their ID
- Have the person send `/start` to the bot in private — check logs for their user ID
- Forward a message from the person to `@userinfobot`

### Step 3: Register orgs/projects

The bot needs a mapping of org names to filesystem paths where `claude --agent <name>` will run. This can be:
- A hardcoded dict in the bot script (simplest)
- A JSON config file (more flexible)
- Auto-discovered from a known parent directory (e.g., `~/Orgs/`)

Each org/project must have `.claude/agents/<agent-name>.md` files.

### Step 4: Guide the user through Telegram setup

Tell the user:

1. Create a Telegram group (or use an existing one)
2. Add the bot to the group
3. Add the other person to the group
4. In the group, send: `/connect <org> <agent>`
5. Then: `/allow <person_telegram_id>`
6. Verify with: `/status`

## Architecture

```
Telegram Group (User A + User B + Bot)
    |
    v
Bot script (long-running Python process)
    |
    +-- reads chat config (JSON file)
    +-- checks allow list (is sender permitted?)
    +-- routes message to AgentSession
            |
            v
        tmux window running: claude --agent <agent>
        working directory: <org/project path>
            |
            v
        Agent reads project files, runs tools, etc.
        Agent replies via send script --chat <chat_id> "message"
```

### Key components:

**Chat config** (`envoy-chats.json`):
```json
{
  "chats": {
    "<chat_id>": {
      "org": "<org-name>",
      "org_path": "<absolute path>",
      "agent": "<agent-name>",
      "allowed_users": [<user_id_1>, <user_id_2>]
    }
  }
}
```

**AgentSession** (tmux-based, same pattern as agent bot runners):
- Each connected chat gets a tmux window: `claude --agent <agent>` running in the org directory
- Messages are sent via `tmux load-buffer` / `paste-buffer` (handles special chars)
- Agent replies via the send script (fire-and-forget)
- Self-healing: TTL-based restart (every 4h), watchdog for unresponsive agents
- Messages tagged with `[chat_id:NUMBER,msg_id:NUMBER,from:NAME]` so agents can reply to the right chat

**Telegram reply instructions** (appended to agent's system prompt via `--append-system-prompt`):
- Agent must use Bash tool to call the send script — stdout doesn't reach Telegram
- React first (acknowledge), then reply
- Include `--chat <chat_id>` in every send command
- Plain text only (no markdown)

## Bot Commands

| Command | Who | What |
|---------|-----|------|
| `/connect <org> <agent>` | Admin only | Link this chat to an org agent |
| `/allow <user_id>` | Admin only | Add a user to the allow list |
| `/disconnect` | Admin only | Remove agent link, stop session |
| `/reset` | Admin only | Restart agent session (fresh context) |
| `/status` | Anyone | Show current chat configuration |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot not responding | Check if bot process is running. Restart if needed. |
| Agent not responding | `/reset` to restart tmux session. Check `tmux ls` for the session. |
| "Unknown org" | Add the org to the path registry in the bot script. |
| "Agent not found" | Verify `.claude/agents/<name>.md` exists in the org directory. |
| Messages ignored | User not in allow list. Admin must `/allow <user_id>`. |
| Agent replies to wrong chat | Ensure `--chat <chat_id>` is in the send script instructions. |

## Security Notes

- Only the admin (owner) can `/connect`, `/allow`, and `/disconnect`
- Messages from non-allowed users are silently ignored
- Each chat gets its own isolated Claude session (separate tmux window, separate context)
- Agent sessions run with `--dangerously-skip-permissions` for autonomous operation — ensure agents have proper boundary policies in their definitions
