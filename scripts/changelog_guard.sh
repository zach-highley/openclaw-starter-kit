#!/bin/bash
# changelog_guard.sh — require CHANGELOG.md updates when docs/ or scripts/ change
#
# Why this exists:
# - Docs/scripts drift quickly in AI-assisted repos.
# - The changelog is the single place readers can trust.
#
# Modes:
#   --staged           Check staged files (for pre-commit hooks)
#   --base <ref>       Base ref for range diff (for CI) (default: origin/main or main)
#   --head <ref>       Head ref for range diff (default: HEAD)
#   --changelog <path> Changelog file path (default: CHANGELOG.md)
#   --paths <csv>      Comma-separated watched prefixes (default: docs/,scripts/)
#
# Bypass (not recommended):
#   SKIP_CHANGELOG_GUARD=1 git commit ...

set -euo pipefail

MODE="range"
BASE=""
HEAD="HEAD"
CHANGELOG_PATH="CHANGELOG.md"
WATCH_PATHS_CSV="docs/,scripts/"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/changelog_guard.sh --staged
  bash scripts/changelog_guard.sh --base origin/main --head HEAD

Options:
  --staged
  --base <ref>
  --head <ref>
  --changelog <path>
  --paths <csv>    e.g. "docs/,scripts/,templates/"
  -h, --help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --staged)
      MODE="staged"
      shift
      ;;
    --base)
      BASE="${2:-}"
      shift 2
      ;;
    --head)
      HEAD="${2:-}"
      shift 2
      ;;
    --changelog)
      CHANGELOG_PATH="${2:-}"
      shift 2
      ;;
    --paths)
      WATCH_PATHS_CSV="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: Unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "${SKIP_CHANGELOG_GUARD:-}" == "1" ]]; then
  echo "SKIP_CHANGELOG_GUARD=1 set; skipping changelog guard."
  exit 0
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$REPO_ROOT" ]]; then
  echo "ERROR: Not in a git repo." >&2
  exit 2
fi
cd "$REPO_ROOT"

# Normalize watched prefixes.
IFS=',' read -r -a WATCH_PATHS <<< "$WATCH_PATHS_CSV"
for i in "${!WATCH_PATHS[@]}"; do
  p="${WATCH_PATHS[$i]}"
  # Ensure trailing slash so prefix match is unambiguous.
  if [[ -n "$p" && "${p: -1}" != "/" ]]; then
    WATCH_PATHS[$i]="$p/"
  fi
done

DIFF_FILTER="ACMR"
CHANGED_FILES=""

if [[ "$MODE" == "staged" ]]; then
  CHANGED_FILES="$(git diff --cached --name-only --diff-filter="$DIFF_FILTER" || true)"
else
  if [[ -z "$BASE" ]]; then
    if git show-ref --quiet refs/remotes/origin/main; then
      BASE="origin/main"
    elif git show-ref --quiet refs/heads/main; then
      BASE="main"
    else
      # Best-effort fallback: compare against the previous commit.
      BASE="HEAD~1"
    fi
  fi

  # Use triple-dot (merge-base) diff for PR-style checks.
  CHANGED_FILES="$(git diff --name-only --diff-filter="$DIFF_FILTER" "$BASE...$HEAD" || true)"
fi

if [[ -z "$CHANGED_FILES" ]]; then
  exit 0
fi

# Determine whether any watched path changed (excluding the changelog itself).
NEEDS_CHANGELOG=0
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  [[ "$f" == "$CHANGELOG_PATH" ]] && continue

  for p in "${WATCH_PATHS[@]}"; do
    [[ -z "$p" ]] && continue
    if [[ "$f" == "$p"* ]]; then
      NEEDS_CHANGELOG=1
      break
    fi
  done

  [[ "$NEEDS_CHANGELOG" -eq 1 ]] && break
done <<< "$CHANGED_FILES"

if [[ "$NEEDS_CHANGELOG" -eq 0 ]]; then
  exit 0
fi

if echo "$CHANGED_FILES" | grep -qxF "$CHANGELOG_PATH"; then
  exit 0
fi

cat <<EOF
ERROR: Changelog required.

You changed at least one file under: ${WATCH_PATHS_CSV}
…but did not update: ${CHANGELOG_PATH}

Fix:
  1) Add a short entry under "[Unreleased]" in ${CHANGELOG_PATH}
  2) Stage it (git add ${CHANGELOG_PATH})
  3) Re-run your commit

Bypass (not recommended):
  SKIP_CHANGELOG_GUARD=1 git commit ...
EOF

exit 1
