#!/usr/bin/env python3
"""Check a registry.json against the schema in ops/toolsdash/REGISTRY.md.

  validate.py <path-to-registry.json> [--usage <scan.py output>]

Errors block (the dashboard would misreport); warnings are worth a look.
"""
import json, re, subprocess, sys, os

REQUIRED = {
    "id": str, "name": str, "category": str, "access": str, "connected_now": bool,
    "owner_agent": str, "also_used_by": list, "usage_keys": list, "depends_on": list,
    "alternatives": list, "fix": str, "docs": str, "notes": str,
}
CATEGORIES = {"mcp", "cli", "api", "browser", "automation", "skill", "manual"}
ALT_KINDS = {"mcp", "cli", "api", "skill", "web", "repo", "local", "automation", "manual"}
ALT_STATES = {"live", "degraded", "broken", "always"}


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: validate.py <registry.json> [--usage <usage.json>]")
    path = sys.argv[1]
    errors, warnings = [], []
    try:
        reg = json.load(open(path))
    except Exception as e:
        sys.exit("registry.json does not parse: %s" % e)

    meta = reg.get("meta") or {}
    for k in ("owner", "connected_verified"):
        if not meta.get(k):
            errors.append("meta.%s is missing" % k)

    tools = reg.get("tools")
    if not isinstance(tools, list) or not tools:
        sys.exit("registry.json has no tools array")

    ids = [t.get("id") for t in tools]
    for i in set(ids):
        if ids.count(i) > 1:
            errors.append("duplicate id: %s" % i)
    known = set(ids)

    for t in tools:
        tid = t.get("id", "<no id>")
        for field, typ in REQUIRED.items():
            if field not in t:
                errors.append("%s: missing %s" % (tid, field))
            elif not isinstance(t[field], typ):
                errors.append("%s: %s should be %s" % (tid, field, typ.__name__))
        if t.get("category") not in CATEGORIES:
            errors.append("%s: category %r is not one of %s" % (tid, t.get("category"), sorted(CATEGORIES)))
        if "probe" not in t:
            errors.append("%s: missing probe (use null when nothing is checkable)" % tid)
        if t.get("probe_ok"):
            try:
                re.compile(t["probe_ok"])
            except re.error as e:
                errors.append("%s: probe_ok is not a valid regex (%s)" % (tid, e))
        if t.get("probe_ok") and not t.get("probe"):
            errors.append("%s: probe_ok without a probe" % tid)
        for d in t.get("depends_on", []):
            if d not in known:
                errors.append("%s: depends_on %r is not an id in this file" % (tid, d))
            if d == tid:
                errors.append("%s: depends on itself" % tid)
        for a in t.get("alternatives", []):
            if not isinstance(a, dict) or not {"kind", "what", "state"} <= set(a):
                errors.append("%s: alternative needs kind, what and state" % tid)
                continue
            if a["kind"] not in ALT_KINDS:
                warnings.append("%s: alternative kind %r is unusual" % (tid, a["kind"]))
            if a["state"] not in ALT_STATES:
                errors.append("%s: alternative state %r is not one of %s" % (tid, a["state"], sorted(ALT_STATES)))
            if a.get("ref") and a["ref"] not in known:
                errors.append("%s: alternative ref %r is not an id in this file" % (tid, a["ref"]))
        if not t.get("alternatives"):
            warnings.append("%s: no alternatives — single point of failure, or unfilled?" % tid)
        if not (t.get("fix") or "").strip():
            errors.append("%s: fix is empty" % tid)
        if t.get("probe") and ("$(" in str(t.get("probe")) and "rm " in str(t.get("probe"))):
            errors.append("%s: probe looks destructive" % tid)
        for word in ("deploy ", "rm -", "delete ", "send ", "git push", "launchctl load",
                     "launchctl unload", "kickstart", " > ", ">>"):
            if word in (t.get("probe") or "").lower():
                warnings.append("%s: probe contains %r — probes must be read-only" % (tid, word))

    # reverse-link check: if A lists B as a fallback, B usually lists A
    # Only within one category: a CLI falling back to a web UI is one-way on purpose, but two
    # MCP connectors for the same service should name each other.
    cat = {t["id"]: t.get("category") for t in tools}
    alt_refs = {t["id"]: {a.get("ref") for a in t.get("alternatives", []) if a.get("ref")} for t in tools}
    for a, refs in alt_refs.items():
        for b in refs:
            if b in alt_refs and a not in alt_refs[b] and cat.get(a) == cat.get(b):
                warnings.append("%s falls back to %s, but %s does not point back" % (a, b, b))

    # usage_keys that match nothing in the transcripts
    usage = None
    if "--usage" in sys.argv:
        usage = json.load(open(sys.argv[sys.argv.index("--usage") + 1]))
    else:
        scan = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scan.py")
        if os.path.exists(scan):
            try:
                usage = json.loads(subprocess.run([sys.executable, scan], capture_output=True,
                                                  text=True, timeout=300).stdout)
            except Exception:
                pass
    if usage:
        seen = list(usage.get("tools", {}))
        for t in tools:
            keys = t.get("usage_keys") or []
            if keys and not any(s == k or s.startswith(k) for k in keys for s in seen):
                warnings.append("%s: no usage_keys match any transcript id — typo, or genuinely unused?"
                                % t.get("id"))
        carded = {k for t in tools for k in (t.get("usage_keys") or [])}
        # Built-ins are not services and are deliberately uncarded.
        BUILTIN = {"Bash", "Read", "Write", "Edit", "Glob", "Grep", "ToolSearch", "WebFetch",
                   "WebSearch", "Artifact", "Agent", "Task", "Skill", "TodoWrite", "NotebookEdit",
                   "AskUserQuestion", "SendUserFile", "TaskOutput", "ScheduleWakeup", "Monitor"}
        orphan = [s for s in seen if not any(s == k or s.startswith(k) for k in carded)
                  and usage["tools"][s]["calls"] >= 5
                  and s not in BUILTIN and not s.startswith(("agent:", "skill:"))]
        if orphan:
            warnings.append("%d used tools are in no entry: %s"
                            % (len(orphan), ", ".join(sorted(orphan, key=lambda s: -usage["tools"][s]["calls"])[:8])))

    for w in warnings:
        print("warn  " + w)
    for e in errors:
        print("ERROR " + e)
    print("\n%d tools, %d errors, %d warnings" % (len(tools), len(errors), len(warnings)))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
