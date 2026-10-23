#!/usr/bin/env python3
"""Scan Claude Code transcripts and aggregate per-tool usage / failure facts.

Reads every ~/.claude/projects/*/*.jsonl, and emits one record per tool
(MCP tool, built-in tool, Skill, and Bash-invoked CLI) with:
  calls, errors, last_used, last_error, last_error_text, sessions, projects.
Pure read-only. No network.
"""
import json, os, re, sys, glob
from collections import defaultdict

STORE = os.path.expanduser("~/.claude/projects")

# CLI binaries we care about when they show up inside a Bash command.
# The CLIs worth attributing, matched against the whole Bash command. This is a starter set:
# add your own for anything you reach for often, and for every shell-script wrapper around a
# credential (a `*-query.sh`, a `deploy.sh`) — those are exactly the paths that rot unnoticed.
CLI_PATTERNS = {
    "git":        r"\bgit\s",
    "gh":         r"\bgh\s",
    "docker":     r"\bdocker\s",
    "kubectl":    r"\bkubectl\s",
    "terraform":  r"\bterraform\s",
    "psql":       r"\bpsql\s",
    "npm":        r"\bnpm\s",
    "pnpm":       r"\bpnpm\s",
    "yarn":       r"\byarn\s",
    "bun":        r"\bbun\s",
    "ssh":        r"\bssh\s",
    "aws":        r"\baws\s",
    "gcloud":     r"\bgcloud\s",
    "launchctl":  r"\blaunchctl\s",
    "systemctl":  r"\bsystemctl\s",
}

CLI_RE = {k: re.compile(v) for k, v in CLI_PATTERNS.items()}


def blank():
    return {"calls": 0, "errors": 0, "last_used": None, "last_error": None,
            "last_error_text": None, "last_session": None, "last_project": None,
            "last_error_session": None, "last_error_project": None,
            "sessions": set(), "projects": set(), "sidechain_calls": 0,
            "agents": defaultdict(int)}


def flatten(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out = []
        for c in content:
            if isinstance(c, dict):
                out.append(c.get("text") or c.get("content") or "")
            else:
                out.append(str(c))
        return " ".join(x if isinstance(x, str) else json.dumps(x) for x in out)
    return json.dumps(content) if content else ""


def main():
    tools = defaultdict(blank)
    # tool_use_id -> (toolname, extra ids)
    pending = {}
    files = sorted(glob.glob(os.path.join(STORE, "*", "*.jsonl")))
    sidechain_agent = {}   # sessionId -> last seen subagent_type (best effort)

    for path in files:
        project = os.path.basename(os.path.dirname(path))
        with open(path, errors="replace") as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                typ = d.get("type")
                if typ not in ("assistant", "user"):
                    continue
                ts = d.get("timestamp")
                sess = d.get("sessionId")
                cwd = d.get("cwd") or project
                side = bool(d.get("isSidechain"))
                msg = d.get("message") or {}
                content = msg.get("content")
                if not isinstance(content, list):
                    continue
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    btype = block.get("type")
                    if btype == "tool_use":
                        name = block.get("name") or "?"
                        inp = block.get("input") or {}
                        ids = [name]
                        if name == "Skill":
                            ids.append("skill:" + str(inp.get("skill")))
                        if name in ("Agent", "Task"):
                            st = inp.get("subagent_type") or "general-purpose"
                            ids.append("agent:" + str(st))
                            if sess:
                                sidechain_agent[sess] = st
                        if name == "Bash":
                            cmd = inp.get("command") or ""
                            for cli, rx in CLI_RE.items():
                                if rx.search(cmd):
                                    ids.append("cli:" + cli)
                        for tid in ids:
                            r = tools[tid]
                            r["calls"] += 1
                            if side:
                                r["sidechain_calls"] += 1
                            if sess:
                                r["sessions"].add(sess)
                            r["projects"].add(cwd)
                            if ts and (r["last_used"] is None or ts > r["last_used"]):
                                r["last_used"] = ts
                                r["last_session"] = sess
                                r["last_project"] = cwd
                        pending[block.get("id")] = (ids, ts, sess, cwd)
                    elif btype == "tool_result":
                        if not block.get("is_error"):
                            continue
                        ent = pending.get(block.get("tool_use_id"))
                        if not ent:
                            continue
                        ids, uts, usess, ucwd = ent
                        text = flatten(block.get("content"))[:600]
                        when = ts or uts
                        for tid in ids:
                            r = tools[tid]
                            r["errors"] += 1
                            if when and (r["last_error"] is None or when > r["last_error"]):
                                r["last_error"] = when
                                r["last_error_text"] = text
                                r["last_error_session"] = usess
                                r["last_error_project"] = ucwd

    out = {}
    for k, v in tools.items():
        out[k] = {
            "calls": v["calls"], "errors": v["errors"],
            "last_used": v["last_used"], "last_error": v["last_error"],
            "last_error_text": v["last_error_text"],
            "last_session": v["last_session"], "last_project": v["last_project"],
            "last_error_session": v["last_error_session"],
            "last_error_project": v["last_error_project"],
            "session_count": len(v["sessions"]),
            "sidechain_calls": v["sidechain_calls"],
        }
    json.dump({"tools": out, "transcripts": len(files)}, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
