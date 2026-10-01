#!/usr/bin/env python3
"""linear-agent.py — Claude Code as a native Linear agent (Linear Agent API, actor=app).

Delegate an issue to the agent, or @mention it in a comment, and Linear opens an agent
session and POSTs an AgentSessionEvent here. We acknowledge inside Linear's 10 s window,
then run Claude Code (headless) inside AGENT_WORKDIR, which finds the owning repo, does the work, opens the PR, and reports back. Progress
streams into the issue as agent activities; follow-up messages in the session resume the
same Claude conversation.

No human in the loop: delegation is the go signal; linear-merge merges green PRs.

Endpoints (behind a public tunnel → AGENT_PUBLIC_URL):
  GET  /install          → redirect to Linear OAuth (actor=app) to install the agent
  POST /github           → GitHub pull_request webhook → merge gate
  GET  /oauth/callback   → exchange code, store token
  POST /webhook          → AgentSessionEvent (signature-verified)
  GET  /health

Config: ~/.config/linear/agent.env — see the skill's SKILL.md for every key
Token:  ~/.config/linear/agent-token.json
State:  ~/.config/linear/agent-sessions.json  (agentSession id → claude session id)
Log:    ~/.config/linear/agent.log
"""
import hashlib
import hmac
import json
import os
import re
import subprocess
import sys
import threading
import time
import traceback
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

CFG_DIR = Path.home() / ".config" / "linear"
ENV_FILE = CFG_DIR / "agent.env"
TOKEN_FILE = CFG_DIR / "agent-token.json"
STATE_FILE = CFG_DIR / "agent-sessions.json"
LOG_FILE = CFG_DIR / "agent.log"
PUBLIC_URL = os.environ.get("AGENT_PUBLIC_URL", "")  # resolved from agent.env in env()
REDIRECT_URI = f"{PUBLIC_URL}/oauth/callback"
PORT = int(os.environ.get("LINEAR_AGENT_PORT", "5055"))

MAX_PARALLEL = 3
JOB_TIMEOUT = 90 * 60
PR_RE = re.compile(r"https://github\.com/[\w.-]+/[\w.-]+/pull/\d+")
TEAM_KEY = os.environ.get("LINEAR_TEAM_KEY", "")  # set in load_config
ISSUE_RE = re.compile(r"$^")  # issue-id regex, built from LINEAR_TEAM_KEY in load_config
# Repos whose PRs the app merges (GitHub webhook → /github + 15-min sweep).
REPOS: list[str] = []  # from AGENT_REPOS (comma-separated owner/repo) — see load_config()
TRACK_FILE = CFG_DIR / "agent-pr-issues.json"  # untracked PR url → its tracking issue
GATED_FILE = CFG_DIR / "agent-gated.json"   # "<pr>@<sha>" → verdict, so a head is gated once
active: set[str] = set()                     # issue identifiers with a running the agent/gate job
active_lock = threading.Lock()

slots = threading.BoundedSemaphore(MAX_PARALLEL)
WORKDIR = Path.home()
CLAUDE = "claude"
AGENT_NAME = "Agent"
OWNER_GH = ""
EXTRA_RULES = ""
state_lock = threading.Lock()


def log(msg: str) -> None:
    CFG_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a") as f:
        f.write(time.strftime("[%Y-%m-%d %H:%M:%S] ") + msg + "\n")


def env() -> dict:
    out = dict(os.environ)
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"')
    return out


def load_config() -> None:
    global PUBLIC_URL, REDIRECT_URI, WORKDIR, CLAUDE, AGENT_NAME, REPOS, OWNER_GH, EXTRA_RULES
    e = env()
    PUBLIC_URL = e.get("AGENT_PUBLIC_URL", PUBLIC_URL).rstrip("/")
    REDIRECT_URI = f"{PUBLIC_URL}/oauth/callback"
    WORKDIR = Path(os.path.expanduser(e.get("AGENT_WORKDIR", str(Path.home()))))
    CLAUDE = e.get("CLAUDE_BIN", str(Path.home() / ".local" / "bin" / "claude"))
    AGENT_NAME = e.get("AGENT_NAME", "Agent")
    REPOS = [r.strip() for r in e.get("AGENT_REPOS", "").split(",") if r.strip()]
    OWNER_GH = e.get("AGENT_OWNER_GITHUB", "")
    global TEAM_KEY, ISSUE_RE
    TEAM_KEY = e.get("LINEAR_TEAM_KEY", "ENG")
    os.environ["LINEAR_TEAM_KEY"] = TEAM_KEY
    os.environ["AGENT_HUMAN_LABEL"] = e.get("AGENT_HUMAN_LABEL", "commander")
    ISSUE_RE = re.compile(rf"\b{re.escape(TEAM_KEY)}-(\d+)\b", re.I)
    rules = e.get("AGENT_RULES_FILE", "")
    EXTRA_RULES = Path(os.path.expanduser(rules)).read_text() if rules and Path(os.path.expanduser(rules)).exists() else ""


