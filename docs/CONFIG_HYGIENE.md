# Configuration Hygiene Guide

> Lessons learned from running OpenClaw 24/7 — keeping your config clean, secure, and aligned with docs.

## The Golden Rule

**Always follow [docs.openclaw.ai](https://docs.openclaw.ai).** When in doubt, check the docs. Don't invent custom paths or override defaults unless you have a specific reason.

---

## Workspace Location

### ✅ Correct (Per Docs)
```json
{
  "agents": {
    "defaults": {
      "workspace": "~/.openclaw/workspace"
    }
  }
}
```

### ❌ Wrong (Custom Path)
```json
{
  "agents": {
    "defaults": {
      "workspace": "/Users/you/my-custom-folder"
    }
  }
}
```

**Why it matters:** Custom paths can cause confusion, orphaned files, and sync issues. The default `~/.openclaw/workspace` is what OpenClaw expects.

**If you have legacy paths:** Create a symlink for backward compatibility:
```bash
ln -s ~/.openclaw/workspace ~/your-old-path
```

---

## Secrets Management

### ❌ Bad: Secrets in Config (Plaintext)
```json
{
  "channels": {
    "telegram": {
      "botToken": "123456:ABC-actual-token-here"
    }
  }
}
```

### ✅ Good: Secrets in .env File
Create `~/.openclaw/.env`:
```bash
# ~/.openclaw/.env
TELEGRAM_BOT_TOKEN=123456:ABC-actual-token-here
OPENCLAW_GATEWAY_TOKEN=your-gateway-token
BRAVE_SEARCH_API_KEY=your-brave-key
```

Set permissions:
```bash
chmod 600 ~/.openclaw/.env
```

Update config to use `${VAR}` substitution:
```json
{
  "channels": {
    "telegram": {
      "botToken": "${TELEGRAM_BOT_TOKEN}"
    }
  },
  "gateway": {
    "auth": {
      "token": "${OPENCLAW_GATEWAY_TOKEN}"
    }
  },
  "tools": {
    "web": {
      "search": {
        "apiKey": "${BRAVE_SEARCH_API_KEY}"
      }
    }
  }
}
```

**Why it matters:**
- Config files get backed up, committed, shared
- `.env` files stay local with strict permissions
- Easier to rotate secrets without touching config
- Follows security best practices

---

## Regular Audits

Run this periodically to check for orphaned/legacy files:

```bash
# Check for non-standard directories
ls -la ~/.openclaw/

# Look for legacy paths in config
grep -r "clawd\|moltbot\|jarvis" ~/.openclaw/openclaw.json

# Check for plaintext secrets (should see ${VAR} not actual values)
grep -E "Token|apiKey|token" ~/.openclaw/openclaw.json | head -10

# Verify workspace is the default
grep "workspace" ~/.openclaw/openclaw.json
```

### What to Clean Up

| Pattern | Action |
|---------|--------|
| Old workspace folders (`~/clawd/`, `~/jarvis/`, etc.) | Move to trash or create symlink |
| `archive-*` directories in `~/.openclaw/` | Review and delete if unused |
| Multiple `.bak` files | Keep only last 2-3 backups |
| Secrets in config | Migrate to `.env` file |

---

## Config Validation

Before making changes, always:

1. **Backup current config:**
   ```bash
   cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup-$(date +%Y%m%d)
   ```

2. **Use `config.patch` not `config.apply`** for partial updates (less risky)

3. **After changes, verify gateway starts:**
   ```bash
   openclaw gateway status
   openclaw health
   ```

4. **If something breaks:**
   ```bash
   # Restore backup
   cp ~/.openclaw/openclaw.json.backup-YYYYMMDD ~/.openclaw/openclaw.json
   openclaw gateway restart
   ```

---

## Checklist for Clean Config

- [ ] Workspace is `~/.openclaw/workspace` (or has symlink for compat)
- [ ] All secrets in `~/.openclaw/.env` with `600` permissions
- [ ] Config uses `${VAR}` substitution for secrets
- [ ] No orphaned directories in `~/.openclaw/`
- [ ] No legacy paths (`clawd`, `moltbot`, etc.) in config
- [ ] Backups have secure permissions (`600`)

---

*Last updated: 2026-02-03*
