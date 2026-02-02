# Out-of-band gateway watchdog (safe-dumb)

This repo includes a **beginner-friendly**, **security-first**, **out-of-band** watchdog for the OpenClaw gateway.

“Out-of-band” means:
- it runs outside of OpenClaw (via `launchd`)
- it can still restart / repair the gateway even when the gateway is down
- it sends a *recovery* notification via the **Telegram HTTP API**, so it does **not** depend on the gateway to tell you it recovered

This watchdog is intentionally **limited** ("safe dumb"):
1. Check gateway health (`openclaw health`)
2. If unhealthy → restart gateway
3. If restart fails → run **exactly once in a while**: `openclaw doctor --repair --non-interactive`
4. If recovered → send a Telegram message (optional)

It does **not**:
- read/modify your agent prompts
- kill unrelated processes
- auto-reset sessions
- run arbitrary self-healing experiments

If you want the more advanced / aggressive version, see `scripts/watchdog.sh`.

---

## Install (macOS launchd)

Nothing is enabled by default. You must opt in.

From the repo root:

```bash
./tools/watchdog/install_launchd.sh
```

### Optional: enable Telegram “recovered” notifications

Edit:

```bash
$HOME/.config/openclaw-watchdog/config.env
```

Set:
- `OPENCLAW_WATCHDOG_TELEGRAM_BOT_TOKEN`
- `OPENCLAW_WATCHDOG_TELEGRAM_CHAT_ID`

Notes:
- The watchdog sends **only** a recovery message (“gateway recovered”).
- No secrets are ever written to logs by the watchdog.

---

## Kill-switch (pause without uninstall)

Create a file:

```bash
touch "$HOME/.config/openclaw-watchdog/disabled"
```

Remove it to re-enable:

```bash
rm "$HOME/.config/openclaw-watchdog/disabled"
```

---

## Status

```bash
launchctl print gui/"$(id -u)"/com.openclaw.gateway-watchdog | head -n 80
```

If you want to see recent invocations and exit codes:

```bash
log show --style syslog --last 10m --predicate 'process == "launchd"' | tail -n 200
```

---

## Logs

Structured JSON lines:

```bash
tail -n 200 "$HOME/Library/Logs/OpenClaw/watchdog.jsonl"
```

launchd stdout/stderr:

```bash
tail -n 200 "$HOME/Library/Logs/OpenClaw/watchdog.launchd.err.log"
tail -n 200 "$HOME/Library/Logs/OpenClaw/watchdog.launchd.out.log"
```

---

## Uninstall

```bash
./tools/watchdog/uninstall_launchd.sh
```

By default, uninstall keeps config/logs/cache for forensics.
To fully remove everything, follow the printed instructions.

---

## Security review checklist (recommended)

Before enabling any watchdog automation, do this:

### A) Principle of least privilege
- [ ] Confirm it runs as your **user** (LaunchAgent), not as root.
- [ ] Confirm it only runs: `openclaw health`, `openclaw gateway restart`, and (rarely) `openclaw doctor --repair --non-interactive`.
- [ ] Confirm the install script writes only into:
  - `~/Library/LaunchAgents/`
  - `~/.local/share/openclaw-watchdog/`
  - `~/.config/openclaw-watchdog/`
  - `~/Library/Logs/OpenClaw/`
  - `~/Library/Caches/OpenClaw/watchdog/`

### B) Secrets hygiene
- [ ] Ensure `~/.config/openclaw-watchdog/config.env` is **chmod 600**.
- [ ] Ensure you never paste bot tokens into terminal scrollback that gets synced/backed up.
- [ ] Confirm logs do not contain:
  - Telegram bot token
  - Telegram chat id
  - OpenClaw auth tokens
  - full command outputs containing secrets

### C) Rate limiting & blast radius
- [ ] Confirm repair rate limit is set (default: 6 hours).
- [ ] Confirm the kill-switch exists and you know how to use it.
- [ ] Confirm you are okay with automated `openclaw doctor --repair --non-interactive`.

### D) Uninstall / rollback
- [ ] Confirm you can uninstall with `./tools/watchdog/uninstall_launchd.sh`.
- [ ] Confirm you can disable without uninstall using the kill-switch.

---

## Troubleshooting

### The watchdog is installed but does nothing
- Ensure the kill-switch file does not exist:

```bash
ls -la "$HOME/.config/openclaw-watchdog/disabled" || true
```

### It can’t find `openclaw`
Set `OPENCLAW_BIN` in `config.env`:

```bash
OPENCLAW_BIN=/full/path/to/openclaw
```

### Telegram notifications don’t work
- Verify token/chat id are correct.
- The watchdog intentionally does not print Telegram API responses (to avoid leaking secrets). You should see a `notify.telegram` event in `watchdog.jsonl`.