# --------------------------------------------------------------------------- OAuth

def save_token(tok: dict) -> None:
    tok["obtained_at"] = int(time.time())
    TOKEN_FILE.write_text(json.dumps(tok, indent=2))
    TOKEN_FILE.chmod(0o600)


def token_request(form: dict) -> dict:
    e = env()
    form |= {"client_id": e["LINEAR_AGENT_CLIENT_ID"], "client_secret": e["LINEAR_AGENT_CLIENT_SECRET"]}
    req = urllib.request.Request("https://api.linear.app/oauth/token",
                                 data=urllib.parse.urlencode(form).encode(),
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def access_token() -> str:
    tok = json.loads(TOKEN_FILE.read_text())
    exp = tok.get("expires_in")
    if tok.get("refresh_token") and exp and time.time() > tok["obtained_at"] + exp - 300:
        new = token_request({"grant_type": "refresh_token", "refresh_token": tok["refresh_token"]})
        new.setdefault("refresh_token", tok["refresh_token"])
        new["app_user_id"] = tok.get("app_user_id")
        save_token(new)
        tok = new
        log("token refreshed")
    return tok["access_token"]


def gql(query: str, variables: dict | None = None) -> dict:
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": f"Bearer {access_token()}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if out.get("errors"):
        raise RuntimeError("; ".join(x.get("message", "?") for x in out["errors"]))
    return out["data"]


# --------------------------------------------------------------------------- Linear helpers

def activity(session_id: str, content: dict) -> None:
    try:
        gql("""mutation($i: AgentActivityCreateInput!) { agentActivityCreate(input: $i) { success } }""",
            {"i": {"agentSessionId": session_id, "content": content}})
    except Exception as ex:  # never let reporting kill the job
        log(f"activity failed ({content.get('type')}): {ex}")


def thought(sid, body): activity(sid, {"type": "thought", "body": body})
def response(sid, body): activity(sid, {"type": "response", "body": body})
def error(sid, body): activity(sid, {"type": "error", "body": body})


def add_external_urls(session_id: str, urls: list[str]) -> None:
    if not urls:
        return
    try:
        gql("""mutation($id: String!, $i: AgentSessionUpdateInput!) { agentSessionUpdate(id: $id, input: $i) { success } }""",
            {"id": session_id, "i": {"addedExternalUrls": [{"label": u.split("github.com/")[1], "url": u} for u in urls]}})
    except Exception as ex:
        log(f"externalUrls failed: {ex}")


def set_state(issue_id: str, name: str) -> None:
    try:
        d = gql("""query($id: String!) { issue(id: $id) { team { states { nodes { id name } } } } }""", {"id": issue_id})["issue"]
        sid = next(s["id"] for s in d["team"]["states"]["nodes"] if s["name"] == name)
        gql("""mutation($id: String!, $s: String!) { issueUpdate(id: $id, input: {stateId: $s}) { success } }""",
            {"id": issue_id, "s": sid})
    except Exception as ex:
        log(f"set_state {name} failed: {ex}")


def move_to_started(issue_id: str) -> None:
    """In Progress = locked: linear-dispatch only scans Todo, linear-merge reviews In Progress PRs."""
    try:
        d = gql("""query($id: String!) { issue(id: $id) { state { type } team { states { nodes { id name type } } } } }""",
                {"id": issue_id})["issue"]
        if d["state"]["type"] in ("started", "completed", "canceled"):
            return
        sid = next(s["id"] for s in d["team"]["states"]["nodes"] if s["name"] == "In Progress")
        gql("""mutation($id: String!, $s: String!) { issueUpdate(id: $id, input: {stateId: $s}) { success } }""",
            {"id": issue_id, "s": sid})
    except Exception as ex:
        log(f"move_to_started failed: {ex}")


def load_state() -> dict:
    with state_lock:
        return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}


