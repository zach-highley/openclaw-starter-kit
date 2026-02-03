#!/usr/bin/env python3
"""Lightweight GitHub issue triage loop (safe).

This script is intentionally conservative:
- It ONLY reads issues by default (dry-run).
- It will ONLY comment or open PRs when run with --apply.
- It will ONLY attempt an "autofix" when BOTH:
  - autofix.enabled=true in config, AND
  - the issue has a label matching an autofix rule.

Requires:
- gh CLI authenticated (GITHUB_TOKEN or `gh auth login`)
- git

Config:
- TOML file (see config/examples/issue-triage.toml)

"Yoda (automation bot)" is a signature inside comments/commits; the GitHub user
that actually posts is whichever account your GH token belongs to.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib  # py>=3.11
except Exception:  # pragma: no cover
    tomllib = None


@dataclass
class Config:
    repo: str
    default_branch: str
    git_name: str
    git_email: str
    comment_signature: str
    autofix_enabled: bool
    autofix_rules: list[dict]


DOCS_HINT_RE = re.compile(r"\b(doc|docs|readme|documentation|typo|spelling|grammar)\b", re.IGNORECASE)


def run(cmd: list[str], *, cwd: Path | None = None, capture: bool = False, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        check=check,
    )


def load_config(path: Path) -> Config:
    if tomllib is None:
        raise RuntimeError("tomllib not available. Use Python 3.11+.")
    raw = tomllib.loads(path.read_text())

    repo = raw.get("repo", {}).get("full_name")
    if not repo:
        raise ValueError("Config missing repo.full_name")

    default_branch = raw.get("repo", {}).get("default_branch", "main")

    bot = raw.get("bot", {})
    git_name = bot.get("git_name", "Yoda (automation bot)")
    git_email = bot.get("git_email", "yoda-bot@users.noreply.github.com")
    comment_signature = bot.get("comment_signature", "— Yoda (automation bot)")

    autofix = raw.get("autofix", {})
    autofix_enabled = bool(autofix.get("enabled", False))
    rules = raw.get("autofix", {}).get("rules", [])
    if rules is None:
        rules = []

    if not isinstance(rules, list):
        raise ValueError("autofix.rules must be an array")

    return Config(
        repo=repo,
        default_branch=default_branch,
        git_name=git_name,
        git_email=git_email,
        comment_signature=comment_signature,
        autofix_enabled=autofix_enabled,
        autofix_rules=rules,
    )


def gh_json(repo: str, args: list[str]) -> object:
    cp = run(["gh", "-R", repo, *args], capture=True)
    return json.loads(cp.stdout)


def list_open_issues(repo: str, limit: int) -> list[dict]:
    # Includes labels and author; keep small + safe.
    data = gh_json(
        repo,
        [
            "issue",
            "list",
            "--state",
            "open",
            "--limit",
            str(limit),
            "--json",
            "number,title,body,labels,url,author,createdAt,updatedAt",
        ],
    )
    assert isinstance(data, list)
    return data


def issue_labels(issue: dict) -> set[str]:
    labels = issue.get("labels") or []
    out: set[str] = set()
    for l in labels:
        name = l.get("name")
        if name:
            out.add(name)
    return out


def classify_issue(issue: dict) -> str:
    title = issue.get("title") or ""
    body = issue.get("body") or ""
    labels = issue_labels(issue)

    if "bot:ignore" in labels or "triage:ignore" in labels:
        return "ignore"

    if any(l.startswith("autofix:") for l in labels):
        return "autofix_candidate"

    if "documentation" in labels or "docs" in labels:
        return "docs"

    if DOCS_HINT_RE.search(title) or DOCS_HINT_RE.search(body):
        return "docs"

    return "needs_human"


def build_yoda_comment(issue: dict, *, kind: str, signature: str) -> str:
    number = issue.get("number")
    title = issue.get("title") or "(no title)"
    url = issue.get("url") or ""

    lines: list[str] = []
    lines.append(f"Automated triage, this is. Issue **#{number}**: _{title}_")
    lines.append("")

    if kind == "docs":
        lines.append("Docs/quick-fix scent, I detect.")
        lines.append("")
        lines.append("To move fast, answer these, you can:")
        lines.append("- Which file/section should change? (link + heading)")
        lines.append("- Desired wording / example output, what is?")
        lines.append("- If a typo: **current text** and **correct text**, paste")
        lines.append("")
        lines.append("If you want the bot to open a PR, add an `autofix:...` label that matches a configured rule.")
    else:
        lines.append("Non-trivial it may be. Clarify, we must.")
        lines.append("")
        lines.append("Help me help you:")
        lines.append("- Steps to reproduce")
        lines.append("- Expected vs actual behavior")
        lines.append("- Environment (OS, version, config)")
        lines.append("- Logs/screenshots, if you have")

    lines.append("")
    lines.append("_Note: This comment was generated by automation. It is **not** Zach speaking._")
    if url:
        lines.append(url)
    lines.append("")
    lines.append(signature)

    return "\n".join(lines)


def gh_comment(repo: str, number: int, body: str, *, apply: bool) -> None:
    if not apply:
        print(f"[dry-run] Would comment on issue #{number} in {repo}:")
        print(body)
        return

    run(["gh", "-R", repo, "issue", "comment", str(number), "--body", body])


def ensure_clean_git_repo(repo_dir: Path) -> None:
    cp = run(["git", "status", "--porcelain"], cwd=repo_dir, capture=True)
    if cp.stdout.strip():
        raise RuntimeError(
            "Working tree not clean. Commit/stash changes before running triage autofix."
        )


def run_autofix_rule(
    *,
    repo_dir: Path,
    cfg: Config,
    issue: dict,
    rule: dict,
    apply: bool,
) -> None:
    number = int(issue["number"])
    title = issue.get("title") or ""

    branch = f"triage/issue-{number}"
    pr_title = f"Fix #{number}: {title}".strip()
    pr_body = "\n".join(
        [
            f"Automated fix for issue #{number}.",
            "",
            "This change was generated by automation (Yoda bot).",
            "Please review carefully before merging.",
            "",
            f"Closes #{number}",
        ]
    )

    commands = rule.get("commands") or []
    if not isinstance(commands, list) or not commands:
        raise ValueError("autofix rule missing commands[]")

    label = rule.get("issue_label") or rule.get("label")
    name = rule.get("name") or label or "(unnamed rule)"

    print(f"Autofix rule matched: {name} (issue #{number})")

    if not apply:
        print(f"[dry-run] Would create branch {branch}, run commands:")
        for c in commands:
            print(f"  - {c}")
        print("[dry-run] Would commit + push + open PR.")
        return

    ensure_clean_git_repo(repo_dir)

    # create/checkout branch from default branch
    run(["git", "fetch", "origin", cfg.default_branch], cwd=repo_dir)
    run(["git", "checkout", cfg.default_branch], cwd=repo_dir)
    run(["git", "pull", "--ff-only"], cwd=repo_dir)
    run(["git", "checkout", "-B", branch], cwd=repo_dir)

    # run commands
    for c in commands:
        print(f"Running: {c}")
        run(["bash", "-lc", c], cwd=repo_dir)

    # verify there is a diff
    diff = run(["git", "status", "--porcelain"], cwd=repo_dir, capture=True).stdout.strip()
    if not diff:
        print("No changes produced by autofix commands; skipping PR.")
        return

    run(["git", "add", "-A"], cwd=repo_dir)

    # commit with bot identity
    run(
        [
            "git",
            "-c",
            f"user.name={cfg.git_name}",
            "-c",
            f"user.email={cfg.git_email}",
            "commit",
            "-m",
            pr_title,
        ],
        cwd=repo_dir,
    )

    run(["git", "push", "-u", "origin", branch], cwd=repo_dir)

    # open PR
    run(
        [
            "gh",
            "-R",
            cfg.repo,
            "pr",
            "create",
            "--title",
            pr_title,
            "--body",
            pr_body,
            "--base",
            cfg.default_branch,
            "--head",
            branch,
        ],
        cwd=repo_dir,
    )


def pick_autofix_rule(cfg: Config, issue: dict) -> dict | None:
    labels = issue_labels(issue)

    for rule in cfg.autofix_rules:
        label = rule.get("issue_label") or rule.get("label")
        if label and label in labels:
            return rule
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Lightweight GitHub issue triage loop")
    ap.add_argument(
        "--config",
        type=Path,
        default=Path("issue-triage.toml"),
        help="Path to TOML config (default: ./issue-triage.toml)",
    )
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Do not write anything (default)")
    mode.add_argument("--apply", action="store_true", help="Post comments / open PRs")
    ap.add_argument("--limit", type=int, default=25, help="Max open issues to fetch")
    ap.add_argument("--max-actions", type=int, default=10, help="Max issues to act on")

    args = ap.parse_args()

    apply = bool(args.apply)

    cfg_path: Path = args.config
    if not cfg_path.exists():
        print(
            f"Config not found: {cfg_path}. Copy config/examples/issue-triage.toml and edit repo.full_name.",
            file=sys.stderr,
        )
        return 2

    cfg = load_config(cfg_path)

    repo_dir = Path.cwd()

    issues = list_open_issues(cfg.repo, args.limit)
    print(f"Open issues in {cfg.repo}: {len(issues)}")

    actions = 0
    for issue in issues:
        if actions >= args.max_actions:
            break

        number = int(issue["number"])
        title = issue.get("title") or ""
        kind = classify_issue(issue)
        labels = sorted(issue_labels(issue))
        print(f"- #{number} [{kind}] {title} ({', '.join(labels)})")

        if kind == "ignore":
            continue

        if kind == "autofix_candidate" and cfg.autofix_enabled:
            rule = pick_autofix_rule(cfg, issue)
            if rule is not None:
                run_autofix_rule(repo_dir=repo_dir, cfg=cfg, issue=issue, rule=rule, apply=apply)
                actions += 1
                continue

        # Otherwise: comment with questions
        if kind in {"docs", "autofix_candidate"}:
            comment_kind = "docs"
        else:
            comment_kind = "needs_human"

        comment = build_yoda_comment(issue, kind=comment_kind, signature=cfg.comment_signature)
        gh_comment(cfg.repo, number, comment, apply=apply)
        actions += 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
