# Check for Multiple OpenClaw Installs (CRITICAL)

**Problem:** OpenClaw can be installed in multiple locations, causing:
- Confusion about which config is active
- Filters/applications running from wrong folder
- Auth token mismatches (1008 errors)
- "Model got worse" symptoms that are actually wrong-install bugs

## How We Fucked Up (2026-02-22)

Eric ran work from `/tmp/openclaw-starter-kit/` instead of `~/.openclaw/workspace/`, causing:
- Stale context from wrong workspace files
- Configuration drift between repos
- Wasted hours debugging non-issues

## Prevention Protocol

### Before ANY task:
```bash
# 1. Check which openclaw is active
which openclaw
# Expected: /opt/homebrew/bin/openclaw

# 2. Verify workspace path
openclaw config get agents.defaults.workspace
# Expected: /Users/zachhighley-gergel/.openclaw/workspace

# 3. Check for competing installs
ls -la ~/.nvm/versions/node/*/bin/openclaw 2>/dev/null
ls -la /usr/local/bin/openclaw 2>/dev/null
ls -la /opt/homebrew/bin/openclaw 2>/dev/null

# 4. Verify current working directory matches workspace
pwd
# Should match config get output from #2
```

### If you find multiple installs:
1. **Use the canonical path only:** `/opt/homebrew/bin/openclaw`
2. **Workspace is non-negotiable:** `~/.openclaw/workspace/`
3. **Never commit/work from temp dirs** like `/tmp/dashboard-check/` or `/tmp/openclaw-starter-kit/` for operational tasks
4. Temp clones are for READ-ONLY inspection only

## Root Cause Pattern

Common multi-install scenarios:
- `npm install -g openclaw` → installs to nvm prefix
- `brew install` → installs to /opt/homebrew/bin/
- Manual clone → installs elsewhere

**Fix:** Always use the canonical `/opt/homebrew/bin/openclaw` and set `NPM_CONFIG_PREFIX` before any npm operations.

## Quick Diagnostic Script

Run before starting any significant work:
```bash
echo "=== OpenClaw Install Check ===" && \
which openclaw && \
openclaw --version && \
openclaw config get agents.defaults.workspace && \
echo "=== Workspace Files ===" && \
ls ~/.openclaw/workspace/*.md | head -5 && \
echo "=== If any mismatch, STOP and fix before proceeding ==="
```

## If You're in the Wrong Folder...

1. `cd ~/.openclaw/workspace`
2. Re-read the canonical files: `AGENTS.md`, `SOUL.md`, `MEMORY.md`, `USER.md`
3. Restart your mental context — fresh session, don't carry over assumptions
4. Verify: `pwd` should show the workspace path