def save_state_entry(agent_session: str, entry: dict) -> None:
    with state_lock:
        s = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
        s[agent_session] = {**s.get(agent_session, {}), **entry}
        STATE_FILE.write_text(json.dumps(s, indent=2))


# --------------------------------------------------------------------------- the work

BRIEF = """You are **{agent}**, running as a native Linear agent. Someone delegated this to you in Linear. Delegation IS the approval — no human in the loop, do not stop to ask
for permission. Release consciously: verify, then ship; if something breaks later we trace back and fix.

{context}

## How to work
- Issue: {identifier} — {url}. Branch (use exactly this so the PR links): `{branch}`.
- Find the repo via the instructions (CLAUDE.md) in your working directory. Work in the foreground — never
  background a sub-agent and report work that isn't done.
- If the issue has a `Merge gate · RED` comment, your job is to fix exactly what it lists ON THE EXISTING PR
  (push to the same branch, never open a second PR), resolve the threads you addressed, and say what you fixed.
- If the request is a question, answer it. If it is work, do it end to end and open a PR (or push to the
  existing PR on that branch). Don't merge it yourself — the runtime runs the merge gate right after you finish.
- Quality bar (the merge gate rejects these every time): no AI attribution in PR body or commit trailers;
  rebase on the default branch and run the FULL test suite (report command + exit code); for web work verify
  the change on its preview/live URL (never print secrets);
  resolve review threads you addressed; cite file:line for every requirement; claim nothing unverified.
- If a decision is genuinely ambiguous, pick the most reasonable option, state the assumption in the PR, ship.
- If only a human can unblock something, create a blocker ticket (`python3 {scripts}/linear.py blocker --for {identifier} --title … --do \"step|step\" --summary …`) — never ask in a comment.
- NEVER run `linear.py approve|drop|done` — those are the owner's verbs. Don't change the issue state yourself; the runtime does it.

{extra}
Linear is read by humans: never post your own status/done comments on Linear — the runtime renders your final
answer into a clean message. Put evidence in the GitHub PR, not Linear.
End your answer with ONE JSON object on its own lines (nothing after it). Fields:
{{"status": "merged" | "fixing" | "answered" | "done",
 "headline": "<what changed or what's wrong — plain language a non-developer understands, ≤12 words>",
 "live_url": "<production URL where the change is visible, or empty>",
 "steps": ["Open <URL>", "Click <…>", "You should see <…>"],   // for a USER on the LIVE product; never GitHub/PR/files/CI; [] if nothing user-visible
 "internal": "<if nothing user-visible: what kind of change, e.g. 'docs only'; else empty>",
 "answer": "<question-only issues: the answer, 1–3 sentences; else empty>",
 "followups": ["ENG-…"]}}"""


def summarize_tool(name: str, inp: dict) -> tuple[str, str]:
    if name == "Bash":
        return "Ran", (inp.get("description") or inp.get("command", ""))[:200]
    if name in ("Edit", "Write", "Read"):
        return {"Edit": "Edited", "Write": "Wrote", "Read": "Read"}[name], str(inp.get("file_path", ""))[-160:]
    if name == "Agent":
        return "Delegated", f"{inp.get('subagent_type', 'agent')}: {inp.get('description', '')}"
    return name, json.dumps(inp)[:160]


