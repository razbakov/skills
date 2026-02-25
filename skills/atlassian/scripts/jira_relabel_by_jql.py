#!/usr/bin/env python3
"""Relabel Jira issues returned by JQL.

Usage:
  jira_relabel_by_jql.py \
    --jql 'project = DD AND labels = old-label' \
    --from-label old-label \
    --to-label new-label \
    --yes
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr.strip()}"
        )
    return proc.stdout


def search_keys(jql: str) -> list[str]:
    out = run(
        [
            "acli",
            "jira",
            "workitem",
            "search",
            "--jql",
            jql,
            "--fields",
            "key,summary,labels",
            "--json",
        ]
    )
    data = json.loads(out)
    keys = []
    for row in data:
        key = row.get("key")
        if isinstance(key, str) and key:
            keys.append(key)
    return keys


def relabel(key: str, old_label: str, new_label: str, dry_run: bool) -> None:
    if dry_run:
        print(f"[DRY-RUN] Would relabel {key}: -{old_label} +{new_label}")
        return

    run(
        [
            "acli",
            "jira",
            "workitem",
            "edit",
            "--key",
            key,
            "--remove-labels",
            old_label,
            "--labels",
            new_label,
            "--yes",
        ]
    )
    print(f"Relabeled {key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jql", required=True)
    parser.add_argument("--from-label", required=True)
    parser.add_argument("--to-label", required=True)
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    keys = search_keys(args.jql)
    if not keys:
        print("No issues found for JQL.")
        return 0

    print("Matched issues:")
    for key in keys:
        print(f"- {key}")

    should_run = args.yes
    if not should_run and not args.dry_run:
        reply = input("Proceed with relabeling these issues? [y/N]: ").strip().lower()
        should_run = reply in {"y", "yes"}

    if not should_run and not args.dry_run:
        print("Aborted.")
        return 1

    for key in keys:
        relabel(key, args.from_label, args.to_label, args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
