#!/usr/bin/env bash
set -euo pipefail

# install_crash_recovery.sh
# ------------------------
# Installs/removes a 2-minute scheduler for scripts/crash_recovery.sh.
#
# macOS:  launchd LaunchAgent (~/Library/LaunchAgents)
# Linux:  systemd --user timer (preferred), else crontab
#
# Notes:
# - Uses generic workspace detection:
#     1) $OPENCLAW_WORKSPACE
#     2) ~/clawd/
#     3) ~/.openclaw/workspace/
# - Adds a PATH that commonly includes Homebrew and (if present) NVM Node.

SERVICE_ID="com.openclaw.crash-recovery"

usage() {
  cat <<EOF
Usage:
  $(basename "$0") install [--workspace PATH]
  $(basename "$0") remove  [--workspace PATH]

Options:
  --workspace PATH   Override workspace detection (otherwise uses OPENCLAW_WORKSPACE, ~/clawd, ~/.openclaw/workspace)
  -h, --help         Show this help

What it installs:
  macOS:  ~/Library/LaunchAgents/${SERVICE_ID}.plist
  Linux:  ~/.config/systemd/user/${SERVICE_ID}.service + .timer (or cron fallback)

Runs every 2 minutes.
EOF
}

CMD="${1:-}"
shift || true

WORKSPACE_OVERRIDE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace)
      WORKSPACE_OVERRIDE="${2:-}"; shift 2;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown arg: $1" >&2
      usage; exit 2;;
  esac
done

if [[ -z "$CMD" ]]; then
  usage; exit 2
fi

detect_workspace() {
  if [[ -n "$WORKSPACE_OVERRIDE" ]]; then
    echo "$WORKSPACE_OVERRIDE"; return 0
  fi
  if [[ -n "${OPENCLAW_WORKSPACE:-}" ]]; then
    echo "$OPENCLAW_WORKSPACE"; return 0
  fi
  if [[ -d "$HOME/clawd" ]]; then
    echo "$HOME/clawd"; return 0
  fi
  if [[ -d "$HOME/.openclaw/workspace" ]]; then
    echo "$HOME/.openclaw/workspace"; return 0
  fi
  # Fallback: current directory
  pwd
}

# Construct a PATH that helps launchd/systemd find openclaw.
# - Homebrew: /opt/homebrew/bin (Apple Silicon), /usr/local/bin (Intel)
# - NVM: pick the newest version if present
find_nvm_node_bin() {
  local nvm_dir="$HOME/.nvm/versions/node"
  if [[ ! -d "$nvm_dir" ]]; then
    return 0
  fi
  # Pick the highest semver folder.
  local latest
  latest=$(ls -1 "$nvm_dir" 2>/dev/null | sort -V | tail -1 || true)
  if [[ -n "$latest" && -d "$nvm_dir/$latest/bin" ]]; then
    echo "$nvm_dir/$latest/bin"
  fi
}

BASE_PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
NVM_BIN="$(find_nvm_node_bin || true)"
if [[ -n "$NVM_BIN" ]]; then
  BASE_PATH="$BASE_PATH:$NVM_BIN"
fi

WORKSPACE="$(detect_workspace)"
SCRIPT_PATH="$WORKSPACE/scripts/crash_recovery.sh"

if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "ERROR: crash_recovery.sh not found at: $SCRIPT_PATH" >&2
  echo "Tip: run this script from the OpenClaw Starter Kit workspace, or pass --workspace PATH" >&2
  exit 1
fi

install_macos() {
  local plist="$HOME/Library/LaunchAgents/${SERVICE_ID}.plist"
  mkdir -p "$HOME/Library/LaunchAgents"

  cat >"$plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${SERVICE_ID}</string>

  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/env</string>
    <string>bash</string>
    <string>${SCRIPT_PATH}</string>
    <string>--once</string>
  </array>

  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>${BASE_PATH}</string>
  </dict>

  <key>RunAtLoad</key>
  <true/>

  <key>StartInterval</key>
  <integer>120</integer>
</dict>
</plist>
PLIST

  launchctl unload "$plist" >/dev/null 2>&1 || true
  launchctl load "$plist"
  echo "Installed launchd agent: $plist"
  echo "To check: launchctl list | grep openclaw"
}