def run_claude(session_id: str, prompt: str, resume: str | None, issue_id: str = "", record: bool = True) -> tuple[str, list[str]]:
    cmd = [CLAUDE, "-p", prompt, "--output-format", "stream-json", "--verbose",
           "--dangerously-skip-permissions", "--model", "opus"]
    if resume:
        cmd += ["--resume", resume]
    log(f"[{session_id}] claude start (resume={resume})")
    proc = subprocess.Popen(cmd, cwd=WORKDIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            env={**os.environ, "PATH": f"/opt/homebrew/bin:/usr/local/bin:{Path.home()}/.local/bin:" + os.environ.get("PATH", "")})
    timer = threading.Timer(JOB_TIMEOUT, proc.kill)
    timer.start()
    last_post, result, claude_sid = 0.0, "", None
    try:
        for line in proc.stdout:
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("session_id") and not claude_sid:
                claude_sid = ev["session_id"]
                if record:
                    save_state_entry(session_id, {"claude_session": claude_sid})
            if ev.get("type") == "assistant":
                for block in ev.get("message", {}).get("content", []):
                    # throttle: at most one progress activity per 20 s
                    if block.get("type") == "tool_use" and time.time() - last_post > 20:
                        act, param = summarize_tool(block.get("name", ""), block.get("input") or {})
                        activity(session_id, {"type": "action", "action": act, "parameter": param})
                        last_post = time.time()
            if ev.get("type") == "result":
                result = ev.get("result") or ""
                if ev.get("is_error"):
                    raise RuntimeError(result or ev.get("subtype", "claude error"))
        proc.wait()
    finally:
        timer.cancel()
    if proc.returncode not in (0, None) and not result:
        raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr.read()[-800:]}")
    prs = list(dict.fromkeys(PR_RE.findall(result)))
    log(f"[{session_id}] claude done; PRs={prs}")
    return result.strip(), prs



GATE = """You are the **merge gate** for Linear issue {ident}, PR {pr}.
**a task is done only when its PR is merged. Every PR gets merged.**
The gate's job is to get it merged safely, not to judge it. Read the issue: `python3 {scripts}/linear.py issue {ident}`.

If checks are still running, wait: `timeout 900 gh pr checks <n> --watch`.
BLOCKING (the only reasons not to merge yet — each breaks main or makes the merge meaningless):
  a. merge conflicts / not mergeable → report "rebase needed";
  b. required CI or the build fails on the PR head (`gh pr checks`; if the repo has no CI, run its install+build in a
     clean checkout with `timeout 600`) → report the failing check and error;
  c. the PR is a no-op / fully superseded by main → close it: `gh pr close <n> --comment "Superseded: delivered on main"`,
     treat as MERGED.
NOT BLOCKING — merge anyway, then file each leftover as ONE follow-up issue
(`python3 {scripts}/linear.py create --title "<{ident} follow-up: …>" --project <same project> --body "<what, file:line, from PR {pr}>"`):
  unresolved review threads, partially met requirements, conventions, missing preview evidence, reserved classes
  (money/legal/governance/infra — just name the class in the comment).
Merge: `gh pr merge <n> --squash --delete-branch` (repo's method if squash is disabled); verify state=MERGED.
Put the full check-by-check evidence in ONE GitHub PR comment (`gh pr comment <n> --body …`). Do NOT comment on Linear —
the runtime renders your result. Use status "merged" or "fixing" (fixing = blocked: headline is the blocking reason).
End your answer with ONE JSON object on its own lines (nothing after it). Fields:
{{"status": "merged" | "fixing" | "answered" | "done",
 "headline": "<what changed or what's wrong — plain language a non-developer understands, ≤12 words>",
 "live_url": "<production URL where the change is visible, or empty>",
 "steps": ["Open <URL>", "Click <…>", "You should see <…>"],   // for a USER on the LIVE product; never GitHub/PR/files/CI; [] if nothing user-visible
 "internal": "<if nothing user-visible: what kind of change, e.g. 'docs only'; else empty>",
 "answer": "<question-only issues: the answer, 1–3 sentences; else empty>",
 "followups": ["ENG-…"]}}
Never push to the branch and never change the issue state. No dev servers or watchers.
Your LAST line must be exactly `VERDICT: MERGED` or `VERDICT: RED — <the blocking reason, one line>`."""

# --------------------------------------------------------------------------- one template for every human message

ICON = {"merged": "✅ Done", "done": "✅ Done", "answered": "💬 Answer", "fixing": "🔧 Fixing"}


def parse_result(text: str) -> dict:
    """Last JSON object in the model's answer; {} if none (then we fall back to plain text)."""
    for m in reversed(list(re.finditer(r"\{[\s\S]*\}", text))):
        try:
            d = json.loads(m.group(0))
            if isinstance(d, dict) and "status" in d:
                return d
        except json.JSONDecodeError:
            continue
    return {}


