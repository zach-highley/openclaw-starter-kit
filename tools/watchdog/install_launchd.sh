#!/bin/bash
# Install the safe-dumb out-of-band OpenClaw watchdog as a per-user launchd agent.
#
# Opt-in: nothing runs until you execute this script.

set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This installer currently supports macOS (launchd) only." >&2
  exit 1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC_WATCHDOG="$REPO_DIR/tools/watchdog/watchdog.sh"

WATCHDOG_HOME="${OPENCLAW_WATCHDOG_HOME:-$HOME/.config/openclaw-watchdog}"
WATCHDOG_SHARE="${OPENCLAW_WATCHDOG_SHARE:-$HOME/.local/share/openclaw-watchdog}"
WATCHDOG_LOG_DIR="${OPENCLAW_WATCHDOG_LOG_DIR:-$HOME/Library/Logs/OpenClaw}"
WATCHDOG_CACHE="${OPENCLAW_WATCHDOG_CACHE:-$HOME/Library/Caches/OpenClaw/watchdog}"

CONFIG_ENV="$WATCHDOG_HOME/config.env"
KILL_SWITCH_FILE="$WATCHDOG_HOME/disabled"
INSTALLED_WATCHDOG="$WATCHDOG_SHARE/watchdog.sh"
PLIST_PATH="$HOME/Library/LaunchAgents/com.openclaw.gateway-watchdog.plist"

mkdir -p "$WATCHDOG_HOME" "$WATCHDOG_SHARE" "$WATCHDOG_LOG_DIR" "$WATCHDOG_CACHE" "$HOME/Library/LaunchAgents"

if [[ ! -f "$SRC_WATCHDOG" ]]; then
  echo "Missing source script: $SRC_WATCHDOG" >&2
  exit 1
fi

cp "$SRC_WATCHDOG" "$INSTALLED_WATCHDOG"
chmod 0755 "$INSTALLED_WATCHDOG"

if [[ ! -f "$CONFIG_ENV" ]]; then
  cat > "$CONFIG_ENV" <<'EOF'
# Optional: Telegram recovery notifications (sent directly via Telegram API).
# These are used ONLY by the watchdog and do not require the OpenClaw gateway.
#
# Create a bot: https://t.me/BotFather
# Find your chat id: https://t.me/userinfobot (or use telegram tools)
#
# IMPORTANT: Keep this file private.
OPENCLAW_WATCHDOG_TELEGRAM_BOT_TOKEN=
OPENCLAW_WATCHDOG_TELEGRAM_CHAT_ID=

# Optional: override path to openclaw binary (default: "openclaw")
# OPENCLAW_BIN=/usr/local/bin/openclaw
EOF
  chmod 0600 "$CONFIG_ENV"
  echo "Created $CONFIG_ENV (permissions 600). Fill it in if you want Telegram notifications."
fi

# Leave kill-switch untouched if it exists. If user previously disabled, keep disabled.
if [[ -f "$KILL_SWITCH_FILE" ]]; then
  echo "Kill-switch is enabled at: $KILL_SWITCH_FILE (watchdog will not run until removed)."
fi

UID_NUM="$(id -u)"
LABEL="com.openclaw.gateway-watchdog"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>

  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${INSTALLED_WATCHDOG}</string>
  </array>

  <!-- Run every 60s; the watchdog itself uses a lock so overlapping runs exit quickly. -->
  <key>StartInterval</key>
  <integer>60</integer>

  <key>RunAtLoad</key>
  <true/>

  <!-- Keep logs local. Avoid logging secrets. -->
  <key>StandardOutPath</key>
  <string>${WATCHDOG_LOG_DIR}/watchdog.launchd.out.log</string>
  <key>StandardErrorPath</key>
  <string>${WATCHDOG_LOG_DIR}/watchdog.launchd.err.log</string>
</dict>
</plist>
EOF

# (Re)load via launchctl bootstrap. We intentionally operate on the per-user domain.
launchctl bootout "gui/${UID_NUM}" "$PLIST_PATH" >/dev/null 2>&1 || true
launchctl bootstrap "gui/${UID_NUM}" "$PLIST_PATH"
launchctl enable "gui/${UID_NUM}/${LABEL}" || true

echo
echo "Installed launchd agent: $PLIST_PATH"
echo "Installed watchdog script: $INSTALLED_WATCHDOG"
echo
echo "Status:" 
echo "  launchctl print gui/${UID_NUM}/${LABEL} | head -n 40"
echo
echo "Logs:" 
echo "  tail -n 200 ${WATCHDOG_LOG_DIR}/watchdog.jsonl"
echo "  tail -n 200 ${WATCHDOG_LOG_DIR}/watchdog.launchd.err.log"
