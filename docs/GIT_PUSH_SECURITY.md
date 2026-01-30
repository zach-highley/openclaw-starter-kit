# Git Push Security Guard

## The Problem

Your AI pushes to git repos regularly. If it accidentally pushes to a **public** repo, your trade secrets, API keys, or personal data could be exposed. Even if nothing sensitive is in the diff, the AI might use confusing language like "pushed publicly" when it means a private repo — causing unnecessary panic.

## The Solution

`git_push_guard.sh` checks repo visibility before every push:

```bash
#!/bin/bash
# Exit 0 = PRIVATE (safe)
# Exit 1 = PUBLIC (STOP — trigger security confirmation)
# Exit 2 = ERROR (treat as public, be safe)

REPO_DIR="${1:-.}"
cd "$REPO_DIR" || exit 2

REMOTE_URL=$(git remote get-url origin 2>/dev/null)
REPO_SLUG=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]([^/]+/[^/.]+)(\.git)?$|\1|')

VISIBILITY=$(gh repo view "$REPO_SLUG" --json visibility -q '.visibility' 2>/dev/null)

case "$VISIBILITY" in
    PRIVATE) echo "PRIVATE: $REPO_SLUG"; exit 0 ;;
    PUBLIC)  echo "⚠️ PUBLIC: $REPO_SLUG"; exit 1 ;;
    *)       echo "ERROR: unknown"; exit 2 ;;
esac
```

## AGENTS.md Hook

Add to your mid-session enforcement table:

```
| About to git push ANY repo | Repo visibility guard | Run git_push_guard.sh. 
  PUBLIC = STOP + security pre-flight. PRIVATE = safe. ERROR = treat as public. |
```

## Security Pre-Flight (for public repos)

If the guard returns PUBLIC:
1. Scan the diff for personal data (names, emails, tokens, keys)
2. Show the user a summary of what will be pushed
3. Wait for explicit approval
4. Verify passphrase if first sensitive action
5. Only then push

## Language Rule

Never say "pushed publicly" when referring to a private repo. It causes panic. Say "pushed to [repo name]" instead.
