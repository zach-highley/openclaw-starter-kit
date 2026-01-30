#!/bin/bash
# git_push_guard.sh — Verify repo visibility before pushing
# Run before any git push to confirm private/public status
#
# Exit 0 = private (safe to push)
# Exit 1 = public (STOP — needs security confirmation)  
# Exit 2 = error (couldn't determine — treat as public)

REPO_DIR="${1:-.}"
cd "$REPO_DIR" || exit 2

REMOTE_URL=$(git remote get-url origin 2>/dev/null)
if [ -z "$REMOTE_URL" ]; then
    echo "ERROR: No git remote found"
    exit 2
fi

REPO_SLUG=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]([^/]+/[^/.]+)(\.git)?$|\1|')

if [ -z "$REPO_SLUG" ]; then
    echo "ERROR: Could not parse repo slug from $REMOTE_URL"
    exit 2
fi

VISIBILITY=$(gh repo view "$REPO_SLUG" --json visibility -q '.visibility' 2>/dev/null)

if [ "$VISIBILITY" = "PRIVATE" ]; then
    echo "PRIVATE: $REPO_SLUG — safe to push"
    exit 0
elif [ "$VISIBILITY" = "PUBLIC" ]; then
    echo "⚠️  PUBLIC REPO: $REPO_SLUG — SECURITY CONFIRMATION REQUIRED"
    exit 1
else
    echo "ERROR: Could not determine visibility for $REPO_SLUG (got: $VISIBILITY)"
    exit 2
fi
