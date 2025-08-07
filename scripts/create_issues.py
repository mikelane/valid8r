#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO = os.environ.get("GITHUB_REPOSITORY", "mikelane/valid8r")
TOKEN = os.environ.get("GITHUB_TOKEN")
ISSUES_DIR = Path(__file__).resolve().parent / "issues"
API_BASE = "https://api.github.com"

TITLE_PREFIX = "Title:"
LABELS_PREFIX = "Labels:"


@dataclass
class IssueSpec:
    title: str
    body: str
    labels: list[str]


def parse_issue_file(path: Path) -> IssueSpec:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines:
        raise ValueError(f"Issue file {path} is empty")

    # Parse title
    if not lines[0].startswith(TITLE_PREFIX):
        raise ValueError(
            f"First line of {path.name} must start with '{TITLE_PREFIX} '"
        )
    title = lines[0][len(TITLE_PREFIX) :].strip()

    # Parse labels (optional)
    labels: list[str] = []
    body_start_index = 1
    if len(lines) >= 2 and lines[1].startswith(LABELS_PREFIX):
        raw_labels = lines[1][len(LABELS_PREFIX) :].strip()
        labels = [lbl.strip() for lbl in raw_labels.split(",") if lbl.strip()]
        body_start_index = 2

    # Remaining is the body
    body = "\n".join(lines[body_start_index:]).strip()
    if not body:
        raise ValueError(f"Body missing in issue file {path}")

    return IssueSpec(title=title, body=body, labels=labels)


def api_request(method: str, url: str, token: str, data: dict[str, Any] | None = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
        "User-Agent": "valid8r-issue-bot",
    }
    req = urllib.request.Request(url=url, method=method, headers=headers)
    if data is not None:
        payload = json.dumps(data).encode("utf-8")
    else:
        payload = None

    try:
        with urllib.request.urlopen(req, data=payload) as resp:
            body = resp.read().decode("utf-8")
            if not body:
                return None
            return json.loads(body)
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"GitHub API error {e.code} for {url}: {msg}") from e


def get_existing_issue_titles(repo: str, token: str) -> set[str]:
    titles: set[str] = set()
    page = 1
    while True:
        url = f"{API_BASE}/repos/{repo}/issues?state=all&per_page=100&page={page}"
        results = api_request("GET", url, token)
        if not results:
            break
        for item in results:
            # Skip PRs (issues API returns PRs too)
            if "pull_request" in item:
                continue
            title = item.get("title", "")
            if title:
                titles.add(title)
        if len(results) < 100:
            break
        page += 1
    return titles


def ensure_labels(repo: str, token: str, labels: list[str]) -> None:
    if not labels:
        return
    url = f"{API_BASE}/repos/{repo}/labels?per_page=100"
    existing = api_request("GET", url, token)
    existing_names = {lbl["name"] for lbl in existing}
    for name in labels:
        if name in existing_names:
            continue
        data = {"name": name}
        api_request("POST", f"{API_BASE}/repos/{repo}/labels", token, data)
        print(f"Created missing label: {name}")


def create_issue(repo: str, token: str, spec: IssueSpec) -> int:
    data: dict[str, Any] = {
        "title": spec.title,
        "body": spec.body,
    }
    if spec.labels:
        data["labels"] = spec.labels
    result = api_request("POST", f"{API_BASE}/repos/{repo}/issues", token, data)
    number = result.get("number")
    print(f"Created issue #{number}: {spec.title}")
    return int(number)


def main() -> int:
    if TOKEN is None:
        print("Error: GITHUB_TOKEN environment variable is required.", file=sys.stderr)
        return 2

    if not ISSUES_DIR.exists():
        print(f"Error: issues directory not found: {ISSUES_DIR}", file=sys.stderr)
        return 2

    issue_files = sorted(ISSUES_DIR.glob("*.md"))
    if not issue_files:
        print(f"No issue files found in {ISSUES_DIR}")
        return 0

    existing_titles = get_existing_issue_titles(REPO, TOKEN)

    # Collect all labels to ensure they exist
    all_labels: set[str] = set()
    specs: list[IssueSpec] = []
    for path in issue_files:
        spec = parse_issue_file(path)
        specs.append(spec)
        all_labels.update(spec.labels)

    ensure_labels(REPO, TOKEN, sorted(all_labels))

    created = 0
    skipped = 0
    for spec in specs:
        if spec.title in existing_titles:
            print(f"Skipping existing issue: {spec.title}")
            skipped += 1
            continue
        create_issue(REPO, TOKEN, spec)
        created += 1

    print(f"Done. Created: {created}, Skipped: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())