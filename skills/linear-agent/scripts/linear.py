#!/usr/bin/env python3
"""linear.py — Linear from a shell, for agents that have bash but no MCP connector.

Reads are free. Agent writes are limited to what any agent may do without asking
(rules/consent-and-control.md): comment on an issue, create an issue in Triage.
`approve` and `drop` are the owner's control verbs — run them ONLY on an explicit
instruction from the owner naming the issue (e.g. "ok ENG-123", "drop ENG-45"), never on
an agent's own judgement. Every write is read back before it is reported.

Key: LINEAR_API_KEY in the environment or ~/.config/linear/agent.env.

  linear.py status   [--project <P>] [--days 7]
  linear.py issues   [--project P] [--state "In Progress,Todo"] [--label L] [--search TEXT] [--limit 25]
  linear.py issue    ENG-123
  linear.py comment  ENG-123 "text"
  linear.py create   --title T [--body B] [--project P] [--label L]
  linear.py projects
  linear.py digest   [--html]            # the daily "on you" list (decisions + next up)
  linear.py approve  ENG-123 [--note N]  # owner: Backlog/Triage → Todo; HELD PR → merge ok
  linear.py drop     ENG-123 [--note N]  # owner: → Canceled, closes its open PRs
  linear.py done     ENG-123 [--note N]  # owner: a physical/GUI task is finished → Done
  linear.py delegate ENG-123             # (re)delegate to the agent → opens a new agent session
  linear.py blocker  --for ENG-123 --title T --do "step 1|step 2" --summary S [--details D]
                                         # a blocker only owner can clear → new ticket assigned to owner
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

API = "https://api.linear.app/graphql"
TEAM_KEY = os.environ.get("LINEAR_TEAM_KEY", "ENG")
STATE_ORDER = ["Triage", "Backlog", "Todo", "In Progress", "Done", "Canceled", "Duplicate"]


def api_key() -> str:
    key = os.environ.get("LINEAR_API_KEY")
    if not key:
        for env in (Path.home() / ".config" / "linear" / "agent.env", Path.home() / ".config" / "linear" / ".env"):
          if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("LINEAR_API_KEY=") and not key:
                    key = line.split("=", 1)[1].strip().strip('"')
    if not key:
        sys.exit("LINEAR_API_KEY not set (env or ~/.config/linear/agent.env)")
    return key


def gql(query: str, variables: dict | None = None) -> dict:
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": api_key(), "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if out.get("errors"):
        sys.exit("Linear error: " + "; ".join(e.get("message", "?") for e in out["errors"]))
    return out["data"]


ISSUE_FIELDS = """identifier title url priority updatedAt createdAt
  state { name } project { name } assignee { name }
  labels { nodes { name } }"""


def fmt(i: dict) -> str:
    labels = ",".join(l["name"] for l in i["labels"]["nodes"])
    proj = (i.get("project") or {}).get("name") or "—"
    return f"{i['identifier']:<8} [{i['state']['name']}] {i['title']}  ({proj}; {labels or 'no labels'}; upd {i['updatedAt'][:10]})"


def issue_filter(project=None, states=None, label=None, search=None, since=None) -> dict:
    f: dict = {"team": {"key": {"eq": TEAM_KEY}}}
    if project:
        f["project"] = {"name": {"eqIgnoreCase": project}}
    if states:
        f["state"] = {"name": {"in": states}}
    if label:
        f["labels"] = {"name": {"eqIgnoreCase": label}}
    if search:
        f["title"] = {"containsIgnoreCase": search}
    if since:
        f["updatedAt"] = {"gte": since}
    return f


def fetch_issues(limit=50, **kw) -> list[dict]:
    q = f"""query($f: IssueFilter, $n: Int) {{
      issues(filter: $f, first: $n, orderBy: updatedAt) {{ nodes {{ {ISSUE_FIELDS} }} }} }}"""
    return gql(q, {"f": issue_filter(**kw), "n": limit})["issues"]["nodes"]


def cmd_status(a):
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=a.days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    active = fetch_issues(limit=250, project=a.project, states=["Triage", "Backlog", "Todo", "In Progress"])
    counts: dict[str, int] = {}
    for i in active:
        counts[i["state"]["name"]] = counts.get(i["state"]["name"], 0) + 1
    scope = a.project or f"team {TEAM_KEY}"
    print(f"# Linear status — {scope} — {dt.date.today()}")
    print("Open: " + " · ".join(f"{s} {counts[s]}" for s in STATE_ORDER if s in counts))
    for state in ["In Progress", "Todo"]:
        rows = [i for i in active if i["state"]["name"] == state]
        print(f"\n## {state} ({len(rows)})")
        for i in rows[:20]:
            print("  " + fmt(i))
    commander = [i for i in active if any(l["name"] == HUMAN_LABEL for l in i["labels"]["nodes"])]
    print(f"\n## On owner — agent:commander ({len(commander)})")
    for i in commander[:15]:
        print("  " + fmt(i))
    triage = sorted((i for i in active if i["state"]["name"] == "Triage"), key=lambda i: i["createdAt"])
    print(f"\n## Triage — needs a decision ({len(triage)}, oldest first)")
    for i in triage[:10]:
        print("  " + fmt(i))
    done = fetch_issues(limit=30, project=a.project, states=["Done"], since=since)
    print(f"\n## Done in last {a.days}d ({len(done)})")
    for i in done:
        print("  " + fmt(i))


def cmd_issues(a):
    states = [s.strip() for s in a.state.split(",")] if a.state else None
    rows = fetch_issues(limit=a.limit, project=a.project, states=states, label=a.label, search=a.search)
    for i in rows:
        print(fmt(i))
    print(f"-- {len(rows)} issue(s)")


def get_issue(ident: str) -> dict:
    q = f"""query($id: String!) {{ issue(id: $id) {{ id {ISSUE_FIELDS} description
      comments(first: 50) {{ nodes {{ body createdAt user {{ name }} }} }}
      attachments {{ nodes {{ title url }} }} }} }}"""
    return gql(q, {"id": ident})["issue"]


def cmd_issue(a):
    i = get_issue(a.id)
    print(fmt(i))
    print(i["url"])
    print("\n" + (i.get("description") or "(no description)"))
    atts = i["attachments"]["nodes"]
    if atts:
        print("\n## Links")
        for x in atts:
            print(f"  {x['title']}: {x['url']}")
    comments = sorted(i["comments"]["nodes"], key=lambda c: c["createdAt"])
    if comments:
        print(f"\n## Comments ({len(comments)})")
        for c in comments:
            who = (c.get("user") or {}).get("name") or "bot"
            print(f"- {c['createdAt'][:16]} {who}: {c['body']}")


def cmd_comment(a):
    issue = get_issue(a.id)
    r = gql("""mutation($i: String!, $b: String!) { commentCreate(input: {issueId: $i, body: $b}) {
      success comment { id } } }""", {"i": issue["id"], "b": a.body})
    cid = r["commentCreate"]["comment"]["id"]
    back = gql("query($id: String!) { comment(id: $id) { id body } }", {"id": cid})["comment"]
    if not back or back["body"] != a.body:
        sys.exit(f"Comment write did not verify on {a.id} — check Linear")
    print(f"Comment added to {a.id} (verified): {issue['url']}")


def cmd_create(a):
    team = gql("query($k: String!) { teams(filter: {key: {eq: $k}}) { nodes { id states { nodes { id name } } } } }",
               {"k": TEAM_KEY})["teams"]["nodes"][0]
    triage = next(s["id"] for s in team["states"]["nodes"] if s["name"] == "Triage")
    inp = {"teamId": team["id"], "title": a.title, "stateId": triage,
           "description": a.body or "Tension: " + a.title + "\nDriver: — (unclarified at capture)\n"
           "Requirement: — (unclarified at capture)\nResponse Options: — (unclarified at capture)"}
    if a.project:
        p = gql("query($n: String!) { projects(filter: {name: {eqIgnoreCase: $n}}) { nodes { id } } }",
                {"n": a.project})["projects"]["nodes"]
        if not p:
            sys.exit(f"No project named {a.project!r} (see: linear.py projects)")
        inp["projectId"] = p[0]["id"]
    if a.label:
        l = gql("query($n: String!) { issueLabels(filter: {name: {eqIgnoreCase: $n}}) { nodes { id } } }",
                {"n": a.label})["issueLabels"]["nodes"]
        if l:
            inp["labelIds"] = [l[0]["id"]]
    r = gql("mutation($i: IssueCreateInput!) { issueCreate(input: $i) { issue { identifier } } }", {"i": inp})
    ident = r["issueCreate"]["issue"]["identifier"]
    back = get_issue(ident)
    print(f"Created (verified): {fmt(back)}\n{back['url']}")


def cmd_projects(a):
    q = "{ projects(first: 50, filter: {state: {nin: [\"canceled\", \"completed\"]}}) { nodes { name state url } } }"
    for p in gql(q)["projects"]["nodes"]:
        print(f"{p['name']}  [{p['state']}]  {p['url']}")


# ---------------------------------------------------------------------------
# owner control loop — digest out, approve/drop back in.
#
# Every terminal state in linear-dispatch / linear-merge ends in "waits for the
# owner" (HELD, fix lane exhausted, parked in Backlog, agent:commander). Without
# this, those asks only lived in run logs nobody reads, so work silently stopped.
# Comments written here carry the "owner ·" prefix: every Linear comment is
# authored by the same API-key user, so the prefix is how the routines tell a
# owner instruction from an agent's own post.

import re
import subprocess

COMMANDER_PREFIX = "Owner ·"
HUMAN_LABEL = os.environ.get("AGENT_HUMAN_LABEL", "commander")  # marks work only a human can do
PR_RE = re.compile(r"https://github\.com/[\w.-]+/[\w.-]+/pull/\d+")
DIGEST_FIELDS = f"""id {ISSUE_FIELDS} description
  comments(first: 50) {{ nodes {{ body createdAt }} }}
  attachments {{ nodes {{ url }} }}"""


def fetch_full(states: list[str], limit=250) -> list[dict]:
    q = f"""query($f: IssueFilter, $n: Int) {{
      issues(filter: $f, first: $n, orderBy: createdAt) {{ nodes {{ {DIGEST_FIELDS} }} }} }}"""
    return gql(q, {"f": issue_filter(states=states), "n": limit})["issues"]["nodes"]


def comments_sorted(i: dict) -> list[dict]:
    return sorted(i["comments"]["nodes"], key=lambda c: c["createdAt"])


def last_gate(i: dict) -> dict | None:
    gates = [c for c in comments_sorted(i) if c["body"].startswith("Merge gate ·")]
    return gates[-1] if gates else None


def pr_urls(i: dict) -> list[str]:
    found = []
    for c in comments_sorted(i):
        found += PR_RE.findall(c["body"])
    found += [a["url"] for a in i["attachments"]["nodes"] if PR_RE.fullmatch(a["url"] or "")]
    return list(dict.fromkeys(found))


_pr_cache: dict[str, str] = {}


def pr_state(url: str) -> str:
    if url not in _pr_cache:
        try:
            out = subprocess.run(["gh", "pr", "view", url, "--json", "state", "-q", ".state"],
                                 capture_output=True, text=True, timeout=30)
            _pr_cache[url] = out.stdout.strip() or "UNKNOWN"
        except Exception:
            _pr_cache[url] = "UNKNOWN"
    return _pr_cache[url]


def open_prs(i: dict) -> list[str]:
    return [u for u in pr_urls(i) if pr_state(u) == "OPEN"]


def needed_line(gate_body: str) -> str:
    """The one sentence the owner needs: the gate's 'Needed:' line, else its verdict line."""
    lines = gate_body.splitlines()
    for n, line in enumerate(lines):
        if "Needed" in line:
            rest = line.split("Needed", 1)[1].lstrip(":- ").strip()
            if rest and not rest.endswith(":"):
                return rest
            follow = [l.lstrip("-• ").strip() for l in lines[n + 1:n + 3] if l.strip()]
            if follow:
                return (rest + " " if rest else "") + "; ".join(follow)
    reds = [l for l in lines[1:] if re.search(r"\b(red|RED|blocked|RESERVED)\b", l)]
    return "; ".join(r.split("—", 1)[0].strip() + ":" + r.split("—", 2)[-1] for r in reds[:2]) or lines[0]


