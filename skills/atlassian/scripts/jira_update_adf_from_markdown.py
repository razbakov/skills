#!/usr/bin/env python3
"""Update Jira descriptions from markdown files as rich ADF.

Usage:
  jira_update_adf_from_markdown.py --pair DD-127=docs/issues/DD-126-audience.md
  jira_update_adf_from_markdown.py \
    --pair DD-127=/abs/path/one.md \
    --pair DD-128=/abs/path/two.md
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr.strip()}"
        )
    return proc.stdout


def parse_markdown(md_text: str) -> str:
    """Strip YAML frontmatter and return markdown body."""
    if not md_text.startswith("---\n"):
        return md_text

    end = md_text.find("\n---\n", 4)
    if end == -1:
        return md_text

    return md_text[end + 5 :]


def flush_paragraph(content: list[dict], paragraph_lines: list[str]) -> None:
    if not paragraph_lines:
        return
    text = " ".join(line.strip() for line in paragraph_lines).strip()
    paragraph_lines.clear()
    if not text:
        return
    content.append(
        {
            "type": "paragraph",
            "content": [{"type": "text", "text": text}],
        }
    )


def flush_bullets(content: list[dict], bullets: list[str]) -> None:
    if not bullets:
        return

    list_items = []
    for item in bullets:
        item = item.strip()
        if not item:
            continue
        list_items.append(
            {
                "type": "listItem",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": item}],
                    }
                ],
            }
        )

    bullets.clear()
    if not list_items:
        return

    content.append({"type": "bulletList", "content": list_items})


def markdown_to_adf(markdown_body: str) -> dict:
    lines = markdown_body.splitlines()
    content: list[dict] = []
    paragraph_lines: list[str] = []
    bullets: list[str] = []

    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()

        # Skip H1. Summary/title should already be in Jira summary.
        if stripped.startswith("# "):
            flush_paragraph(content, paragraph_lines)
            flush_bullets(content, bullets)
            continue

        if stripped.startswith("## "):
            flush_paragraph(content, paragraph_lines)
            flush_bullets(content, bullets)
            content.append(
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": stripped[3:].strip()}],
                }
            )
            continue

        if stripped.startswith("### "):
            flush_paragraph(content, paragraph_lines)
            flush_bullets(content, bullets)
            content.append(
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": stripped[4:].strip()}],
                }
            )
            continue

        if stripped.startswith("- "):
            flush_paragraph(content, paragraph_lines)
            bullets.append(stripped[2:].strip())
            continue

        if bullets and (line.startswith("  ") or line.startswith("\t")):
            bullets[-1] = f"{bullets[-1]} {stripped}".strip()
            continue

        if stripped == "":
            flush_paragraph(content, paragraph_lines)
            flush_bullets(content, bullets)
            continue

        flush_bullets(content, bullets)
        paragraph_lines.append(line)

    flush_paragraph(content, paragraph_lines)
    flush_bullets(content, bullets)

    return {"version": 1, "type": "doc", "content": content}


def parse_pair(raw: str) -> tuple[str, Path]:
    if "=" not in raw:
        raise ValueError(f"Invalid --pair '{raw}'. Expected KEY=/path/file.md")
    key, file_path = raw.split("=", 1)
    key = key.strip()
    path = Path(file_path.strip()).expanduser()
    if not key:
        raise ValueError(f"Invalid --pair '{raw}': missing key")
    if not path.exists():
        raise ValueError(f"File not found for --pair '{raw}'")
    return key, path


def update_issue_description(issue_key: str, adf: dict, dry_run: bool) -> None:
    payload = {"issues": [issue_key], "description": adf}

    if dry_run:
        print(f"[DRY-RUN] Would update {issue_key}")
        return

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(payload, tmp, ensure_ascii=False, indent=2)
        tmp_path = tmp.name

    try:
        run(["acli", "jira", "workitem", "edit", "--from-json", tmp_path, "--yes"])
        print(f"Updated {issue_key}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pair",
        action="append",
        required=True,
        help="Issue mapping in KEY=/path/file.md format. Can be repeated.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    pairs: list[tuple[str, Path]] = []
    for raw in args.pair:
        pairs.append(parse_pair(raw))

    for issue_key, md_path in pairs:
        md = md_path.read_text(encoding="utf-8")
        body = parse_markdown(md)
        adf = markdown_to_adf(body)
        update_issue_description(issue_key, adf, args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