def render(d: dict, pr: str = "", fallback: str = "") -> str:
    if not d:
        return fallback.strip()[:900] or (f"✅ Done — {pr}" if pr else "✅ Done")
    st = d.get("status", "done")
    out = [f"### {ICON.get(st, '✅ Done')} — {d.get('headline', '').strip() or 'update'}", ""]
    if st == "answered":
        out.append(d.get("answer", "").strip())
        return "\n".join(out).strip()
    if st == "fixing":
        out.append("Fixing now — no action needed.")
        if pr:
            out += ["", f"**PR:** {pr}"]
        return "\n".join(out).strip()
    if d.get("live_url"):
        out.append(f"**Live:** {d['live_url']}")
    if pr:
        out.append(f"**PR:** {pr}")
    steps = [x.strip() for x in d.get("steps") or [] if x.strip()]
    out.append("")
    if steps:
        out.append("**Try it**")
        out += [f"{n}. {x}" for n, x in enumerate(steps, 1)]
    else:
        out.append(f"Nothing to try — internal change ({d.get('internal') or 'no user-visible effect'}).")
    if d.get("followups"):
        out += ["", "**Follow-ups:** " + ", ".join(d["followups"])]
    return "\n".join(out).strip()


MAX_FIX_ROUNDS = 5


def ship(sid: str, ident: str, issue_id: str, pr: str) -> None:
    """Gate → merge → Done, or RED → the agent fixes the same PR (resumed session) → re-gate."""
    for rnd in range(MAX_FIX_ROUNDS + 1):
        activity(sid, {"type": "action", "action": "Merge gate", "parameter": pr.rsplit("/", 1)[-1]})
        out, _ = run_claude(sid, GATE.format(ident=ident, pr=pr, scripts=Path(__file__).parent), None, record=False)
        verdict = next((l for l in reversed(out.splitlines()) if l.startswith("VERDICT:")), "VERDICT: RED — gate returned no verdict")
        log(f"[{sid}] {ident} gate round {rnd}: {verdict}")
        if verdict.startswith("VERDICT: MERGED"):
            set_state(issue_id, "Done")
            response(sid, render(parse_result(out), pr, out))
            return
        if rnd == MAX_FIX_ROUNDS:
            response(sid, f"Still not mergeable after {MAX_FIX_ROUNDS} fix rounds — {verdict[9:]}. Reply here to continue.")
            subprocess.run(["python3", str(Path(__file__).parent / "linear.py"), "blocker", "--for", ident,
                            "--title", f"Unstick {ident}: PR won't merge",
                            "--do", f"Open {pr}|Read the last 'Merge gate' comment on {ident}|Reply in the agent session on {ident} with how to proceed, or close the PR",
                            "--summary", f"the agent tried {MAX_FIX_ROUNDS} fix rounds and the PR is still not mergeable: {verdict[9:]}"])
            return
        thought(sid, f"🔧 Fixing — {verdict[11:]} ({rnd + 1}/{MAX_FIX_ROUNDS})")
        prev = load_state().get(sid, {}).get("claude_session")
        run_claude(sid, f"The merge gate ruled RED on {pr}:\n\n{out[-3000:]}\n\nFix every item on the SAME branch "
                        "(push to the existing PR), resolve the threads you addressed, then summarise. The only goal: make the PR mergeable (conflicts resolved, build/CI green).", prev, issue_id)


def finish(sid: str, ident: str, issue_id: str, result: str, prs: list[str]) -> None:
    add_external_urls(sid, prs)
    if not prs:
        if issue_id:
            set_state(issue_id, "Done")  # question / non-code work finished
        response(sid, render(parse_result(result), "", result))
        return
    thought(sid, "PR ready — merging.")
    save_state_entry(sid, {"forge_summary": result[:1500]})
    ship(sid, ident, issue_id, prs[-1])


