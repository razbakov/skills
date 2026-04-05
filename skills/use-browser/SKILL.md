---
name: use-browser
description: Meta skill for browser automation — routes to the right browser tool. Use when you need to automate a browser task and aren't sure which MCP toolset to use (Claude in Chrome vs chrome-devtools vs agent-browser CLI). Also use when writing prompts for agents that need browser access, or when deciding between browser automation approaches.
---

# Browser Automation — Which Tool?

Three browser automation toolsets are available. All three connect to the user's actual Chrome with cookies and session state intact.

## Decision Matrix

| Need | Use | Skill |
|------|-----|-------|
| Authenticated page (logged in) | Claude in Chrome OR chrome-devtools | `/use-browser-claude-in-chrome` or `/use-browser-chrome-devtools` |
| Run JS with user's cookies | Either MCP tool — both work | Both have `credentials: 'include'` |
| Lighthouse / performance audit | chrome-devtools | `/use-browser-chrome-devtools` |
| Network request inspection | chrome-devtools | `/use-browser-chrome-devtools` |
| Device/viewport emulation | chrome-devtools or agent-browser | `/use-browser-chrome-devtools` or `/agent-browser` |
| Natural language element search | Claude in Chrome | `/use-browser-claude-in-chrome` — `find("login button")` |
| Screenshot-based interaction | Claude in Chrome | `/use-browser-claude-in-chrome` — coordinate clicks |
| Batch form filling | chrome-devtools | `/use-browser-chrome-devtools` — `fill_form()` |
| GIF recording of actions | Claude in Chrome | `/use-browser-claude-in-chrome` — `gif_creator` |
| Headless / CLI automation | agent-browser | `/agent-browser` |
| Auth with state persistence | agent-browser | `/agent-browser` — `state save/load`, `--session-name` |
| Parallel browser sessions | agent-browser | `/agent-browser` — `--session agent1` / `--session agent2` |
| Iframe interaction | agent-browser | `/agent-browser` — auto-inlines iframe content in snapshots |
| Memory heap analysis | chrome-devtools | `/use-browser-chrome-devtools` |
| Visual diff / regression test | agent-browser | `/agent-browser` — `diff snapshot`, `diff screenshot` |
| Network HAR recording | agent-browser | `/agent-browser` — `network har start/stop` |

## Quick Comparison

| Feature | Claude in Chrome | chrome-devtools | agent-browser CLI |
|---------|-----------------|-----------------|-------------------|
| Connects to user's Chrome | Yes (extension) | Yes (DevTools Protocol) | Own Chromium (or `--auto-connect`) |
| Has user's cookies/session | Yes | Yes | Via `--auto-connect`, `--state`, or `--session-name` |
| Element refs | `ref_1`, `ref_2` | `uid` (e.g. `e42`) | `@e1`, `@e2` |
| JS execution | `javascript_tool` (raw code) | `evaluate_script` (function wrapper) | `agent-browser eval` |
| Needs tabId per call | Yes | No (uses selected page) | No (single session) |
| Performance tracing | No | Yes | Yes (`profiler start/stop`) |
| Lighthouse | No | Yes | No |
| Network body inspection | No | Yes (full req/res) | Yes (`network requests`, HAR) |
| Device emulation | No | Yes | Yes (`set device`, `set viewport`) |
| Natural language find | Yes (`find`) | No | Yes (`find text/label/role`) |
| Auth state persistence | No | No | Yes (`state save/load`, `--session-name`, auth vault) |
| Parallel sessions | No | No | Yes (`--session name`) |
| Visual diffing | No | No | Yes (`diff snapshot`, `diff screenshot`) |
| Iframe support | Limited | Limited | Auto-inlined in snapshots |
| Annotated screenshots | No | No | Yes (`screenshot --annotate`) |
| Works without MCP | No | No | Yes (CLI via Bash) |

## For Agent Prompts

When writing a prompt for an agent that needs browser access, include this pattern:

### Claude in Chrome pattern:
```
Browser: use mcp__Claude_in_Chrome__ tools
1. tabs_context_mcp(createIfEmpty: true) → get tabId
2. navigate(url, tabId) → load page
3. read_page(tabId) → get element refs
4. javascript_tool(action: 'javascript_exec', text: '<code>', tabId) → run JS with cookies
```

### chrome-devtools pattern:
```
Browser: use mcp__chrome-devtools__ tools
1. list_pages() → find page, or new_page(url) → open one
2. select_page(pageId) → set active page
3. take_snapshot() → get element uids
4. evaluate_script(function: '() => { return ... }') → run JS with cookies
```

### agent-browser CLI pattern:
```
Browser: use agent-browser CLI via Bash (see /agent-browser skill for full reference)
1. agent-browser open <url>
2. agent-browser snapshot -i → get refs (@e1, @e2)
3. agent-browser click @e1 / fill @e1 "value"
4. agent-browser eval "document.title"

For authenticated pages:
- agent-browser --auto-connect open <url>           → use user's running Chrome
- agent-browser --session-name myapp open <url>      → persistent session with cookies
- agent-browser state load auth.json && agent-browser open <url>  → saved auth state
```

## Rule of Thumb

- **Default to Claude in Chrome** — simplest MCP API, natural language `find`, works for most tasks
- **Use chrome-devtools when** you need Lighthouse, performance traces, network body inspection, or device emulation
- **Use agent-browser CLI when** you need headless automation, parallel sessions, auth state persistence, visual diffing, or the MCP tools aren't available
- **agent-browser can also connect to user's Chrome** via `--auto-connect` — it's not limited to fresh sessions
