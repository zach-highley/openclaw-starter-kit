# Changelog guard (anti-bloat consistency)

In AI-assisted repos, docs and scripts change constantly.
To keep the project understandable for humans, this starter-kit includes an **optional guard** that **requires** updating `CHANGELOG.md` whenever you change:

- `docs/`
- `scripts/`

The goal is not bureaucracy — it’s making sure changes stay discoverable.

---

## What’s included

- `scripts/changelog_guard.sh`
  - Supports **pre-commit** checks (`--staged`) and **CI** checks (`--base/--head`).
- `templates/githooks/pre-commit`
  - A minimal Git hook template that calls the guard.

---

## Enable locally (recommended)

Git does not version-control `.git/hooks/`, so the usual pattern is to use a repo-local hooks directory.

```bash
mkdir -p .githooks
cp templates/githooks/pre-commit .githooks/pre-commit
chmod +x .githooks/pre-commit

git config core.hooksPath .githooks
```

Now a commit that stages changes in `docs/` or `scripts/` without staging `CHANGELOG.md` will fail.

---

## Use in CI (example)

In GitHub Actions (or any CI), run the guard against the PR merge-base:

```bash
# Make sure the base branch is available locally
git fetch --no-tags origin main:refs/remotes/origin/main

bash scripts/changelog_guard.sh --base origin/main --head HEAD
```

If you use a different default branch, replace `main` accordingly.

---

## Emergency bypass

You can bypass the guard (not recommended) with:

```bash
SKIP_CHANGELOG_GUARD=1 git commit -m "..."
```

If you bypass, add the changelog entry immediately after.
