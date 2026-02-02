#!/bin/bash
# OpenClaw Out-of-Band Watchdog (safe-dumb)
#
# Goal: Keep the local OpenClaw gateway alive using ONLY local actions.
# - Checks gateway health
# - Restarts gateway when unhealthy
# - ONLY runs `openclaw doctor --repair --non-interactive` if restart fails
# - Uses a lockfile + rate limiting
# - Kill-switch support
# - Writes structured JSONL logs (no secrets)
# - Sends Telegram "recovered" notification via direct Telegram API (no gateway required)
#
# This script is intended to be executed by launchd on macOS.

set -euo pipefail

OPENCLAW_BIN="${OPENCLAW_BIN:-openclaw}"

# --- Paths (no hardcoded user paths; everything based on $HOME) ---
WATCHDOG_HOME="${OPENCLAW_WATCHDOG_HOME:-$HOME/.config/openclaw-watchdog}"
WATCHDOG_SHARE="${OPENCLAW_WATCHDOG_SHARE:-$HOME/.local/share/openclaw-watchdog}"
WATCHDOG_CACHE="${OPENCLAW_WATCHDOG_CACHE:-$HOME/Library/Caches/OpenClaw/watchdog}"
WATCHDOG_LOG_DIR="${OPENCLAW_WATCHDOG_LOG_DIR:-$HOME/Library/Logs/OpenClaw}"

CONFIG_ENV="$WATCHDOG_HOME/config.env"
KILL_SWITCH_FILE="$WATCHDOG_HOME/disabled"
STATE_FILE="$WATCHDOG_CACHE/state.json"
LOCK_DIR="$WATCHDOG_CACHE/lock"
LOG_FILE="$WATCHDOG_LOG_DIR/watchdog.jsonl"

# --- Tunables ---
START_INTERVAL_SEC="${OPENCLAW_WATCHDOG_START_INTERVAL_SEC:-60}"
HEALTH_TIMEOUT_SEC="${OPENCLAW_WATCHDOG_HEALTH_TIMEOUT_SEC:-10}"
RESTART_TIMEOUT_SEC="${OPENCLAW_WATCHDOG_RESTART_TIMEOUT_SEC:-30}"
REPAIR_TIMEOUT_SEC="${OPENCLAW_WATCHDOG_REPAIR_TIMEOUT_SEC:-300}"
REPAIR_MIN_INTERVAL_SEC="${OPENCLAW_WATCHDOG_REPAIR_MIN_INTERVAL_SEC:-21600}" # 6h
LOCK_STALE_SEC="${OPENCLAW_WATCHDOG_LOCK_STALE_SEC:-600}" # 10m

mkdir -p "$WATCHDOG_HOME" "$WATCHDOG_SHARE" "$WATCHDOG_CACHE" "$WATCHDOG_LOG_DIR"

# Load optional config env (token/chat id, etc).
if [[ -f "$CONFIG_ENV" ]]; then
  # shellcheck disable=SC1090
  set +u
  source "$CONFIG_ENV"
  set -u
fi

now_epoch() { date +%s; }
now_iso() { date -u +%Y-%m-%dT%H:%M:%SZ; }