def short(s: str, n=160) -> str:
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def has_label(i: dict, name: str) -> bool:
    return any(l["name"] in (name, f"agent:{name}") for l in i["labels"]["nodes"])


def build_digest() -> dict:
    active = fetch_full(["Triage", "Backlog", "Todo", "In Progress"])
    held, red, parked, hands, nxt = [], [], [], [], []
    for i in active:
        st = i["state"]["name"]
        gate = last_gate(i)
        verdict = gate["body"].split("·")[1].strip() if gate else ""
        if st == "In Progress":
            if verdict == "HELD":
                held.append((i, needed_line(gate["body"]), open_prs(i)))
            elif verdict == "RED":
                red.append((i, needed_line(gate["body"]), open_prs(i)))
        elif st in ("Backlog", "Triage"):
            prs = open_prs(i) if pr_urls(i) else []
            if has_label(i, HUMAN_LABEL):
                hands.append((i, "", prs))
            elif prs:
                parked.append((i, needed_line(gate["body"]) if gate else "PR open, issue parked", prs))
            else:
                nxt.append(i)
    nxt.sort(key=lambda i: (i["priority"] or 5, i["createdAt"]))
    return {"held": held, "red": red, "parked": parked, "hands": hands, "next": nxt[:3],
            "counts": {s: sum(1 for i in active if i["state"]["name"] == s)
                       for s in ["Triage", "Backlog", "Todo", "In Progress"]}}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_digest(d: dict, html: bool) -> str:
    b = (lambda s: f"<b>{esc(s)}</b>") if html else (lambda s: s)
    t = esc if html else (lambda s: s)
    out = [b("Work — what's waiting on you")]
    c = d["counts"]
    out.append(t(f"In Progress {c['In Progress']} · Todo {c['Todo']} · Backlog {c['Backlog']} · Triage {c['Triage']}"))

    def sec(title, rows, verb):
        if not rows:
            return
        out.append("")
        out.append(b(title))
        for i, why, prs in rows:
            line = f"{i['identifier']} · {i['title']}"
            if why:
                line += f" — {short(why)}"
            out.append(t(line))
            for u in prs[:1]:
                out.append(t("   " + u))
        out.append(t(verb))

    sec("1. Merge? (all checks green, reserved class — needs your explicit ok)", d["held"],
        "→ reply: ok ENG-n = merge · drop ENG-n = cancel")
    sec("2. PR blocked — fix lane can't finish without you", d["red"],
        "→ reply: ok ENG-n = re-dispatch the fix (counter resets) · drop ENG-n = cancel + close PR")
    sec("3. Parked with an open PR (gate ran out of tries)", d["parked"],
        "→ reply: ok ENG-n = re-dispatch on the same PR · drop ENG-n = cancel + close PR")
    sec("4. Only your hands can do these (physical / GUI)", d["hands"],
        "→ do it, then reply: done ENG-n")
    if d["next"]:
        out.append("")
        out.append(b("5. Next up — approve to start (max 3/run, oldest first)"))
        for i in d["next"]:
            out.append(t(f"{i['identifier']} · {i['title']} ({(i.get('project') or {}).get('name') or '—'})"))
        out.append(t("→ reply: ok ENG-n (several: ok ENG-1 ENG-2)"))
    return "\n".join(out)


