#!/bin/bash
# OpenClaw Watchdog (starter-kit edition)
#
# Goal: keep ONE Gateway healthy without doing anything schema-invalid or
# multi-gateway-hostile.
#
# This script intentionally prefers OpenClaw's built-in supervision and repair:
# - openclaw gateway install/start/stop/restart (service lifecycle)
# - openclaw health --json (Gateway snapshot)
# - openclaw doctor (migrations + repairs)
#
# IMPORTANT:
# - Do NOT `nohup openclaw gateway &` from a watchdog. That can spawn a second
#   Gateway instance, which is a common reliability footgun.
# - Use the service lifecycle commands instead.
#
# Schedule with launchd/cron every 5 minutes.

set -euo pipefail

# --- Configuration ------------------------------------------------------------
OPENCLAW_BIN="${OPENCLAW_BIN:-openclaw}"
LOG_DIR="${OPENCLAW_WATCHDOG_LOG_DIR:-$HOME/.openclaw/logs}"
LOG_FILE="$LOG_DIR/watchdog.log"
STATE_FILE="$LOG_DIR/watchdog-state.json"

# Optional notification destination for watchdog messages.
# For Telegram, prefer a numeric chat id (DM user id or group id like -100...).
TELEGRAM_TARGET="${TELEGRAM_TARGET:-${TELEGRAM_CHAT_ID:-}}"

# Doctor cadence (hours)
DOCTOR_INTERVAL_HOURS="${WATCHDOG_DOCTOR_INTERVAL_HOURS:-6}"
# If set to 1, apply repairs in automation (may restart service / adjust supervisor).
WATCHDOG_DOCTOR_REPAIR="${WATCHDOG_DOCTOR_REPAIR:-0}"

# Timeouts
STATUS_TIMEOUT_SEC="${WATCHDOG_STATUS_TIMEOUT_SEC:-15}"
HEALTH_TIMEOUT_SEC="${WATCHDOG_HEALTH_TIMEOUT_SEC:-20}"
DOCTOR_TIMEOUT_SEC="${WATCHDOG_DOCTOR_TIMEOUT_SEC:-300}"

mkdir -p "$LOG_DIR"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >>"$LOG_FILE"
}

run_with_timeout() {
  local secs="$1"; shift
  if command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$secs" "$@"
  elif command -v timeout >/dev/null 2>&1; then
    timeout "$secs" "$@"
  else
    "$@"
  fi
}

notify_telegram() {
  local msg="$1"

  if [[ -n "$TELEGRAM_TARGET" ]]; then
    run_with_timeout 30 "$OPENCLAW_BIN" message send \
      --channel telegram \
      --target "$TELEGRAM_TARGET" \
      --message "$msg" >>"$LOG_FILE" 2>&1 && return 0
  fi

  # Optional last-ditch fallback (not recommended; requires secrets on disk)
  if [[ -n "${TELEGRAM_BOT_TOKEN:-}" && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d chat_id="$TELEGRAM_CHAT_ID" \
      -d text="$msg" >>"$LOG_FILE" 2>&1 || true
  fi
}

update_state() {
  cat >"$STATE_FILE" <<EOF
{
  "lastCheck": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "$1",
  "lastAction": "$2",
  "details": "${3:-}"
}
EOF
}

log "=== Watchdog check starting ==="

# --- 1) Ensure gateway service is up -----------------------------------------
log "[1] gateway status"
if ! run_with_timeout "$STATUS_TIMEOUT_SEC" "$OPENCLAW_BIN" gateway status --json >/dev/null 2>&1; then
  log "Gateway status failed; attempting gateway start"
  notify_telegram "🤖 Watchdog: Gateway looks down. Starting service…"
  run_with_timeout 60 "$OPENCLAW_BIN" gateway start >>"$LOG_FILE" 2>&1 || true
  sleep 5
fi

# --- 2) Health snapshot -------------------------------------------------------
log "[2] health"
if ! run_with_timeout "$HEALTH_TIMEOUT_SEC" "$OPENCLAW_BIN" health --json >/dev/null 2>&1; then
  log "Health probe failed; restarting gateway"
  notify_telegram "🤖 Watchdog: Health check failed. Restarting Gateway…"
  run_with_timeout 60 "$OPENCLAW_BIN" gateway restart >>"$LOG_FILE" 2>&1 || true
  sleep 8

  if run_with_timeout "$HEALTH_TIMEOUT_SEC" "$OPENCLAW_BIN" health --json >/dev/null 2>&1; then
    notify_telegram "✅ Watchdog: Gateway restarted and health is back."
  else
    notify_telegram "⚠️ Watchdog: Gateway restart did not restore health. Run: openclaw doctor"
  fi
fi

# --- 3) Periodic doctor -------------------------------------------------------
LAST_DOCTOR_FILE="$LOG_DIR/last-doctor-run"
LAST_DOCTOR=0
[[ -f "$LAST_DOCTOR_FILE" ]] && LAST_DOCTOR=$(cat "$LAST_DOCTOR_FILE" 2>/dev/null || echo 0)
NOW_EPOCH=$(date +%s)
HOURS_SINCE_DOCTOR=$(( (NOW_EPOCH - LAST_DOCTOR) / 3600 ))

if [[ "$HOURS_SINCE_DOCTOR" -ge "$DOCTOR_INTERVAL_HOURS" ]]; then
  log "[3] doctor (non-interactive)"
  notify_telegram "🩺 Watchdog: Running openclaw doctor (non-interactive)…"
  run_with_timeout "$DOCTOR_TIMEOUT_SEC" "$OPENCLAW_BIN" doctor --non-interactive >>"$LOG_FILE" 2>&1 || true

  if [[ "$WATCHDOG_DOCTOR_REPAIR" == "1" ]]; then
    log "[3b] doctor --repair --yes (opt-in)"
    run_with_timeout "$DOCTOR_TIMEOUT_SEC" "$OPENCLAW_BIN" doctor --repair --yes >>"$LOG_FILE" 2>&1 || true
  fi

  echo "$NOW_EPOCH" >"$LAST_DOCTOR_FILE"
fi

update_state "ok" "complete" "gateway ok"
log "=== Watchdog complete ==="