json_escape() {
  # Minimal JSON string escape for log messages (avoid dependencies)
  local s="$1"
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\n'/\\n}
  s=${s//$'\r'/\\r}
  s=${s//$'\t'/\\t}
  printf '%s' "$s"
}

log_json() {
  local level="$1" event="$2" msg="$3"
  local ts; ts="$(now_iso)"
  printf '{"ts":"%s","level":"%s","event":"%s","msg":"%s"}\n' \
    "$ts" "$(json_escape "$level")" "$(json_escape "$event")" "$(json_escape "$msg")" >> "$LOG_FILE"
}

# Never log secrets: do NOT log env dumps, config contents, curl URLs, or command output.

with_timeout() {
  local secs="$1"; shift
  if command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$secs" "$@"
  elif command -v timeout >/dev/null 2>&1; then
    timeout "$secs" "$@"
  else
    "$@"
  fi
}

acquire_lock() {
  local now; now="$(now_epoch)"
  if mkdir "$LOCK_DIR" 2>/dev/null; then
    echo "$now" > "$LOCK_DIR/ts"
    return 0
  fi

  # Lock exists. If stale, remove it.
  local lock_ts="0"
  if [[ -f "$LOCK_DIR/ts" ]]; then
    lock_ts=$(cat "$LOCK_DIR/ts" 2>/dev/null || echo 0)
  fi
  if [[ $((now - lock_ts)) -gt "$LOCK_STALE_SEC" ]]; then
    rm -rf "$LOCK_DIR" 2>/dev/null || true
    if mkdir "$LOCK_DIR" 2>/dev/null; then
      echo "$now" > "$LOCK_DIR/ts"
      log_json "warn" "lock.stale" "Stale lock cleared"
      return 0
    fi
  fi

  return 1
}

release_lock() {
  rm -rf "$LOCK_DIR" 2>/dev/null || true
}

state_get() {
  local key="$1"
  [[ -f "$STATE_FILE" ]] || return 1
  # naive JSON parse (file is ours) – keep it dependency-free
  grep -E '"'"$key"'"\s*:\s*"' "$STATE_FILE" | head -n1 | sed -E 's/.*:\s*"(.*)".*/\1/'
}

state_set() {
  local status="$1" last_ok_epoch="$2" last_repair_epoch="$3"
  cat > "$STATE_FILE" <<EOF
{"status":"$status","last_ok_epoch":"$last_ok_epoch","last_repair_epoch":"$last_repair_epoch"}
EOF
}

telegram_notify_recovered() {
  # Only sends on recovery. Uses direct Telegram API (no gateway dependency).
  local text="$1"
  if [[ -z "${OPENCLAW_WATCHDOG_TELEGRAM_BOT_TOKEN:-}" || -z "${OPENCLAW_WATCHDOG_TELEGRAM_CHAT_ID:-}" ]]; then
    return 0
  fi

  # IMPORTANT: Do not log token or full URL. Also silence stderr.
  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "https://api.telegram.org/bot${OPENCLAW_WATCHDOG_TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d "chat_id=${OPENCLAW_WATCHDOG_TELEGRAM_CHAT_ID}" \
    --data-urlencode "text=${text}" \
    2>/dev/null || echo "000")

  if [[ "$http_code" == "200" ]]; then
    log_json "info" "notify.telegram" "Recovery notification sent"
  else
    log_json "warn" "notify.telegram" "Recovery notification failed (http=${http_code})"
  fi
}

is_healthy() {
  # Health check: try `openclaw health` (fast). Any failure => unhealthy.
  # We deliberately do not log command output.
  if with_timeout "$HEALTH_TIMEOUT_SEC" "$OPENCLAW_BIN" health >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

restart_gateway() {
  # Try the simplest safe restart.
  if with_timeout "$RESTART_TIMEOUT_SEC" "$OPENCLAW_BIN" gateway restart >/dev/null 2>&1; then
    return 0
  fi

  # Fallback: stop + start.
  with_timeout 15 "$OPENCLAW_BIN" gateway stop >/dev/null 2>&1 || true
  if with_timeout "$RESTART_TIMEOUT_SEC" "$OPENCLAW_BIN" gateway >/dev/null 2>&1; then
    return 0
  fi

  return 1
}

repair_if_allowed() {
  local now; now="$(now_epoch)"
  local last_repair="0"
  last_repair=$(state_get last_repair_epoch 2>/dev/null || echo 0)
  if [[ -z "$last_repair" ]]; then last_repair=0; fi

  if [[ $((now - last_repair)) -lt "$REPAIR_MIN_INTERVAL_SEC" ]]; then
    log_json "warn" "repair.rate_limited" "Repair skipped due to rate limit"
    return 2
  fi

  log_json "warn" "repair.start" "Running openclaw doctor --repair --non-interactive"
  if with_timeout "$REPAIR_TIMEOUT_SEC" "$OPENCLAW_BIN" doctor --repair --non-interactive >/dev/null 2>&1; then
    log_json "info" "repair.ok" "Repair completed"
    local status; status=$(state_get status 2>/dev/null || echo "unknown")
    local last_ok; last_ok=$(state_get last_ok_epoch 2>/dev/null || echo 0)
    state_set "$status" "$last_ok" "$now"
    return 0
  else
    log_json "error" "repair.fail" "Repair failed"
    local status; status=$(state_get status 2>/dev/null || echo "unknown")
    local last_ok; last_ok=$(state_get last_ok_epoch 2>/dev/null || echo 0)
    state_set "$status" "$last_ok" "$now"
    return 1
  fi
}

main() {
  if [[ -f "$KILL_SWITCH_FILE" ]]; then
    log_json "info" "watchdog.disabled" "Kill-switch is enabled; exiting"
    exit 0
  fi

  if ! acquire_lock; then
    # Another watchdog run in progress.
    exit 0
  fi
  trap release_lock EXIT

  local prev_status="unknown"
  prev_status=$(state_get status 2>/dev/null || echo "unknown")

  if is_healthy; then
    local now; now="$(now_epoch)"
    local last_repair; last_repair=$(state_get last_repair_epoch 2>/dev/null || echo 0)
    state_set "healthy" "$now" "$last_repair"

    if [[ "$prev_status" != "healthy" ]]; then
      telegram_notify_recovered "✅ OpenClaw gateway recovered (watchdog)"
    fi

    log_json "info" "health.ok" "Gateway healthy"
    exit 0
  fi

  log_json "warn" "health.fail" "Gateway unhealthy; attempting restart"

  if restart_gateway; then
    # Give it a moment, then re-check.
    sleep 3
    if is_healthy; then
      local now; now="$(now_epoch)"
      local last_repair; last_repair=$(state_get last_repair_epoch 2>/dev/null || echo 0)
      state_set "healthy" "$now" "$last_repair"
      telegram_notify_recovered "✅ OpenClaw gateway recovered (watchdog restart)"
      log_json "info" "restart.ok" "Restart succeeded"
      exit 0
    fi
  fi

  log_json "error" "restart.fail" "Restart failed; considering repair"

  # Restart failed. Only now do we attempt a repair.
  repair_if_allowed || true

  log_json "warn" "post_repair.restart" "Attempting restart after repair"
  restart_gateway || true
  sleep 3

  if is_healthy; then
    local now; now="$(now_epoch)"
    local last_repair; last_repair=$(state_get last_repair_epoch 2>/dev/null || echo 0)
    state_set "healthy" "$now" "$last_repair"
    telegram_notify_recovered "✅ OpenClaw gateway recovered (watchdog repair)"
    log_json "info" "recovered" "Gateway recovered"
    exit 0
  fi

  # Still down.
  local last_ok; last_ok=$(state_get last_ok_epoch 2>/dev/null || echo 0)
  local last_repair; last_repair=$(state_get last_repair_epoch 2>/dev/null || echo 0)
  state_set "unhealthy" "$last_ok" "$last_repair"
  log_json "error" "still_down" "Gateway still unhealthy after restart/repair"

  exit 1
}

main "$@"