def handle_event(payload: dict) -> None:
    action = payload.get("action")
    sess = payload.get("agentSession") or {}
    sid = sess.get("id")
    if not sid:
        return
    issue = sess.get("issue") or {}
    ident = issue.get("identifier", "?")
    with active_lock:
        active.add(ident)
    try:
        if action == "created":
            thought(sid, f"On it — picking up {ident}." +
                    ("" if slots._value else " Queued behind other running jobs."))  # noqa: SLF001
            with slots:
                move_to_started(issue.get("id", ""))
                prompt = BRIEF.format(agent=AGENT_NAME, scripts=Path(__file__).parent, extra=EXTRA_RULES,
                    context=payload.get("promptContext") or json.dumps(issue)[:4000],
                    identifier=ident, url=issue.get("url", ""),
                    branch=issue.get("branchName") or issue.get("gitBranchName") or "(use the issue's Linear branch name)")
                save_state_entry(sid, {"issue": ident, "started": time.strftime("%F %T")})
                result, prs = run_claude(sid, prompt, None, issue.get("id", ""))
                finish(sid, ident, issue.get("id", ""), result, prs)
        elif action == "prompted":
            msg = ((payload.get("agentActivity") or {}).get("content") or {}).get("body") \
                or (payload.get("agentActivity") or {}).get("body") or ""
            if (payload.get("agentActivity") or {}).get("signal") == "stop":
                thought(sid, "Stop received.")
                return
            thought(sid, "Got it — continuing.")
            prev = load_state().get(sid, {}).get("claude_session")
            with slots:
                result, prs = run_claude(sid, f"Follow-up in the Linear session for {ident}:\n\n{msg}\n\n"
                                              "Act on it with the same rules as before, then summarise.", prev, issue.get("id", ""))
                finish(sid, ident, issue.get("id", ""), result, prs)
    except Exception as ex:
        log(f"[{sid}] FAILED: {ex}\n{traceback.format_exc()}")
        error(sid, f"the agent failed: {str(ex)[:300]} — reply here to retry.")
    finally:
        with active_lock:
            active.discard(ident)




# --------------------------------------------------------------------------- PR events → merge (replaces hourly linear-merge)

def gated() -> dict:
    return json.loads(GATED_FILE.read_text()) if GATED_FILE.exists() else {}


def mark_gated(key: str, verdict: str) -> None:
    with state_lock:
        g = gated()
        g[key] = verdict
        GATED_FILE.write_text(json.dumps(g, indent=1))


def linear_mod():
    sys.path.insert(0, str(Path(__file__).parent))
    import linear  # noqa: E402
    return linear


def comment_as_forge(ident: str, body: str) -> None:
    try:
        iid = gql("query($id: String!) { issue(id: $id) { id } }", {"id": ident})["issue"]["id"]
        gql("mutation($i: CommentCreateInput!) { commentCreate(input: $i) { success } }", {"i": {"issueId": iid, "body": body}})
    except Exception as ex:
        log(f"comment on {ident} failed: {ex}")


def issue_for_pr(pr: dict) -> str | None:
    """Issue id from title/branch/body; an untracked PR by the owner gets a tracking issue."""
    m = ISSUE_RE.search(" ".join([pr.get("title") or "", pr.get("headRefName") or "", pr.get("body") or ""]))
    if m:
        return f"{TEAM_KEY}-{m.group(1)}"
    if not OWNER_GH or (pr.get("author") or {}).get("login") != OWNER_GH:
        return None  # contributors / dependabot: not ours to auto-merge
    tracked = json.loads(TRACK_FILE.read_text()) if TRACK_FILE.exists() else {}
    if pr["url"] in tracked:
        return tracked[pr["url"]]
    hit = linear_mod().gql("""query($q: String!) { issues(first: 5, filter: {or: [
        {title: {containsIgnoreCase: $q}}, {description: {containsIgnoreCase: $q}}]}) { nodes { identifier } } }""",
        {"q": pr["url"].split("github.com/")[1]})["issues"]["nodes"]
    hit = hit or linear_mod().gql("""query($q: String!) { issues(first: 5, filter: {title: {containsIgnoreCase: $q}}) {
        nodes { identifier } } }""", {"q": f"PR #{pr['number']}"})["issues"]["nodes"]
    if hit:
        tracked[pr["url"]] = hit[0]["identifier"]
        TRACK_FILE.write_text(json.dumps(tracked, indent=1))
        return hit[0]["identifier"]
    out = subprocess.run(["python3", str(Path(__file__).parent / "linear.py"), "create", "--title",
                          f"{pr['repo']} PR #{pr['number']}: {pr['title']}"[:120], "--body",
                          f"Tracking issue for {pr['url']} (opened without a Linear issue). Done = merged."],
                         capture_output=True, text=True).stdout
    m = ISSUE_RE.search(out)
    if m:
        tracked[pr["url"]] = f"{TEAM_KEY}-{m.group(1)}"
        TRACK_FILE.write_text(json.dumps(tracked, indent=1))
    return f"{TEAM_KEY}-{m.group(1)}" if m else None


