#!/bin/bash
# Uninstall the safe-dumb out-of-band OpenClaw watchdog launchd agent.

set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This uninstaller currently supports macOS (launchd) only." >&2
  exit 1
fi

WATCHDOG_HOME="${OPENCLAW_WATCHDOG_HOME:-$HOME/.config/openclaw-watchdog}"
WATCHDOG_SHARE="${OPENCLAW_WATCHDOG_SHARE:-$HOME/.local/share/openclaw-watchdog}"
WATCHDOG_LOG_DIR="${OPENCLAW_WATCHDOG_LOG_DIR:-$HOME/Library/Logs/OpenClaw}"
WATCHDOG_CACHE="${OPENCLAW_WATCHDOG_CACHE:-$HOME/Library/Caches/OpenClaw/watchdog}"

PLIST_PATH="$HOME/Library/LaunchAgents/com.openclaw.gateway-watchdog.plist"
LABEL="com.openclaw.gateway-watchdog"
UID_NUM="$(id -u)"

launchctl bootout "gui/${UID_NUM}" "$PLIST_PATH" >/dev/null 2>&1 || true

rm -f "$PLIST_PATH" || true

# Remove installed copy of the script (keep user config by default).
rm -f "$WATCHDOG_SHARE/watchdog.sh" || true

# Optional cleanup (comment out if you want to keep forensics)
# rm -rf "$WATCHDOG_CACHE" || true

cat <<EOF
Uninstalled launchd agent.

Left in place (by default):
  Config: $WATCHDOG_HOME
  Logs:   $WATCHDOG_LOG_DIR
  Cache:  $WATCHDOG_CACHE

To fully remove everything:
  rm -rf "$WATCHDOG_HOME" "$WATCHDOG_LOG_DIR" "$WATCHDOG_CACHE" "$WATCHDOG_SHARE"
EOF