def cmd_digest(a):
    d = build_digest()
    if not any(d[k] for k in ("held", "red", "parked", "hands", "next")):
        return  # empty digest = send nothing
    print(render_digest(d, a.html))


def set_state(issue: dict, name: str) -> None:
    team = gql("query($k: String!) { teams(filter: {key: {eq: $k}}) { nodes { states { nodes { id name } } } } }",
               {"k": TEAM_KEY})["teams"]["nodes"][0]
    sid = next(s["id"] for s in team["states"]["nodes"] if s["name"] == name)
    gql("mutation($i: String!, $s: String!) { issueUpdate(id: $i, input: {stateId: $s}) { success } }",
        {"i": issue["id"], "s": sid})
    # save_issue-style writes can silently fail; read back (Linear reads may lag — retry)
    for _ in range(3):
        if get_issue(issue["identifier"])["state"]["name"] == name:
            return
        __import__("time").sleep(2)
    sys.exit(f"State write to {name} did not verify on {issue['identifier']} — check Linear")


def add_comment(issue: dict, body: str) -> None:
    gql("mutation($i: String!, $b: String!) { commentCreate(input: {issueId: $i, body: $b}) { success } }",
        {"i": issue["id"], "b": body})


def cmd_approve(a):
    i = fetch_one(a.id)
    st = i["state"]["name"]
    gate = last_gate(i)
    note = f" — {a.note}" if a.note else ""
    if st == "In Progress" and gate and "· HELD ·" in gate["body"]:
        add_comment(i, f"{COMMANDER_PREFIX} ok — merge.{note}")
        print(f"{a.id}: merge approved (HELD → linear-merge merges on its next hourly run). {i['url']}")
    elif st == "In Progress":
        add_comment(i, f"{COMMANDER_PREFIX} ok — re-dispatch the fix.{note}")
        delegate_to_forge(a.id)
        print(f"{a.id}: delegated to the agent to fix — work starts now. {i['url']}")
    elif st in ("Backlog", "Triage", "Todo"):
        add_comment(i, f"{COMMANDER_PREFIX} ok — approved; fix-lane counter resets here.{note}")
        if st != "Todo":
            set_state(i, "Todo")
        delegate_to_forge(a.id)
        print(f"{a.id}: {st} → Todo, delegated to the agent (verified) — work starts now. {i['url']}")
    else:
        sys.exit(f"{a.id} is {st} — nothing to approve")


