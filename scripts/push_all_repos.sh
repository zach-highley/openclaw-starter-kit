#!/bin/bash
# push_all_repos.sh — Push ALL repos every time. Never push manually.
# Commandment #15: "Push" means ALL repos. No exceptions.
#
# Usage: bash scripts/push_all_repos.sh "commit message"
# Customize the REPOS array below for your setup.

set -e

# Define your repos here: "path:branch:name"
REPOS=(
  "$HOME/.openclaw/workspace:master:Workspace"
  # "$HOME/my-dashboard:master:Dashboard"
  # "/tmp/my-public-repo:main:Public Repo"
)

MSG="${1:-chore: auto-push}"
TOTAL=${#REPOS[@]}
CURRENT=0

echo "🔄 Pushing $TOTAL repos..."

for entry in "${REPOS[@]}"; do
  IFS=':' read -r path branch name <<< "$entry"
  CURRENT=$((CURRENT + 1))
  echo ""
  echo "📦 [$CURRENT/$TOTAL] $name → $branch"
  
  cd "$path" 2>/dev/null || { echo "  ⚠️ Path not found: $path"; continue; }
  
  if git diff --quiet && git diff --cached --quiet; then
    echo "  ✅ Clean — nothing to commit"
  else
    git add -A
    git commit -m "$MSG" || true
  fi
  
  git push origin "$branch" 2>&1 && echo "  ✅ Pushed" || echo "  ⚠️ Push failed"
done

echo ""
echo "✅ All $TOTAL repos checked and pushed."
