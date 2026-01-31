# 🔄 Migration & Upgrade Guide

## For Humans AND Bots

**If you're an AI agent reading this:** Follow these steps EXACTLY. Do NOT improvise. Do NOT skip verification steps. Do NOT proceed to the next step until the current step's verification passes. If ANY step fails, STOP and tell your human.

**If you're a human reading this:** This is the safe, tested, verified path for every migration scenario. Every step has a verification check. If you're nervous, that's smart, but this works.

---

## Which Section Do I Need?

| Coming From | Going To | Section |
|-------------|----------|---------|
| **Clawdbot** (any version) | OpenClaw | [Section A: From Clawdbot](#a-migrating-from-clawdbot) |
| **Moltbot** (any version) | OpenClaw | [Section B: From Moltbot](#b-migrating-from-moltbot) |
| **Old OpenClaw** (e.g. 2026.1.29) | Newer OpenClaw | [Section C: Upgrading OpenClaw](#c-upgrading-openclaw) |
| **Fresh install** (nothing installed) | OpenClaw | [Section D: Fresh Install](#d-fresh-install) |

All sections share the same [Post-Migration Verification](#-post-migration-verification) and [Troubleshooting](#-if-something-goes-wrong) steps at the bottom.

---

## ⚠️ THE GOLDEN RULE

**OpenClaw is a DROP-IN REPLACEMENT for Clawdbot and Moltbot.** It installs alongside the old package. Your config, sessions, memory, and state ALL carry over automatically. You are NOT uninstalling and reinstalling. You are UPGRADING.

When you install `openclaw`, it:
1. Detects your existing clawdbot/moltbot config
2. Copies it to the new `~/.openclaw/` directory
3. Migrates session files, auth profiles, and state
4. Keeps the old files as backup (doesn't delete anything)

**Nothing breaks. Nothing is lost. The old package stays installed until you explicitly remove it.**

---

## 📋 PRE-FLIGHT CHECKLIST (ALL MIGRATIONS)

Before touching anything, run these checks. If you're a bot, run them silently and report results to your human.

```bash
# 1. What are you currently running?
openclaw --version 2>/dev/null && echo "OpenClaw installed"
clawdbot --version 2>/dev/null && echo "Clawdbot installed"
moltbot --version 2>/dev/null && echo "Moltbot installed"
echo "---"
node --version

# 2. Where's your config?
ls ~/.openclaw/openclaw.json 2>/dev/null && echo "OpenClaw config found"
ls ~/.clawdbot/clawdbot.json 2>/dev/null && echo "Clawdbot config found"
ls ~/.moltbot/moltbot.json 2>/dev/null && echo "Moltbot config found"

# 3. Back up EVERYTHING (MANDATORY — do this no matter what)
BACKUP_DIR="$HOME/openclaw-migration-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r ~/.openclaw "$BACKUP_DIR/" 2>/dev/null
cp -r ~/.clawdbot "$BACKUP_DIR/" 2>/dev/null
cp -r ~/.moltbot "$BACKUP_DIR/" 2>/dev/null
echo "✅ Backup saved to: $BACKUP_DIR"

# 4. Verify backup exists and has files
ls -la "$BACKUP_DIR/" && echo "✅ Backup verified"
```

**🛑 STOP if backup fails. Do NOT proceed without a backup.**

---

## A: Migrating from Clawdbot

### Step 1: Stop the old gateway
```bash
clawdbot gateway stop

# VERIFY:
clawdbot gateway status
# Expected: "not running" or similar
```

### Step 2: Install OpenClaw
```bash
npm i -g openclaw@latest

# VERIFY:
openclaw --version
# Expected: 2026.1.29 or newer
```

### Step 3: Run the doctor
```bash
openclaw doctor --non-interactive

# This will:
# - Detect your clawdbot config and migrate it
# - Check auth profiles
# - Validate the config
# - Report any issues

# VERIFY: Look for "config is valid" or "config migrated" in the output
```

### Step 4: Start the new gateway
```bash
openclaw gateway start

# VERIFY:
openclaw gateway status
# Expected: "running" with a PID and port number
```

### Step 5: Test it
Send your bot a message on Telegram/WhatsApp/Discord. It should respond normally. **Done. Skip to [Post-Migration Verification](#-post-migration-verification).**

---

## B: Migrating from Moltbot

The process is identical to Clawdbot. OpenClaw auto-detects moltbot configs too.

### Step 1: Stop the old gateway
```bash
moltbot gateway stop

# VERIFY:
moltbot gateway status
# Expected: "not running" or similar
```

### Step 2: Install OpenClaw
```bash
npm i -g openclaw@latest

# VERIFY:
openclaw --version
# Expected: 2026.1.29 or newer
```

### Step 3: Run the doctor
```bash
openclaw doctor --non-interactive

# VERIFY: Look for "config is valid" or "config migrated" in the output
```

### Step 4: Start the new gateway
```bash
openclaw gateway start

# VERIFY:
openclaw gateway status
# Expected: "running" with a PID
```

### Step 5: Test it
Send your bot a message. It should respond normally. **Done. Skip to [Post-Migration Verification](#-post-migration-verification).**

---

## C: Upgrading OpenClaw

Already on OpenClaw but behind on versions? This is even simpler.

### Option 1: One-liner upgrade (recommended)
```bash
# Stop, upgrade, restart — all in one
openclaw gateway stop && npm i -g openclaw@latest && openclaw doctor --non-interactive && openclaw gateway start

# VERIFY:
openclaw --version && openclaw gateway status
```

### Option 2: Let your bot do it
Send your bot this message:
> "Update yourself to the latest OpenClaw version. Stop the gateway, run npm i -g openclaw@latest, run doctor, restart, and confirm everything works."

Most bots can handle this autonomously. If yours can't, use Option 1.

### Option 3: Use the installer script
```bash
curl -fsSL https://openclaw.bot/install.sh | bash
```
The installer detects your existing install and upgrades in place. It runs `openclaw doctor --non-interactive` automatically after upgrading.

### After upgrading
```bash
# Check the new version
openclaw --version

# Make sure gateway is running
openclaw gateway status

# If not running:
openclaw gateway start
```

**Done. Skip to [Post-Migration Verification](#-post-migration-verification).**

---

## D: Fresh Install

Never had any bot installed? Start here.

```bash
# Install OpenClaw
curl -fsSL https://openclaw.bot/install.sh | bash

# Run the setup wizard
openclaw onboard
```

The onboard wizard walks you through everything: Telegram setup, model authentication, workspace creation. Follow the prompts. **Skip to [Post-Migration Verification](#-post-migration-verification) when done.**

---

## ✅ Post-Migration Verification

Run through ALL of these after any migration or upgrade.

| Check | Command | Expected |
|-------|---------|----------|
| Version | `openclaw --version` | 2026.1.29+ |
| Gateway running | `openclaw gateway status` | "running" with PID |
| Config valid | `openclaw doctor --non-interactive` | No errors |
| Models authed | `openclaw models list` | Your models show authenticated |
| Bot responds | Send a message on Telegram/WhatsApp/Discord | Bot replies normally |
| Memory intact | Ask bot "what do you remember about me?" | Should recall prior conversations |
| Sessions intact | `ls ~/.openclaw/agents/` | Session files exist |
| Backup safe | `ls ~/openclaw-migration-backup-*` | Backup directory exists |

---

## 🔥 If Something Goes Wrong

### Bot doesn't respond after migration
```bash
# Check gateway status
openclaw gateway status

# If not running:
openclaw gateway start

# If still not responding:
openclaw doctor --fix
```

### Config didn't migrate automatically
```bash
# Manual migration — copy your old config
cp ~/.clawdbot/clawdbot.json ~/.openclaw/openclaw.json 2>/dev/null
cp ~/.moltbot/moltbot.json ~/.openclaw/openclaw.json 2>/dev/null

# Then validate and fix
openclaw doctor --fix
```

### Auth profiles lost
```bash
# Re-authenticate
openclaw onboard

# Or individually:
openclaw models auth login --provider anthropic
openclaw models auth login --provider google-gemini-cli
openclaw models auth login --provider openai
```

### Gateway won't start (port conflict)
```bash
# Check if old gateway is still running
ps aux | grep -E "clawdbot|moltbot|openclaw" | grep -v grep

# Kill any lingering processes
pkill -f clawdbot 2>/dev/null
pkill -f moltbot 2>/dev/null

# Try again
openclaw gateway start
```

### Node.js version too old
```bash
node --version
# Needs to be v22+

# On macOS:
brew install node@22

# On Linux:
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### NUCLEAR OPTION: Full rollback
```bash
# Stop OpenClaw
openclaw gateway stop

# Find your backup
ls ~/openclaw-migration-backup-*

# Restore (pick the right source for your old setup)
# For clawdbot:
cp -r ~/openclaw-migration-backup-XXXXX/.clawdbot/. ~/.clawdbot/
clawdbot gateway start

# For moltbot:
cp -r ~/openclaw-migration-backup-XXXXX/.moltbot/. ~/.moltbot/
moltbot gateway start

# You're back to exactly where you started. Nothing lost.
```

---

## 🤖 For AI Agents: Automated Migration Script

If you're a bot and your human asks you to migrate, here's the complete script. Run each section one at a time, NOT all at once. Verify each step before proceeding.

```bash
#!/bin/bash
# OpenClaw Migration Script — Safe, Verified, Reversible
# Works for clawdbot, moltbot, or old openclaw → latest openclaw
set -euo pipefail

echo "🔄 OpenClaw Migration — Starting Pre-Flight..."

# === DETECT CURRENT SETUP ===
OLD_CMD=""
OLD_VERSION="none"
if command -v openclaw &>/dev/null; then
  OLD_CMD="openclaw"
  OLD_VERSION=$(openclaw --version 2>/dev/null || echo "unknown")
elif command -v clawdbot &>/dev/null; then
  OLD_CMD="clawdbot"
  OLD_VERSION=$(clawdbot --version 2>/dev/null || echo "unknown")
elif command -v moltbot &>/dev/null; then
  OLD_CMD="moltbot"
  OLD_VERSION=$(moltbot --version 2>/dev/null || echo "unknown")
fi
echo "Current: $OLD_CMD $OLD_VERSION"

# === BACKUP ===
BACKUP_DIR="$HOME/openclaw-migration-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r ~/.openclaw "$BACKUP_DIR/" 2>/dev/null || true
cp -r ~/.clawdbot "$BACKUP_DIR/" 2>/dev/null || true
cp -r ~/.moltbot "$BACKUP_DIR/" 2>/dev/null || true
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
echo "✅ Backup: $BACKUP_DIR ($BACKUP_SIZE)"

# === STOP OLD GATEWAY ===
echo "Stopping gateway..."
openclaw gateway stop 2>/dev/null || true
clawdbot gateway stop 2>/dev/null || true
moltbot gateway stop 2>/dev/null || true
sleep 2
echo "✅ Gateway stopped"

# === INSTALL / UPGRADE ===
echo "Installing OpenClaw..."
npm i -g openclaw@latest
NEW_VERSION=$(openclaw --version)
echo "✅ Installed: $NEW_VERSION"

# === DOCTOR ===
echo "Running doctor..."
openclaw doctor --non-interactive
echo "✅ Doctor complete"

# === START ===
echo "Starting OpenClaw gateway..."
openclaw gateway start
sleep 3
openclaw gateway status
echo "✅ Gateway started"

# === DONE ===
echo ""
echo "========================================="
echo "✅ Migration complete: $OLD_CMD $OLD_VERSION → openclaw $NEW_VERSION"
echo "📁 Backup at: $BACKUP_DIR"
echo "========================================="
echo ""
echo "NEXT: Send your bot a test message to verify it responds."
echo "If anything is wrong: openclaw doctor --fix"
echo "Full rollback: restore from $BACKUP_DIR"
```

---

## 🧹 Cleanup (Optional — After 24+ Hours)

Only do this once everything has been working for at least a full day:

```bash
# Remove old package (optional — it's not hurting anything)
npm uninstall -g clawdbot 2>/dev/null
npm uninstall -g moltbot 2>/dev/null

# Update Chrome extension if using browser relay
openclaw browser extension install
# Then in Chrome: chrome://extensions → reload the extension

# Install auto-start service (macOS)
openclaw gateway install
```

---

## FAQ

**Q: Will I lose my conversations/memory?**
A: No. Everything migrates automatically. Your bot remembers everything.

**Q: Do I need to reconfigure my Telegram/WhatsApp/Discord?**
A: No. Your channel configs carry over. Same bot token, same everything.

**Q: Can I go back if something breaks?**
A: Yes. The backup you made in pre-flight lets you fully rollback in under a minute.

**Q: How long does this take?**
A: 2-5 minutes for most setups. The actual install is ~30 seconds. The rest is verification.

**Q: My bot is running on a VPS/cloud server. Anything different?**
A: Same exact steps. SSH in and run them. The only difference is you'll use `sudo npm i -g openclaw@latest` if your npm requires root.

**Q: I'm on Windows. Does this work?**
A: Yes. Use the PowerShell installer: `iwr -useb https://openclaw.ai/install.ps1 | iex`. Same migration logic applies.

---

*Tested across clawdbot, moltbot, and openclaw version upgrades. If you find an edge case, open an issue on GitHub.*