def cmd_drop(a):
    i = fetch_one(a.id)
    closed = []
    for u in open_prs(i):
        r = subprocess.run(["gh", "pr", "close", u, "--comment",
                            f"Closed: {a.id} was dropped by the owner."], capture_output=True, text=True)
        if r.returncode == 0:
            closed.append(u)
    add_comment(i, f"{COMMANDER_PREFIX} drop.{(' — ' + a.note) if a.note else ''}"
                   + (f" Closed PRs: {', '.join(closed)}" if closed else ""))
    set_state(i, "Canceled")
    print(f"{a.id}: → Canceled (verified); closed {len(closed)} PR(s). {i['url']}")


def cmd_done(a):
    i = fetch_one(a.id)
    add_comment(i, f"{COMMANDER_PREFIX} done — completed by the owner.{(' ' + a.note) if a.note else ''}")
    set_state(i, "Done")
    print(f"{a.id}: → Done (verified). {i['url']}")


def _cfg(key: str) -> str:
    v = os.environ.get(key, "")
    f = Path.home() / ".config" / "linear" / "agent.env"
    if not v and f.exists():
        for line in f.read_text().splitlines():
            if line.startswith(key + "="):
                v = line.split("=", 1)[1].strip().strip('"')
    if not v and key == "LINEAR_AGENT_USER_ID":
        t = Path.home() / ".config" / "linear" / "agent-token.json"
        if t.exists():
            v = json.loads(t.read_text()).get("app_user_id", "")
    return v