remove_macos() {
  local plist="$HOME/Library/LaunchAgents/${SERVICE_ID}.plist"
  if [[ -f "$plist" ]]; then
    launchctl unload "$plist" >/dev/null 2>&1 || true
    rm -f "$plist"
    echo "Removed launchd agent: $plist"
  else
    echo "Not installed: $plist"
  fi
}

install_linux_systemd() {
  local user_dir="$HOME/.config/systemd/user"
  mkdir -p "$user_dir"

  local service_file="$user_dir/${SERVICE_ID}.service"
  local timer_file="$user_dir/${SERVICE_ID}.timer"

  cat >"$service_file" <<SERVICE
[Unit]
Description=OpenClaw crash recovery watchdog

[Service]
Type=oneshot
Environment=PATH=${BASE_PATH}
ExecStart=/usr/bin/env bash ${SCRIPT_PATH} --once
SERVICE

  cat >"$timer_file" <<TIMER
[Unit]
Description=Run OpenClaw crash recovery every 2 minutes

[Timer]
OnBootSec=60
OnUnitActiveSec=120
Unit=${SERVICE_ID}.service

[Install]
WantedBy=timers.target
TIMER

  systemctl --user daemon-reload
  systemctl --user enable --now "${SERVICE_ID}.timer"
  echo "Installed systemd user timer: ${timer_file}"
  echo "To check: systemctl --user status ${SERVICE_ID}.timer"
}

remove_linux_systemd() {
  local user_dir="$HOME/.config/systemd/user"
  local service_file="$user_dir/${SERVICE_ID}.service"
  local timer_file="$user_dir/${SERVICE_ID}.timer"

  systemctl --user disable --now "${SERVICE_ID}.timer" >/dev/null 2>&1 || true
  rm -f "$service_file" "$timer_file"
  systemctl --user daemon-reload >/dev/null 2>&1 || true
  echo "Removed systemd user timer/service (if present)."
}

install_linux_cron() {
  local line="*/2 * * * * OPENCLAW_WORKSPACE=${WORKSPACE} PATH=${BASE_PATH} bash ${SCRIPT_PATH} --once >/dev/null 2>&1"

  # Avoid duplicates.
  (crontab -l 2>/dev/null | grep -v "${SERVICE_ID}" || true; echo "# ${SERVICE_ID}"; echo "$line") | crontab -
  echo "Installed cron entry (every 2 minutes)."
}

remove_linux_cron() {
  (crontab -l 2>/dev/null | grep -v "${SERVICE_ID}" | grep -v "crash_recovery.sh" || true) | crontab - || true
  echo "Removed cron entry (if present)."
}

is_macos() {
  [[ "$(uname -s)" == "Darwin" ]]
}

is_linux() {
  [[ "$(uname -s)" == "Linux" ]]
}

has_systemd_user() {
  command -v systemctl >/dev/null 2>&1 && systemctl --user show-environment >/dev/null 2>&1
}

case "$CMD" in
  install)
    if is_macos; then
      install_macos
    elif is_linux; then
      if has_systemd_user; then
        install_linux_systemd
      else
        install_linux_cron
      fi
    else
      echo "Unsupported OS: $(uname -s)" >&2
      exit 1
    fi
    ;;
  remove)
    if is_macos; then
      remove_macos
    elif is_linux; then
      if has_systemd_user; then
        remove_linux_systemd
      fi
      remove_linux_cron
    else
      echo "Unsupported OS: $(uname -s)" >&2
      exit 1
    fi
    ;;
  *)
    usage; exit 2;;
esac
