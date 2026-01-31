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
| **Old OpenClaw** (any version) | Newer OpenClaw | [Section C: Upgrading OpenClaw](#c-upgrading-openclaw) |
| **Fresh install** (nothing) | OpenClaw | [Section D: Fresh Install](#d-fresh-install) |
| **Moving to a new machine** | Same OpenClaw | [Section E: Machine Migration](#e-migrating-to-a-new-machine) |

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
# Node 22+ required. If older, upgrade first (see Troubleshooting below).

# 2. Where's your config?
ls ~/.openclaw/openclaw.json 2>/dev/null && echo "OpenClaw config found"
ls ~/.clawdbot/clawdbot.json 2>/dev/null && echo "Clawdbot config found"
ls ~/.moltbot/moltbot.json 2>/dev/null && echo "Moltbot config found"

# 3. How was it installed? (npm global vs git checkout)
npm list -g openclaw 2>/dev/null && echo "npm global install"
ls ~/openclaw/pnpm-workspace.yaml 2>/dev/null && echo "git source checkout"

# 4. Back up EVERYTHING (MANDATORY — do this no matter what)
BACKUP_DIR="$HOME/openclaw-migration-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r ~/.openclaw "$BACKUP_DIR/" 2>/dev/null || true
cp -r ~/.clawdbot "$BACKUP_DIR/" 2>/dev/null || true
cp -r ~/.moltbot "$BACKUP_DIR/" 2>/dev/null || true
echo "✅ Backup saved to: $BACKUP_DIR"

# 5. Verify backup exists and has files
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

# Doctor will:
# - Detect your clawdbot config and migrate it to ~/.openclaw/
# - Migrate legacy config keys to the current schema
# - Move session files to the new per-agent directory structure
# - Check and refresh OAuth tokens if needed
# - Validate everything and report issues

# VERIFY: Look for "config is valid" or "config migrated" in the output
# If it mentions legacy key migrations — that's expected and good
```

### Step 4: Start the new gateway
```bash
openclaw gateway start

# VERIFY:
openclaw gateway status
# Expected: "running" with a PID and port number

# Also run:
openclaw health
# Expected: healthy status for gateway + channels
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
openclaw health
```

### Step 5: Test it
Send your bot a message. It should respond normally. **Done. Skip to [Post-Migration Verification](#-post-migration-verification).**

---

## C: Upgrading OpenClaw

Already on OpenClaw but behind on versions? Multiple ways to do this, pick one.

### Option 1: `openclaw update` (recommended for most users)
```bash
# Built-in update command — handles everything
openclaw update

# This will:
# - Detect your install method (npm or git)
# - Update via the appropriate method
# - Run openclaw doctor automatically
# - Restart the gateway

# VERIFY:
openclaw --version
openclaw gateway status
```

### Option 2: `openclaw update wizard` (interactive, best for beginners)
```bash
# Interactive flow — picks channel, confirms restart
openclaw update wizard
```

### Option 3: Re-run the installer (official recommendation from OpenClaw docs)
```bash
# The installer detects existing installs and upgrades in place
curl -fsSL https://openclaw.bot/install.sh | bash

# Add --no-onboard to skip the setup wizard if you're already configured
curl -fsSL https://openclaw.bot/install.sh | bash -s -- --no-onboard
```

### Option 4: Manual npm upgrade
```bash
openclaw gateway stop
npm i -g openclaw@latest
openclaw doctor --non-interactive
openclaw gateway restart

# VERIFY:
openclaw --version && openclaw gateway status && openclaw health
```

### Option 5: Source install (git checkout) upgrade
```bash
# If you installed from source:
cd ~/openclaw  # or wherever your checkout is
openclaw update

# Or manually:
git pull
pnpm install
pnpm build
pnpm ui:build
openclaw doctor
openclaw gateway restart
```

### Option 6: Let your bot do it
Send your bot this message:
> "Update yourself to the latest OpenClaw version safely. Back up first, then update, run doctor, restart, and confirm everything works."

Most bots can handle this autonomously.

### Update Channels

OpenClaw has three update channels. Most users should stay on **stable**.

| Channel | What it is | Command |
|---------|-----------|---------|
| **stable** | Production releases (default) | `openclaw update --channel stable` |
| **beta** | Builds under test | `openclaw update --channel beta` |
| **dev** | Latest from main branch | `openclaw update --channel dev` |

You can check your current channel:
```bash
openclaw update status
```

**Done. Skip to [Post-Migration Verification](#-post-migration-verification).**

---

## D: Fresh Install

Never had any bot installed? Start here.

```bash
# Install OpenClaw
curl -fsSL https://openclaw.bot/install.sh | bash

# Run the setup wizard (Telegram, models, workspace)
openclaw onboard --install-daemon
```

The onboard wizard walks you through everything: Telegram setup, model authentication, workspace creation, and installing the auto-start service. Follow the prompts.

**Windows:**
```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

**Skip to [Post-Migration Verification](#-post-migration-verification) when done.**

---

## E: Migrating to a New Machine

Moving OpenClaw from one computer to another without redoing onboarding.

### What you're moving
Your entire `~/.openclaw/` directory contains everything:
- Config (`openclaw.json`)
- Credentials (API keys, OAuth tokens)
- Session history and agent state
- Channel state (WhatsApp login, etc.)
- Workspace files (memory, skills, prompts)

### Steps

**On the old machine:**
```bash
# Stop the gateway
openclaw gateway stop

# Archive everything
cd ~
tar -czf openclaw-state.tgz .openclaw

# If your workspace is outside ~/.openclaw:
tar -czf openclaw-workspace.tgz /path/to/workspace
```

**On the new machine:**
```bash
# Install OpenClaw
curl -fsSL https://openclaw.bot/install.sh | bash -s -- --no-onboard

# Copy the archive from old machine (scp, rsync, USB, whatever)
# Then extract:
cd ~
tar -xzf openclaw-state.tgz

# Run doctor (repairs services, validates config)
openclaw doctor

# Start the gateway
openclaw gateway restart
openclaw status
```

### Common gotchas
- **Copy the entire `~/.openclaw/` directory**, not just `openclaw.json`. Credentials, sessions, and channel state live in subdirectories.
- **File ownership matters.** If you copied as root, `chown -R $(whoami) ~/.openclaw/`
- **If using profiles** (e.g. `--profile work`), you also need `~/.openclaw-work/`
- **Secrets are in that directory.** Treat backups like production secrets, encrypt them, don't send over insecure channels.

Full details: [Official machine migration guide](https://docs.openclaw.ai/install/migrating)

---

## ✅ Post-Migration Verification

Run through ALL of these after any migration or upgrade.

| Check | Command | Expected |
|-------|---------|----------|
| Version | `openclaw --version` | 2026.1.29+ |
| Gateway running | `openclaw gateway status` | "running" with PID |
| Gateway healthy | `openclaw health` | All checks pass |
| System status | `openclaw status` | Shows gateway, channels, models |
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

# Check health:
openclaw health

# If still not responding, repair everything:
openclaw doctor --repair
```

### Config didn't migrate automatically
```bash
# Manual migration — copy your old config
cp ~/.clawdbot/clawdbot.json ~/.openclaw/openclaw.json 2>/dev/null
cp ~/.moltbot/moltbot.json ~/.openclaw/openclaw.json 2>/dev/null

# Then validate, migrate legacy keys, and fix
openclaw doctor --repair
```

### Legacy config keys causing errors
```bash
# Doctor automatically migrates old config keys like:
# - routing.allowFrom → channels.whatsapp.allowFrom
# - routing.groupChat.* → messages.groupChat.*
# - agent.* → agents.defaults + tools.*
# - identity → agents.list[].identity
# Just run:
openclaw doctor
# It will explain what it migrated and rewrite your config
```

### Auth profiles lost or expired
```bash
# Re-authenticate everything
openclaw onboard

# Or individually:
openclaw models auth login --provider anthropic
openclaw models auth login --provider google-gemini-cli
openclaw models auth login --provider openai

# Doctor also checks OAuth token expiry and can refresh tokens:
openclaw doctor
```

### Gateway won't start (port conflict)
```bash
# Check if old gateway is still running
ps aux | grep -E "clawdbot|moltbot|openclaw" | grep -v grep

# Kill any lingering processes
pkill -f clawdbot 2>/dev/null
pkill -f moltbot 2>/dev/null

# Doctor can detect and clean up legacy services:
openclaw doctor --deep

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

# On Windows: winget install OpenJS.NodeJS
```

### npm permission errors on Linux (EACCES)
```bash
# Common on fresh Linux. Fix npm's global prefix:
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Then retry:
npm i -g openclaw@latest
```

### `openclaw` command not found after install
```bash
# Check where npm installs globals:
npm prefix -g

# Make sure that path's bin/ is in your PATH:
echo $PATH

# Fix (add to ~/.zshrc or ~/.bashrc):
export PATH="$(npm prefix -g)/bin:$PATH"
```

### Rollback to a specific version
```bash
# If the latest update broke something, pin to a known-good version:
npm i -g openclaw@2026.1.29  # replace with your last working version

openclaw doctor
openclaw gateway restart
```

### NUCLEAR OPTION: Full rollback to old bot
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
INSTALL_METHOD="npm"
if command -v openclaw &>/dev/null; then
  OLD_CMD="openclaw"
  OLD_VERSION=$(openclaw --version 2>/dev/null || echo "unknown")
  # Check if source install
  if [ -f ~/openclaw/pnpm-workspace.yaml ]; then
    INSTALL_METHOD="git"
  fi
elif command -v clawdbot &>/dev/null; then
  OLD_CMD="clawdbot"
  OLD_VERSION=$(clawdbot --version 2>/dev/null || echo "unknown")
elif command -v moltbot &>/dev/null; then
  OLD_CMD="moltbot"
  OLD_VERSION=$(moltbot --version 2>/dev/null || echo "unknown")
fi
echo "Current: $OLD_CMD $OLD_VERSION (install: $INSTALL_METHOD)"

# === CHECK NODE VERSION ===
NODE_MAJOR=$(node --version 2>/dev/null | sed 's/v//' | cut -d. -f1)
if [ "${NODE_MAJOR:-0}" -lt 22 ]; then
  echo "❌ Node.js 22+ required. Current: $(node --version 2>/dev/null || echo 'not found')"
  echo "Install: brew install node@22 (macOS) or see https://nodejs.org"
  exit 1
fi
echo "✅ Node $(node --version)"

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
if [ "$INSTALL_METHOD" = "git" ]; then
  echo "Updating source checkout..."
  cd ~/openclaw
  git pull
  pnpm install
  pnpm build
  pnpm ui:build
else
  echo "Installing via npm..."
  npm i -g openclaw@latest
fi
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

# === HEALTH CHECK ===
echo "Checking health..."
openclaw health
echo "✅ Health check complete"

# === DONE ===
echo ""
echo "========================================="
echo "✅ Migration complete: $OLD_CMD $OLD_VERSION → openclaw $NEW_VERSION"
echo "📁 Backup at: $BACKUP_DIR"
echo "========================================="
echo ""
echo "NEXT: Send your bot a test message to verify it responds."
echo "If anything is wrong: openclaw doctor --repair"
echo "Pin to old version: npm i -g openclaw@<version>"
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

# Install auto-start service (so gateway survives reboots)
openclaw gateway install

# On Linux, enable systemd lingering (gateway survives logout):
loginctl enable-linger $(whoami)
```

---

## 📚 What `openclaw doctor` Actually Does

Doctor is the most important command in your toolkit. It's not just a health check — it's a repair, migration, and audit tool. Here's what it handles:

- **Config migration:** Rewrites deprecated config keys to current schema (routing.* → channels.*, agent.* → agents.defaults, etc.)
- **State migration:** Moves sessions from old directory layouts to per-agent structure
- **WhatsApp auth migration:** Moves Baileys auth state to new credential paths
- **OAuth token refresh:** Checks expiry dates, refreshes tokens when possible
- **Service detection:** Finds and cleans up legacy launchd/systemd services
- **Sandbox repair:** Checks Docker images when sandboxing is enabled
- **Security audit:** Warns on open DM policies, missing gateway auth tokens
- **Config permissions:** Ensures `~/.openclaw/openclaw.json` is chmod 600
- **Port collision detection:** Checks for conflicts on gateway port (default 18789)

**Flags worth knowing:**
| Flag | What it does |
|------|-------------|
| `--non-interactive` | Safe migrations only, no prompts (CI/automation) |
| `--repair` | Apply recommended repairs without prompting |
| `--repair --force` | Aggressive repairs (overwrites custom service configs) |
| `--deep` | Scan for extra gateway installs across the system |
| `--yes` | Accept all defaults without prompting |

Full reference: [docs.openclaw.ai/gateway/doctor](https://docs.openclaw.ai/gateway/doctor)

---

## FAQ

**Q: Will I lose my conversations/memory?**
A: No. Everything migrates automatically. Your bot remembers everything.

**Q: Do I need to reconfigure my Telegram/WhatsApp/Discord?**
A: No. Your channel configs carry over. Same bot token, same everything.

**Q: Can I go back if something breaks?**
A: Yes. The backup you made in pre-flight lets you fully rollback. You can also pin to a specific version: `npm i -g openclaw@2026.1.29`

**Q: How long does this take?**
A: 2-5 minutes for most setups. The actual install is ~30 seconds. The rest is verification.

**Q: My bot is running on a VPS/cloud server. Anything different?**
A: Same exact steps. SSH in and run them. If npm requires root: `sudo npm i -g openclaw@latest`

**Q: I'm on Windows. Does this work?**
A: Yes. Use the PowerShell installer: `iwr -useb https://openclaw.ai/install.ps1 | iex`

**Q: I installed from source (git clone). Can I still upgrade?**
A: Yes. Use `openclaw update` or manually `git pull && pnpm install && pnpm build`. See Section C, Option 5.

**Q: What are update channels?**
A: Stable (default, recommended), beta (pre-release testing), dev (bleeding edge from main). Switch with `openclaw update --channel <name>`. Most users should stay on stable.

**Q: The update broke something. How do I go back?**
A: Pin to the last working version: `npm i -g openclaw@<version>` then `openclaw doctor && openclaw gateway restart`. For source installs, checkout a specific commit: `git checkout "$(git rev-list -n 1 --before="2026-01-01" origin/main)"`

**Q: Where does OpenClaw store its data?**
A: Everything lives in `~/.openclaw/` by default. Config, credentials, sessions, workspace. If you use `--profile`, it's `~/.openclaw-<profilename>/`.

---

## 📖 Official Documentation Links

- [Install guide](https://docs.openclaw.ai/install)
- [Updating guide](https://docs.openclaw.ai/install/updating)
- [Machine migration](https://docs.openclaw.ai/install/migrating)
- [Doctor reference](https://docs.openclaw.ai/gateway/doctor)
- [Update channels](https://docs.openclaw.ai/install/development-channels)
- [Installer internals](https://docs.openclaw.ai/install/installer)
- [Troubleshooting](https://docs.openclaw.ai/gateway/troubleshooting)
- [Discord community](https://discord.com/invite/clawd)

---

*Tested across clawdbot, moltbot, and openclaw version upgrades. If you find an edge case, open an issue on GitHub.*