FORGE_ID = _cfg("LINEAR_AGENT_USER_ID")  # the agent's app user id (written at install)


def delegate_to_forge(ident: str) -> None:
    """Delegating as the API-key user opens an agent session; if the agent is already the
    delegate, clear and re-set so a new session starts (used by the merge gate's fix loop)."""
    i = gql("query($id: String!) { issue(id: $id) { id delegate { id } } }", {"id": ident})["issue"]
    upd = "mutation($id: String!, $d: String) { issueUpdate(id: $id, input: {delegateId: $d}) { success } }"
    if (i.get("delegate") or {}).get("id") == FORGE_ID:
        gql(upd, {"id": i["id"], "d": None})
        __import__("time").sleep(2)
    gql(upd, {"id": i["id"], "d": FORGE_ID})


def cmd_delegate(a):
    delegate_to_forge(a.id)
    back = gql("query($id: String!) { issue(id: $id) { delegate { name } url } }", {"id": a.id})["issue"]
    if (back.get("delegate") or {}).get("name") != "the agent":
        sys.exit(f"Delegation did not verify on {a.id}")
    print(f"{a.id}: delegated to the agent (verified) — session starting. {back['url']}")


ALEX_ID = _cfg("LINEAR_OWNER_ID")  # the human who receives blocker tickets


