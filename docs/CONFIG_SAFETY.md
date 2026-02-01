# Config Safety — Avoiding Auth Crashes on Config Changes

## The Problem

When using `config.apply` or `config.patch` to modify auth profiles, a race condition can cause the gateway to restart multiple times in rapid succession. This corrupts the auth state and leaves the agent unable to authenticate.

### What Happens

1. `config.apply` writes the config file
2. The filesystem watcher detects the change and fires SIGUSR1 (restart signal)
3. If the write takes >1 second, the watcher fires AGAIN before the first restart completes
4. The gateway restarts twice in ~1 second with a partially initialized model registry
5. Auth profiles fail to load → "No API key found" errors → agent is dead

### Symptoms

- `Unknown model: anthropic/claude-sonnet-4` errors
- `No API key found for provider "anthropic"`
- Complete silence from the agent (can't notify if it can't authenticate)
- Multiple restart entries in `gateway.err.log` within seconds of each other

## Prevention

### 1. Pre-Flight Check Script

Before any config change that touches auth:

```python
#!/usr/bin/env python3
"""Pre-flight check for config changes.
Run before config.apply/config.patch.
Validates auth profiles, checks for stale entries, enforces debounce."""

import json, time, sys
from pathlib import Path

OPENCLAW_DIR = Path.home() / ".openclaw"
AUTH_PATH = OPENCLAW_DIR / "agents" / "main" / "agent" / "auth-profiles.json"
DEBOUNCE_PATH = OPENCLAW_DIR / ".last-config-apply"
DEBOUNCE_SECONDS = 5

def check():
    issues = []

    # Check auth profiles
    if AUTH_PATH.exists():
        data = json.loads(AUTH_PATH.read_text())
        profiles = data.get("profiles", {})
        # Flag stale entries
        for key in profiles:
            if any(bad in key for bad in ["Symbol", "clack", "cancel", "undefined"]):
                issues.append(f"Stale auth entry: {key}")
        # Flag missing credentials
        for key, val in profiles.items():
            if "anthropic" in key and not (val.get("token") or val.get("key")):
                issues.append(f"No credentials in: {key}")

    # Check debounce
    if DEBOUNCE_PATH.exists():
        elapsed = time.time() - float(DEBOUNCE_PATH.read_text().strip())
        if elapsed < DEBOUNCE_SECONDS:
            issues.append(f"Too soon! {elapsed:.1f}s since last apply (min {DEBOUNCE_SECONDS}s)")

    return issues

issues = check()
if issues:
    for i in issues:
        print(f"❌ {i}")
    sys.exit(1)
else:
    print("✅ Safe to apply config")
```

### 2. Debounce Rule

**Never chain config writes.** Wait at minimum 5 seconds between `config.apply` or `config.patch` calls. Record a timestamp after each apply and check it before the next.

### 3. Auth Profile Hygiene

Periodically check `auth-profiles.json` for:
- Stale entries from cancelled interactive prompts (e.g., `Symbol(clack:cancel)`)
- Profiles with no credentials
- Profiles that don't match any config entry

### 4. Post-Restart Verification

After any config restart:
1. Verify auth is working (can the agent respond?)
2. Check `gateway.err.log` for auth errors
3. Send a restart notification to confirm the system is alive

## Recovery

If you hit this issue:

1. **From terminal:** `openclaw models auth paste-token --provider anthropic`
2. Paste a fresh session token
3. The gateway will detect the config change and restart cleanly
4. Delete any Telegram messages that contained the token

## Best Practices from docs.openclaw.ai

- Use `config.patch` over `config.apply` when possible (less risk of clobbering)
- `config.patch` uses JSON merge semantics — objects merge, null deletes, arrays replace
- Both validate, write, and restart in one step
- Use `restartDelayMs` parameter (default 2000ms) to control restart timing
- Always pass `baseHash` from `config.get` to detect concurrent changes

## Related

- [Configuration](https://docs.openclaw.ai/gateway/configuration) — full config reference
- [Heartbeat](https://docs.openclaw.ai/gateway/heartbeat) — periodic agent turns
- [Cron vs Heartbeat](https://docs.openclaw.ai/automation/cron-vs-heartbeat) — when to use each
