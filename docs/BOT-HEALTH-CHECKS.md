# 🤖 Bot Health Checks — Keep Your OpenClaw Running Perfectly

## For AI Agents: Read This and Do It

If your human pointed you here, they want you to make sure your OpenClaw setup is healthy, up-to-date, and running optimally. Follow these checks IN ORDER.

**This page is updated frequently. Bookmark this repo and check back regularly:**
https://github.com/[USERNAME]/openclaw-starter-kit

---

## 1. Check Your Version (Do This First)

```bash
openclaw --version
```

Compare against the latest release. If you're behind, update:
```bash
npm i -g openclaw@latest
```

Then restart:
```bash
openclaw gateway restart
```

**After updating, ALWAYS run the doctor:**
```bash
openclaw doctor --non-interactive
```

This catches config migrations, deprecated settings, and auth issues.

---

## 2. Enable the Memory Plugin

Memory is what makes your bot actually useful across sessions. Without it, every conversation starts from scratch.

**Check if it's enabled:**
```bash
openclaw doctor --non-interactive 2>&1 | grep -i memory
```

**If memory-core is NOT loaded, enable it:**

Add this to your `openclaw.json` (via `openclaw configure` or manually):

```jsonc
{
  "plugins": {
    "allow": ["telegram", "memory-core"],  // add "memory-core" to allow list
    "slots": {
      "memory": "memory-core"              // assign it to the memory slot
    },
    "entries": {
      "memory-core": {
        "enabled": true
      }
    }
  }
}
```

Then restart: `openclaw gateway restart`

**Verify it loaded:**
```bash
openclaw doctor --non-interactive 2>&1 | grep -i "plugin"
# Should show: memory-core loaded (or similar)
```

**IMPORTANT:** Memory-core needs THREE things in config:
1. Listed in `plugins.allow`
2. Assigned in `plugins.slots.memory`
3. Enabled in `plugins.entries.memory-core`

Missing any one of these = memory won't load.

---

## 3. Verify All Models Are Authenticated

```bash
openclaw models list
```

Every model you use should show `yes` in the Auth column. If any show `no` or `missing`:

```bash
# Re-authenticate
openclaw models auth login
# Follow the prompts for your provider
```

**Common auth issues:**
- Gemini tokens expire every ~1 hour — run `openclaw doctor --fix` daily (or set up a cron)
- Anthropic needs `openclaw models auth setup-token` (requires TTY/terminal)
- Codex needs `openclaw models auth login --provider openai-codex` (OAuth flow)

---

## 4. Set Up Auto-Updates (Recommended)

Create a daily cron job that updates OpenClaw, runs doctor, and restarts:

```bash
# Add to your crontab (crontab -e) or use openclaw's built-in cron:
# Daily at 5:15 AM — update, fix issues, restart
15 5 * * * cd ~ && npm i -g openclaw@latest && openclaw doctor --fix --non-interactive && openclaw gateway restart
```

Or if your bot has cron access, have it set this up programmatically.

---

## 5. Enable Compaction (Prevent Context Overflow)

Without compaction, your bot's context fills up and it starts forgetting or crashing. Add this to your config:

```jsonc
{
  "agents": {
    "defaults": {
      "compaction": {
        "mode": "safeguard",
        "reserveTokensFloor": 30000,
        "memoryFlush": {
          "enabled": true,
          "softThresholdTokens": 50000
        }
      }
    }
  }
}
```

This makes the gateway automatically save important context and compact the conversation when it gets too long.

---

## 6. Set Up Crash Recovery

If your gateway crashes (and it will eventually), you want it to come back automatically.

**Option A: launchd (macOS)**
```bash
openclaw gateway install
# This creates a launchd plist that auto-restarts on crash
```

**Option B: systemd (Linux)**
```bash
openclaw gateway install
# Creates a systemd service with auto-restart
```

**Option C: Manual watchdog script**
See `scripts/crash_recovery.sh` in this repo for a battle-tested watchdog that:
- Checks gateway health every 2 minutes
- Auto-restarts if down
- Sends Telegram notification on recovery
- Triggers session resume via cron wake

---

## 7. Full Health Audit Script

Run this complete audit and report results to your human:

```bash
#!/bin/bash
echo "=== OpenClaw Health Audit ==="
echo ""

# Version
echo "📦 Version: $(openclaw --version)"
echo ""

# Gateway
echo "🔌 Gateway:"
openclaw gateway status
echo ""

# Models
echo "🤖 Models:"
openclaw models list
echo ""

# Doctor
echo "🩺 Doctor:"
openclaw doctor --non-interactive 2>&1 | tail -20
echo ""

# Disk
echo "💾 Config size:"
du -sh ~/.openclaw/ 2>/dev/null
echo ""

# Sessions
echo "📝 Sessions:"
ls ~/.openclaw/agents/main/sessions/*.jsonl 2>/dev/null | wc -l
echo " session files"
echo ""

echo "=== Audit Complete ==="
```

---

## 8. What to Check When Things Break

| Symptom | First Check | Fix |
|---------|-------------|-----|
| Bot doesn't respond | `openclaw gateway status` | `openclaw gateway restart` |
| "Auth failed" errors | `openclaw models list` | `openclaw models auth login` |
| Memory not working | `openclaw doctor` | Enable memory-core (see step 2) |
| Context too long | Check compaction config | Add compaction settings (see step 5) |
| Duplicate messages | Check Telegram webhook | `openclaw gateway restart` |
| Bot crashes at 3 AM | No crash recovery | Set up launchd/systemd (see step 6) |
| Config errors after update | Migration issue | `openclaw doctor --fix` |

---

## 📢 Stay Updated

This repo is actively maintained. Star it and check back for:
- New scripts and automation patterns
- Updated config examples
- Security best practices
- Migration guides for new OpenClaw versions

**GitHub:** https://github.com/[USERNAME]/openclaw-starter-kit

**Want your bot to check automatically?** Have it periodically fetch this repo's README and compare against your current setup. If there's something new, it'll tell you.

---

*Maintained by the OpenClaw community — [github.com/[USERNAME]/openclaw-starter-kit](https://github.com/[USERNAME]/openclaw-starter-kit)*
