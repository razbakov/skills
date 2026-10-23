#!/usr/bin/env python3
"""Local live dashboard of the tools this workspace depends on.

Serves:
  /                 the dashboard page
  /api/state        merged registry + transcript usage + live probe results
Probes are shell commands declared in registry.json; all are read-only.
"""
import json, os, re, subprocess, sys, time, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = os.path.join(os.path.dirname(HERE), "assets")   # index.html and map.html
# The registry describes a workspace and lives in it, not next to this code. Probes run with the
# registry's own directory as their working directory, so a relative probe means what its author
# meant it to mean.
REGISTRY = os.path.abspath(os.environ.get("TOOLSDASH_REGISTRY",
                                          os.path.join(PAGES, "registry.example.json")))
REPO = os.path.abspath(os.environ.get("TOOLSDASH_ROOT",
                                      os.path.dirname(os.path.dirname(REGISTRY))))
PORT = int(os.environ.get("PORT", "3523"))
PROBE_TIMEOUT = 20
CACHE_TTL = 45

_cache = {"at": 0, "data": None}
_lock = threading.Lock()


def scan_usage():
    out = subprocess.run([sys.executable, os.path.join(HERE, "scan.py")],
                         capture_output=True, text=True, timeout=300)
    if out.returncode != 0:
        return {"tools": {}, "transcripts": 0, "scan_error": out.stderr[-400:]}
    return json.loads(out.stdout)


def run_probe(entry):
    cmd = entry.get("probe")
    if not cmd:
        return None
    t0 = time.time()
    try:
        p = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True,
                           timeout=PROBE_TIMEOUT, cwd=REPO)
        out = (p.stdout + p.stderr).strip()
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "probe timed out after %ss" % PROBE_TIMEOUT,
                "ms": int((time.time() - t0) * 1000)}
    ok_pat = entry.get("probe_ok")
    if ok_pat:
        ok = bool(re.search(ok_pat, out))
    else:
        ok = p.returncode == 0
    return {"ok": ok, "output": out[:400], "ms": int((time.time() - t0) * 1000)}


def merge(entry, usage):
    keys = entry.get("usage_keys") or []
    agg = {"calls": 0, "errors": 0, "last_used": None, "last_error": None,
           "last_error_text": None, "last_session": None, "last_project": None,
           "last_error_session": None, "last_error_project": None, "members": []}
    for tid, rec in usage.get("tools", {}).items():
        if not any(tid == k or tid.startswith(k) for k in keys):
            continue
        agg["calls"] += rec["calls"]
        agg["errors"] += rec["errors"]
        if rec["last_used"] and (not agg["last_used"] or rec["last_used"] > agg["last_used"]):
            agg["last_used"] = rec["last_used"]
            agg["last_session"] = rec["last_session"]
            agg["last_project"] = rec["last_project"]
        if rec["last_error"] and (not agg["last_error"] or rec["last_error"] > agg["last_error"]):
            agg["last_error"] = rec["last_error"]
            agg["last_error_text"] = rec["last_error_text"]
            agg["last_error_session"] = rec["last_error_session"]
            agg["last_error_project"] = rec["last_error_project"]
        short = tid.split("__")[-1] if tid.startswith("mcp__") else tid
        agg["members"].append({"name": short, "calls": rec["calls"], "errors": rec["errors"]})
    agg["members"].sort(key=lambda m: -m["calls"])
    agg["members"] = agg["members"][:8]
    return agg


def status_of(entry, probe, usage):
    """broken | degraded | healthy | idle | disconnected"""
    if probe is not None and not probe["ok"]:
        return "broken", "live probe failed"
    if entry.get("connected_now") is False:
        return ("broken", "credentials/binary missing") if probe is not None \
            else ("disconnected", "not in the current session's connector list")
    u = usage
    if u["errors"] and u["last_error"] and u["last_used"] and u["last_error"] > u["last_used"]:
        return "degraded", "most recent call failed"
    if u["errors"] and u["calls"] and u["errors"] / u["calls"] >= 0.5:
        return "degraded", "fails more often than it works"
    if u["calls"] == 0:
        if probe is not None and probe["ok"]:
            return "healthy", "live probe passed (no call history to judge)"
        return "idle", "never called in the scanned transcripts"
    return "healthy", "last call succeeded"


def build():
    reg = json.load(open(REGISTRY))
    usage = scan_usage()
    entries = reg["tools"]
    with ThreadPoolExecutor(max_workers=12) as ex:
        probes = list(ex.map(run_probe, entries))
    rows = []
    for entry, probe in zip(entries, probes):
        u = merge(entry, usage)
        st, why = status_of(entry, probe, u)
        row = dict(entry)
        row.pop("probe", None)
        row.pop("probe_ok", None)
        row["probe_result"] = probe
        row["usage"] = u
        row["status"] = st
        row["status_reason"] = why
        rows.append(row)
    # A tool standing on a broken dependency is not healthy, however well it probes itself.
    by = {r["id"]: r for r in rows}
    for r in rows:
        if r["status"] not in ("healthy", "idle"):
            continue
        bad = [by[d]["name"] for d in r.get("depends_on", [])
               if d in by and by[d]["status"] in ("broken", "disconnected")]
        if bad:
            r["status"] = "degraded"
            r["status_reason"] = "depends on " + ", ".join(bad) + ", which is down"
    order = {"broken": 0, "disconnected": 1, "degraded": 2, "healthy": 3, "idle": 4}
    rows.sort(key=lambda r: (order[r["status"]], -r["usage"]["calls"]))
    return {"generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "meta": reg["meta"], "transcripts": usage.get("transcripts", 0),
            "scan_error": usage.get("scan_error"),
            "counts": {k: sum(1 for r in rows if r["status"] == k) for k in order},
            "tools": rows}


def state(force=False):
    with _lock:
        if not force and _cache["data"] and time.time() - _cache["at"] < CACHE_TTL:
            return _cache["data"]
        data = build()
        _cache.update(at=time.time(), data=data)
        return data


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.startswith("/api/state"):
            body = json.dumps(state(force="refresh=1" in self.path)).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        page = {"/": "index.html", "/index.html": "index.html",
                "/map": "map.html", "/map.html": "map.html"}.get(self.path.split("?")[0])
        if page:
            body = open(os.path.join(PAGES, page), "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)


if __name__ == "__main__":
    if not os.path.exists(REGISTRY):
        sys.exit("no registry at %s — set TOOLSDASH_REGISTRY to the registry you are serving"
                 % REGISTRY)
    print("tool dashboard on http://localhost:%d (registry: %s)" % (PORT, REGISTRY), flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
