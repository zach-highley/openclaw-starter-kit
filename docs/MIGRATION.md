# 🔄 Migration & Upgrade Guide (Beginner Friendly)

If you’re looking for `MIGRATION.md` because you saw it referenced somewhere, you’re not crazy. It existed in older versions of this repo and was removed during a rewrite. It’s back now.

This guide is for:
- **Beginners (humans)** who just want their bot to keep working.
- **Beginner bots** that need a deterministic checklist.

## The Golden Rule
OpenClaw upgrades are designed to be **non-destructive**.

- You should **back up first**.
- You should **run `openclaw doctor`**.
- You should **verify the gateway is healthy**.

## Quick decision table

| Coming from | Goal | Do this |
|---|---|---|
| Clawdbot | Move to OpenClaw | Section A |
| Moltbot | Move to OpenClaw | Section B |
| Older OpenClaw | Upgrade to latest | Section C |
| New machine | Move everything | Section D |

---

## Pre-flight checklist (do not skip)

```bash
BACKUP_DIR="$HOME/openclaw-migration-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r ~/.openclaw "$BACKUP_DIR/" 2>/dev/null || true
cp -r ~/.clawdbot "$BACKUP_DIR/" 2>/dev/null || true
cp -r ~/.moltbot "$BACKUP_DIR/" 2>/dev/null || true

echo "Backup saved to: $BACKUP_DIR"
ls -la "$BACKUP_DIR" | head

node --version
```

If backup fails, stop.

---

## A) Migrating from Clawdbot → OpenClaw

```bash
clawdbot gateway stop || true
npm i -g openclaw@latest
openclaw doctor --non-interactive
openclaw gateway start
openclaw gateway status
openclaw health
```

Verification:
- `openclaw gateway status` shows running PID
- `openclaw health` returns healthy for gateway + your channel

---

## B) Migrating from Moltbot → OpenClaw

```bash
moltbot gateway stop || true
npm i -g openclaw@latest
openclaw doctor --non-interactive
openclaw gateway start
openclaw gateway status
openclaw health
```

---

## C) Upgrading OpenClaw (old → latest)

Preferred beginner path:

```bash
openclaw update
openclaw gateway status
openclaw doctor --non-interactive
```

If you are using OpenClaw.app on macOS, use the menu bar app for start/stop and still run:

```bash
openclaw doctor --non-interactive
```

---

## D) Migrating to a new machine

Copy these directories from old → new machine (after install):

- `~/.openclaw/` (config, logs, sessions, auth profiles)
- Your agent workspace repo (this repo or your own)

Then:

```bash
openclaw doctor --non-interactive
openclaw gateway start
openclaw health
```

---

## Post-migration verification (required)

```bash
openclaw gateway status
openclaw health
openclaw logs --tail 200
```

Send the bot a test message on your primary channel.

---

## Troubleshooting (common beginner issues)

### 1) "Provider in cooldown" / rate limits
This is usually message-volume, not raw token usage.

- Batch inbound messages: see `docs/CRON_HEARTBEAT_GUIDE.md`
- Prefer heartbeat for periodic LLM checks

### 2) Auth / OAuth issues
Run:

```bash
openclaw doctor --non-interactive
```

### 3) Config schema errors
Run:

```bash
openclaw doctor --non-interactive
```

and read `docs/CONFIG_SAFETY.md`.

---

## Appendix: legacy migration guide (reference)
The previous, very long migration guide is available in git history if you want the full deep-dive.
This file is intentionally shorter and beginner-friendly.