def gate_pr(pr: dict) -> None:
    """Merge gate for a PR outside a the agent session. MERGED → Done; RED → the agent fixes it."""
    ident = issue_for_pr(pr)
    if not ident:
        return
    key = f"{pr['url']}@{pr['headRefOid']}"
    with active_lock:
        if ident in active or key in gated():
            return
        active.add(ident)
    try:
        with slots:
            log(f"gate {ident} {pr['url']} @ {pr['headRefOid'][:7]} (event)")
            out, _ = run_claude("gate", GATE.format(ident=ident, pr=pr["url"], scripts=Path(__file__).parent), None, record=False)
            verdict = next((l for l in reversed(out.splitlines()) if l.startswith("VERDICT:")), "VERDICT: RED — gate returned no verdict")
            body = render(parse_result(out), pr["url"], out)
            mark_gated(key, verdict)
            log(f"gate {ident}: {verdict}")
            if verdict.startswith("VERDICT: MERGED"):
                comment_as_forge(ident, body)
                iid = gql("query($id: String!) { issue(id: $id) { id } }", {"id": ident})["issue"]["id"]
                set_state(iid, "Done")
            else:
                comment_as_forge(ident, body)
                linear_mod().delegate_to_forge(ident)  # the agent session fixes the same PR, then re-gates
    except BaseException as ex:
        log(f"gate {ident} failed: {ex}\n{traceback.format_exc()}")
    finally:
        with active_lock:
            active.discard(ident)


PR_FIELDS = "number,title,url,headRefName,headRefOid,author,isDraft,body"


def open_prs(repo: str) -> list[dict]:
    out = subprocess.run(["gh", "pr", "list", "-R", repo, "--state", "open", "--json", PR_FIELDS, "--limit", "50"],
                         capture_output=True, text=True, timeout=60).stdout or "[]"
    return [{**p, "repo": repo} for p in json.loads(out) if not p["isDraft"]]


def sweep_loop() -> None:
    """Safety net for missed webhooks (Mac asleep, tunnel down): every 15 min gate any open PR
    whose current head hasn't been gated yet."""
    time.sleep(60)
    while True:
        for repo in REPOS:
            try:
                for pr in open_prs(repo):
                    if f"{pr['url']}@{pr['headRefOid']}" not in gated():
                        threading.Thread(target=gate_pr, args=(pr,), daemon=True).start()
            except Exception as ex:
                log(f"sweep {repo} failed: {ex}")
        time.sleep(15 * 60)


def handle_github(event: str, payload: dict) -> None:
    pr = payload.get("pull_request") or {}
    if event != "pull_request" or payload.get("action") not in ("opened", "reopened", "synchronize", "ready_for_review"):
        return
    if pr.get("draft") or pr.get("state") != "open":
        return
    repo = payload["repository"]["full_name"]
    gate_pr({"number": pr["number"], "title": pr["title"], "url": pr["html_url"], "headRefName": pr["head"]["ref"],
             "headRefOid": pr["head"]["sha"], "author": {"login": pr["user"]["login"]}, "body": pr.get("body") or "",
             "repo": repo})

# --------------------------------------------------------------------------- HTTP