def cmd_blocker(a):
    """Blockers are tickets, never comments . Assigned to owner,
    labelled commander (so the agent auto-delegation skips it), in Todo, blocking the source issue.
    Body: very simple steps first, then a short executive summary, then details only if needed."""
    src = gql("query($id: String!) { issue(id: $id) { id identifier url project { id } team { id states { nodes { id name } } } } }",
              {"id": a.source})["issue"]
    todo = next(x["id"] for x in src["team"]["states"]["nodes"] if x["name"] == "Todo")
    label = gql("query($n: String!) { issueLabels(filter: {name: {eq: $n}}) { nodes { id } } }", {"n": HUMAN_LABEL})["issueLabels"]["nodes"]
    if not label:  # first blocker in this workspace — create the label
        label = [gql("mutation($n: String!) { issueLabelCreate(input: {name: $n, color: \"#F2994A\"}) { issueLabel { id } } }",
                     {"n": HUMAN_LABEL})["issueLabelCreate"]["issueLabel"]]
    steps = "\n".join(f"{n}. {t.strip()}" for n, t in enumerate(a.do.split("|"), 1) if t.strip())
    body = (f"## Do this\n{steps}\n\nThen move this ticket to **Done** — the agent resumes {src['identifier']} automatically.\n\n"
            f"## Summary\n{a.summary.strip()}\n\nBlocks: {src['url']}")
    if a.details:
        body += f"\n\n## Details\n{a.details.strip()}"
    inp = {"teamId": src["team"]["id"], "title": a.title, "description": body, "stateId": todo,
           "assigneeId": ALEX_ID, "priority": 1}
    if src.get("project"):
        inp["projectId"] = src["project"]["id"]
    if label:
        inp["labelIds"] = [label[0]["id"]]
    new = gql("mutation($i: IssueCreateInput!) { issueCreate(input: $i) { issue { id identifier url } } }", {"i": inp})["issueCreate"]["issue"]
    gql("mutation($i: IssueRelationCreateInput!) { issueRelationCreate(input: $i) { success } }",
        {"i": {"issueId": new["id"], "relatedIssueId": src["id"], "type": "blocks"}})
    back = gql("query($id: String!) { issue(id: $id) { assignee { id } state { name } } }", {"id": new["identifier"]})["issue"]
    if (back.get("assignee") or {}).get("id") != ALEX_ID:
        sys.exit(f"Blocker {new['identifier']} created but assignment did not verify")
    print(f"Blocker {new['identifier']} → owner [{back['state']['name']}], blocks {src['identifier']}: {new['url']}")


def fetch_one(ident: str) -> dict:
    q = f"query($id: String!) {{ issue(id: $id) {{ {DIGEST_FIELDS} }} }}"
    return gql(q, {"id": ident})["issue"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status"); s.add_argument("--project"); s.add_argument("--days", type=int, default=7)
    s.set_defaults(fn=cmd_status)
    s = sub.add_parser("issues"); s.add_argument("--project"); s.add_argument("--state"); s.add_argument("--label")
    s.add_argument("--search"); s.add_argument("--limit", type=int, default=25); s.set_defaults(fn=cmd_issues)
    s = sub.add_parser("issue"); s.add_argument("id"); s.set_defaults(fn=cmd_issue)
    s = sub.add_parser("comment"); s.add_argument("id"); s.add_argument("body"); s.set_defaults(fn=cmd_comment)
    s = sub.add_parser("create"); s.add_argument("--title", required=True); s.add_argument("--body")
    s.add_argument("--project"); s.add_argument("--label"); s.set_defaults(fn=cmd_create)
    s = sub.add_parser("projects"); s.set_defaults(fn=cmd_projects)
    s = sub.add_parser("blocker"); s.add_argument("--for", dest="source", required=True)
    s.add_argument("--title", required=True); s.add_argument("--do", required=True)
    s.add_argument("--summary", required=True); s.add_argument("--details"); s.set_defaults(fn=cmd_blocker)
    s = sub.add_parser("delegate"); s.add_argument("id"); s.set_defaults(fn=cmd_delegate)
    s = sub.add_parser("digest"); s.add_argument("--html", action="store_true"); s.set_defaults(fn=cmd_digest)
    for name, fn in (("approve", cmd_approve), ("drop", cmd_drop), ("done", cmd_done)):
        s = sub.add_parser(name); s.add_argument("id", nargs="+"); s.add_argument("--note")
        s.set_defaults(fn=lambda a, fn=fn: [fn(argparse.Namespace(id=x.upper(), note=a.note)) for x in a.id])
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
