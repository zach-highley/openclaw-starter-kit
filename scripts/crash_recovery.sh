#!/usr/bin/env bash
set -euo pipefail

# OpenClaw Crash Recovery
# ----------------------
# Generic watchdog that checks the local gateway health endpoint and attempts
# to restart the gateway if it appears down.
#
# Features:
# - Health check:   http://localhost:18789/api/health
# - Recovery:       openclaw gateway restart, then stop+start
# - Notifications:  Telegram (bot token read from ~/.openclaw/openclaw.json)
# - Logging:        $WORKSPACE/logs/crash_recovery.log
# - Retries:        max 3 attempts, 10s delay
# - Post-recovery:  sends a "cron wake" event to the gateway
#
# Requirements:
# - curl
# - python3 (for JSON parsing)
# - openclaw CLI in PATH

HEALTH_URL="http://localhost:18789/api/health"
CRON_WAKE_URL="http://localhost:18789/api/cron/wake"

DEFAULT_CONFIG_PATH="$HOME/.openclaw/openclaw.json"

usage() {
  cat <<'EOF'
Usage:
  crash_recovery.sh [--config PATH] [--once]

Options:
  --config PATH   Path to openclaw.json (default: ~/.openclaw/openclaw.json)
  --once          Run a single check/recovery cycle (default behavior)
  -h, --help      Show this help

Environment:
  OPENCLAW_WORKSPACE           Workspace dir override
  CRASH_RECOVERY_CHAT_ID       Telegram chat_id override (recommended)
  CRASH_RECOVERY_DISABLE_TELEGRAM=1  Disable Telegram notifications
EOF
}

CONFIG_PATH="$DEFAULT_CONFIG_PATH"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      CONFIG_PATH="${2:-}"; shift 2 ;;
    --once)
      shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown arg: $1" >&2
      usage; exit 2 ;;
  esac
done

# ----------------------
# Workspace detection
# ----------------------
detect_workspace() {
  if [[ -n "${OPENCLAW_WORKSPACE:-}" ]]; then
    echo "$OPENCLAW_WORKSPACE"; return 0
  fi
  if [[ -d "$HOME/clawd" ]]; then
    echo "$HOME/clawd"; return 0
  fi
  if [[ -d "$HOME/.openclaw/workspace" ]]; then
    echo "$HOME/.openclaw/workspace"; return 0
  fi
  # Fallback: current directory (safe default)
  pwd
}

WORKSPACE="$(detect_workspace)"
LOG_DIR="$WORKSPACE/logs"
LOG_FILE="$LOG_DIR/crash_recovery.log"
mkdir -p "$LOG_DIR"

log() {
  local msg="$1"
  printf "%s %s\n" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$msg" | tee -a "$LOG_FILE" >/dev/null
}

# ----------------------
# JSON config helpers (python-based; avoids jq dependency)
# ----------------------
py_get() {
  # Usage: py_get <json_file> <python_expr>
  # python_expr can reference a loaded dict called `cfg`.
  local file="$1"; shift
  local expr="$1"; shift || true
  python3 - <<PY
import json, sys
from pathlib import Path
p = Path(${file@Q})
if not p.exists():
    sys.exit(0)
try:
    cfg = json.loads(p.read_text())
except Exception:
    sys.exit(0)
try:
    v = ${expr}
except Exception:
    v = None
if v is None:
    sys.exit(0)
if isinstance(v, (dict, list)):
    print(json.dumps(v))
else:
    print(str(v))
PY
}

read_gateway_token() {
  py_get "$CONFIG_PATH" "cfg.get('gatewayToken') or cfg.get('gateway', {}).get('token')"
}

read_telegram_bot_token() {
  py_get "$CONFIG_PATH" "cfg.get('channels', {}).get('telegram', {}).get('botToken')"
}

read_telegram_chat_id() {
  if [[ -n "${CRASH_RECOVERY_CHAT_ID:-}" ]]; then
    echo "$CRASH_RECOVERY_CHAT_ID"; return 0
  fi
  # allowFrom can be list of chat_ids/user_ids depending on user setup.
  py_get "$CONFIG_PATH" "(cfg.get('channels', {}).get('telegram', {}).get('allowFrom') or [None])[0]"
}

telegram_send() {
  local text="$1"

  if [[ "${CRASH_RECOVERY_DISABLE_TELEGRAM:-0}" == "1" ]]; then
    log "[telegram] disabled; would send: $text"
    return 0
  fi

  local bot_token chat_id
  bot_token="$(read_telegram_bot_token || true)"
  chat_id="$(read_telegram_chat_id || true)"

  if [[ -z "$bot_token" || -z "$chat_id" ]]; then
    log "[telegram] not configured (missing botToken or chat_id)."
    return 0
  fi

  # Send a simple message; ignore failures to avoid making recovery worse.
  curl -fsS -X POST "https://api.telegram.org/bot${bot_token}/sendMessage" \
    -d "chat_id=${chat_id}" \
    --data-urlencode "text=${text}" \
    -d "disable_notification=true" \
    >/dev/null 2>&1 || true
}

health_ok() {
  curl -fsS "$HEALTH_URL" >/dev/null 2>&1
}

cron_wake() {
  local token
  token="$(read_gateway_token || true)"

  # Token may be required on some setups. We'll try both ways.
  if [[ -n "$token" ]]; then
    curl -fsS -X POST "$CRON_WAKE_URL" -H "Authorization: Bearer $token" >/dev/null 2>&1 || true
  else
    curl -fsS -X POST "$CRON_WAKE_URL" >/dev/null 2>&1 || true
  fi
}

recover_gateway() {
  # Attempt 1: restart
  log "Attempting: openclaw gateway restart"
  if openclaw gateway restart >>"$LOG_FILE" 2>&1; then
    return 0
  fi

  # Attempt 2: stop+start
  log "Attempting: openclaw gateway stop + start"
  openclaw gateway stop >>"$LOG_FILE" 2>&1 || true
  sleep 2
  if openclaw gateway start >>"$LOG_FILE" 2>&1; then
    return 0
  fi

  return 1
}

main() {
  log "--- crash_recovery check ---"

  if health_ok; then
    log "Gateway healthy."
    exit 0
  fi

  log "Gateway health check FAILED. Starting recovery."
  telegram_send "OpenClaw gateway health check failed. Attempting recovery…"

  local attempt
  for attempt in 1 2 3; do
    log "Recovery attempt $attempt/3"

    if recover_gateway; then
      sleep 2
      if health_ok; then
        log "Recovery succeeded. Gateway is healthy."
        telegram_send "OpenClaw gateway recovered successfully ✅"
        cron_wake
        exit 0
      fi
      log "Gateway restart command succeeded, but health still failing."
    else
      log "Recovery commands failed."
    fi

    if [[ $attempt -lt 3 ]]; then
      log "Waiting 10s before retry…"
      sleep 10
    fi
  done

  log "Recovery failed after 3 attempts."
  telegram_send "OpenClaw gateway recovery FAILED after 3 attempts ❌ (see crash_recovery.log)"
  exit 1
}

main
