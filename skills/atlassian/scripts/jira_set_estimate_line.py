#!/usr/bin/env python3
"""Append or replace 'Estimate: XX' line at end of Jira issue description.

Usage:
  jira_set_estimate_line.py --pair DD-127=3 --pair DD-128=5
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

ESTIMATE_RE = re.compile(r"^Estimate:\s*\d+\s*$")


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr.strip()}"
        )
    return proc.stdout


def parse_pair(raw: str) -> tuple[str, int]:
    if "=" not in raw:
        raise ValueError(f"Invalid --pair '{raw}'. Expected KEY=POINTS")

    key, points_raw = raw.split("=", 1)
    key = key.strip()
    points_raw = points_raw.strip()

    if not key:
        raise ValueError(f"Invalid --pair '{raw}': missing issue key")

    try:
        points = int(points_raw)
    except ValueError as exc:
        raise ValueError(f"Invalid points in --pair '{raw}'") from exc

    if points <= 0:
        raise ValueError(f"Points must be > 0 in --pair '{raw}'")

    return key, points


def get_description(key: str) -> dict:
    out = run(
        [
            "acli",
            "jira",
            "workitem",
            "view",
            key,
            "--fields",
            "key,description",
            "--json",
        ]
    )
    issue = json.loads(out)
    description = issue.get("fields", {}).get("description")
    if not isinstance(description, dict):
        return {"version": 1, "type": "doc", "content": []}
    if description.get("type") != "doc":
        return {"version": 1, "type": "doc", "content": []}
    if not isinstance(description.get("content"), list):
        description["content"] = []
    return description


def paragraph_text(block: dict) -> str:
    if block.get("type") != "paragraph":
        return ""
    bits = []
    for node in block.get("content", []):
        if node.get("type") == "text":
            bits.append(node.get("text", ""))
    return "".join(bits).strip()


def update_estimate(description: dict, points: int) -> dict:
    cleaned = []
    for block in description.get("content", []):
        if ESTIMATE_RE.fullmatch(paragraph_text(block)):
            continue
        cleaned.append(block)

    cleaned.append(
        {
            "type": "paragraph",
            "content": [{"type": "text", "text": f"Estimate: {points}"}],
        }
    )

    return {"version": 1, "type": "doc", "content": cleaned}


def apply_description(key: str, description: dict, dry_run: bool) -> None:
    payload = {"issues": [key], "description": description}

    if dry_run:
        print(f"[DRY-RUN] Would set estimate on {key}")
        return

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(payload, tmp, ensure_ascii=False, indent=2)
        tmp_path = tmp.name

    try:
        run(["acli", "jira", "workitem", "edit", "--from-json", tmp_path, "--yes"])
        print(f"Updated {key}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pair",
        action="append",
        required=True,
        help="Estimate mapping in KEY=POINTS format. Can be repeated.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    for raw in args.pair:
        key, points = parse_pair(raw)
        desc = get_description(key)
        next_desc = update_estimate(desc, points)
        apply_description(key, next_desc, args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