class H(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def send(self, code: int, body: str, ctype="text/plain", headers: dict | None = None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == "/health":
            ok = TOKEN_FILE.exists()
            return self.send(200 if ok else 503, "ok" if ok else "not installed")
        if u.path == "/install":
            params = {"client_id": env()["LINEAR_AGENT_CLIENT_ID"], "redirect_uri": REDIRECT_URI,
                      "response_type": "code", "actor": "app",
                      "scope": "read,write,app:assignable,app:mentionable"}
            return self.send(302, "", headers={"Location": "https://linear.app/oauth/authorize?" + urllib.parse.urlencode(params)})
        if u.path == "/oauth/callback" and "code" in q:
            try:
                tok = token_request({"grant_type": "authorization_code", "code": q["code"][0], "redirect_uri": REDIRECT_URI})
                save_token(tok)
                me = gql("{ viewer { id name } }")["viewer"]
                tok["app_user_id"] = me["id"]
                save_token(tok)
                log(f"installed as {me}")
                return self.send(200, f"the agent installed in Linear as {me['name']} ({me['id']}). You can close this tab.")
            except Exception as ex:
                log(f"oauth failed: {ex}")
                return self.send(500, f"OAuth failed: {ex}")
        return self.send(404, "not found")

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if path == "/github":
            secret = env().get("GITHUB_WEBHOOK_SECRET", "")
            sig = self.headers.get("X-Hub-Signature-256", "")
            want = "sha256=" + hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
            if not secret or not hmac.compare_digest(want, sig):
                log("rejected github webhook: bad signature")
                return self.send(401, "bad signature")
            self.send(200, "ok")
            ev = self.headers.get("X-GitHub-Event", "")
            threading.Thread(target=handle_github, args=(ev, json.loads(raw)), daemon=True).start()
            return
        if path != "/webhook":
            return self.send(404, "not found")
        secret = env().get("LINEAR_AGENT_WEBHOOK_SECRET", "")
        sig = self.headers.get("Linear-Signature", "")
        if not secret or not hmac.compare_digest(hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest(), sig):
            log("rejected webhook: bad signature")
            return self.send(401, "bad signature")
        payload = json.loads(raw)
        self.send(200, "ok")  # Linear needs a reply within 5 s — work happens in a thread
        if payload.get("type") == "AgentSessionEvent":
            log(f"event {payload.get('action')} session={(payload.get('agentSession') or {}).get('id')}")
            threading.Thread(target=handle_event, args=(payload,), daemon=True).start()
        else:
            log(f"ignored webhook type={payload.get('type')} action={payload.get('action')}")


def auto_delegate_loop() -> None:
    """Replaces the linear-dispatch routine: Todo = approved → delegate to the agent.
    Runs as the owner (API key) so Linear opens a real agent session."""
    sys.path.insert(0, str(Path(__file__).parent))
    import linear  # noqa: E402
    while True:
        try:
            todo = linear.fetch_issues(limit=50, states=["Todo"])
            for i in sorted(todo, key=lambda x: x["createdAt"])[:MAX_PARALLEL]:
                if any(l["name"] == os.environ.get("AGENT_HUMAN_LABEL", "commander") for l in i["labels"]["nodes"]):
                    continue
                d = linear.gql("query($id: String!) { issue(id: $id) { delegate { id } assignee { id } } }",
                               {"id": i["identifier"]})["issue"]
                # Delegation is the real trigger; Todo is only a fallback for UNASSIGNED issues —
                # an issue a teammate owns is theirs, never grabbed.
                if not d.get("delegate") and not d.get("assignee"):
                    linear.delegate_to_forge(i["identifier"])
                    log(f"auto-delegated {i['identifier']} (Todo) to the agent")
            resume_unblocked()
        except BaseException as ex:  # linear.py uses sys.exit on API errors
            log(f"auto-delegate tick failed: {ex}")
        time.sleep(60)


RESUMED_FILE = CFG_DIR / "agent-resumed-blockers.json"


def resume_unblocked() -> None:
    """A commander blocker moved to Done → re-delegate the issue it blocked to the agent."""
    sys.path.insert(0, str(Path(__file__).parent))
    import linear  # noqa: E402
    seen = set(json.loads(RESUMED_FILE.read_text())) if RESUMED_FILE.exists() else set()
    q = """{ issues(first: 50, filter: {labels: {name: {eq: "%s"}}, state: {type: {eq: "completed"}},
            completedAt: {gt: "-P2D"}}) { nodes { identifier relations { nodes { type relatedIssue {
            identifier state { type } } } } } } }""" % os.environ.get("AGENT_HUMAN_LABEL", "commander")
    for b in linear.gql(q)["issues"]["nodes"]:
        if b["identifier"] in seen:
            continue
        for r in b["relations"]["nodes"]:
            if r["type"] == "blocks" and r["relatedIssue"]["state"]["type"] not in ("completed", "canceled"):
                linear.delegate_to_forge(r["relatedIssue"]["identifier"])
                log(f"blocker {b['identifier']} done → resumed {r['relatedIssue']['identifier']}")
        seen.add(b["identifier"])
    RESUMED_FILE.write_text(json.dumps(sorted(seen)))


def main():
    load_config()
    log(f"listening on 127.0.0.1:{PORT} as {AGENT_NAME} for {len(REPOS)} repos")
    threading.Thread(target=auto_delegate_loop, daemon=True).start()
    threading.Thread(target=sweep_loop, daemon=True).start()
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()


if __name__ == "__main__":
    sys.exit(main())
