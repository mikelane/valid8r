#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ISSUES_DIR = Path(__file__).resolve().parent / "issues"
REPO = os.environ.get("GITHUB_REPOSITORY")  # optional; gh can infer from git remote

TITLE_PREFIX = "Title:"
LABELS_PREFIX = "Labels:"


@dataclass
class IssueSpec:
    title: str
    body: str
    labels: list[str]


def run_gh(args: list[str]) -> subprocess.CompletedProcess[str]:
    cmd = ["gh", *args]
    if REPO:
        cmd.extend(["--repo", REPO])
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def ensure_gh_available() -> None:
    proc = subprocess.run(["gh", "--version"], capture_output=True, text=True)
    if proc.returncode != 0:
        print("Error: gh CLI not found. Please install and authenticate: https://cli.github.com/", file=sys.stderr)
        sys.exit(2)

    # Check auth status
    status = run_gh(["auth", "status"])  # non-zero if not authed
    if status.returncode != 0:
        print("Error: gh CLI is not authenticated. Run 'gh auth login' and try again.", file=sys.stderr)
        sys.exit(2)


def parse_issue_file(path: Path) -> IssueSpec:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines:
        raise ValueError(f"Issue file {path} is empty")

    if not lines[0].startswith(TITLE_PREFIX):
        raise ValueError(f"First line must start with '{TITLE_PREFIX} '")
    title = lines[0][len(TITLE_PREFIX) :].strip()

    labels: list[str] = []
    body_start_index = 1
    if len(lines) >= 2 and lines[1].startswith(LABELS_PREFIX):
        raw_labels = lines[1][len(LABELS_PREFIX) :].strip()
        labels = [lbl.strip() for lbl in raw_labels.split(",") if lbl.strip()]
        body_start_index = 2

    body = "\n".join(lines[body_start_index:]).strip()
    if not body:
        raise ValueError(f"Body missing in issue file {path}")

    return IssueSpec(title=title, body=body, labels=labels)


def list_issue_titles() -> set[str]:
    proc = run_gh(["issue", "list", "--state", "all", "--json", "title", "--limit", "1000"])
    if proc.returncode != 0:
        raise RuntimeError(f"Failed to list issues: {proc.stderr}")
    try:
        items = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse gh output: {e}\nOutput: {proc.stdout}")
    titles = {item.get("title", "") for item in items if isinstance(item, dict)}
    return {t for t in titles if t}


def ensure_labels_exist(labels: list[str]) -> None:
    if not labels:
        return
    proc = run_gh(["label", "list", "--json", "name", "--limit", "1000"])
    if proc.returncode != 0:
        # Not critical; attempt creation blindly later
        existing = set()
    else:
        try:
            existing_items = json.loads(proc.stdout)
            existing = {item.get("name", "") for item in existing_items if isinstance(item, dict)}
        except json.JSONDecodeError:
            existing = set()

    for name in labels:
        if name in existing:
            continue
        create = run_gh(["label", "create", name])
        if create.returncode != 0 and "already exists" not in create.stderr.lower():
            print(f"Warning: failed to create label '{name}': {create.stderr}")


def create_issue(spec: IssueSpec) -> None:
    # Write body to a temp file
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as tf:
        tf.write(spec.body)
        body_path = tf.name

    args = [
        "issue",
        "create",
        "--title",
        spec.title,
        "--body-file",
        body_path,
    ]
    for label in spec.labels:
        args.extend(["--label", label])

    proc = run_gh(args)
    if proc.returncode != 0:
        raise RuntimeError(f"Failed to create issue '{spec.title}': {proc.stderr}")
    print(f"Created: {spec.title}\n{proc.stdout.strip()}")


def main() -> int:
    ensure_gh_available()

    if not ISSUES_DIR.exists():
        print(f"Error: issues directory not found: {ISSUES_DIR}", file=sys.stderr)
        return 2

    files = sorted(ISSUES_DIR.glob("*.md"))
    if not files:
        print(f"No issue files found in {ISSUES_DIR}")
        return 0

    specs = [parse_issue_file(p) for p in files]

    # Ensure labels
    all_labels: list[str] = sorted({lbl for spec in specs for lbl in spec.labels})
    ensure_labels_exist(all_labels)

    # Skip duplicates by title
    existing_titles = list_issue_titles()

    created = 0
    skipped = 0
    for spec in specs:
        if spec.title in existing_titles:
            print(f"Skipping existing: {spec.title}")
            skipped += 1
            continue
        create_issue(spec)
        created += 1

    print(f"Done. Created: {created}, Skipped: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())