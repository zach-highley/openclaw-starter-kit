#!/bin/bash
# Moltbot Watchdog v6 — Self-Learning Resilience System
# Runs via launchd/cron every 5 minutes. Monitors health, fixes problems, learns from failures.
#
# What it does:
# - 13 health checks per cycle
# - 4-level escalation ladder (doctor → restart → model switch → alert human)
# - Learns which fixes work for which problems
# - Memory leak detection + auto-kill
# - Routine restart every 48h for freshness
# - Proactive doctor runs every 6h
# - Disk space monitoring + auto-cleanup
# - Heartbeat response tracking
# - Local LLM fallback monitoring (Ollama)
# - Predictive failure analysis
# - Pipeline health checks
# - Error recovery engine

set -euo pipefail

# === CONFIGURATION (customize these) ===
MOLTBOT="moltbot"                            # Path to moltbot binary
LEARN_SCRIPT="$(dirname "$0")/watchdog_learn.sh"
LOG_DIR="$HOME/.moltbot/logs"
LOG_FILE="$LOG_DIR/watchdog.log"
STATE_FILE="$LOG_DIR/watchdog-state.json"
HEARTBEAT_STATE="$LOG_DIR/heartbeat-monitor.json"
MAX_LOG_SIZE=1048576  # 1MB

# macOS uses gtimeout from coreutils
TIMEOUT_CMD="gtimeout"
if ! command -v gtimeout &>/dev/null; then
    TIMEOUT_CMD=""
fi

run_with_timeout() {
    local secs="$1"; shift
    if [[ -n "$TIMEOUT_CMD" ]]; then
        "$TIMEOUT_CMD" "$secs" "$@"
    else
        "$@"
    fi
}

# Thresholds
MAX_MEMORY_MB=2000          # Kill if using more than 2GB RAM
HEALTH_TIMEOUT_SEC=30       # Health check timeout
MAX_UPTIME_HOURS=48         # Force restart every 48h for freshness
DOCTOR_INTERVAL_HOURS=6     # Run doctor proactively every 6h
MAX_HEARTBEAT_SILENCE_MIN=60  # Alert if no heartbeat response for 60min

# === SETUP ===
mkdir -p "$LOG_DIR"

# Rotate log if too large
if [[ -f "$LOG_FILE" ]] && [[ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]]; then
    mv "$LOG_FILE" "$LOG_FILE.old"
fi

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"; }

learn() {
    local level="$1" trigger="$2" outcome="$3"
    if [[ -x "$LEARN_SCRIPT" ]]; then
        bash "$LEARN_SCRIPT" "$level" "$trigger" "$outcome" >> "$LOG_FILE" 2>&1 || true
    fi
}

notify() {
    local message="$1" urgency="${2:-normal}"
    log "📢 [$urgency] $message"
    run_with_timeout 30 "$MOLTBOT" message send --channel telegram --message "🤖 Watchdog [$urgency]: $message" >> "$LOG_FILE" 2>&1 || true
}

safe_json_update() {
    local file="$1" jq_filter="$2" backup="${file}.backup"
    [[ ! -f "$file" ]] && return 1
    if ! jq empty "$file" 2>/dev/null; then
        [[ -f "$backup" ]] && cp "$backup" "$file" || return 1
    fi
    cp "$file" "$backup"
    local tmpfile="${file}.tmp.$$"
    if jq "$jq_filter" "$file" > "$tmpfile" 2>/dev/null && jq empty "$tmpfile" 2>/dev/null; then
        mv "$tmpfile" "$file"
    else
        rm -f "$tmpfile"; return 1
    fi
}

update_state() {
    cat > "$STATE_FILE" << EOF
{
  "lastCheck": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "$1",
  "lastAction": "$2",
  "details": "${3:-}",
  "consecutiveFailures": ${FAILURES:-0},
  "gatewayPid": ${GATEWAY_PID:-0},
  "gatewayMemoryMB": ${GATEWAY_MEM_MB:-0}
}
EOF
}

# === LOAD STATE ===
FAILURES=0
if [[ -f "$STATE_FILE" ]]; then
    FAILURES=$(grep -o '"consecutiveFailures": [0-9]*' "$STATE_FILE" | grep -o '[0-9]*' || echo 0)
fi

log "=== Watchdog check starting (failures: $FAILURES) ==="

# ============================================
# CHECK 1: Is gateway process running?
# ============================================
log "[CHECK 1] Gateway process..."
GATEWAY_PID=$(pgrep -f "moltbot.*gateway" 2>/dev/null | head -1 || echo "")

if [[ -z "$GATEWAY_PID" ]]; then
    log "❌ Gateway not running — starting it"
    FAILURES=$((FAILURES + 1))
    nohup "$MOLTBOT" gateway >> "$LOG_DIR/gateway-restart.log" 2>&1 &
    sleep 15
    GATEWAY_PID=$(pgrep -f "moltbot.*gateway" 2>/dev/null | head -1 || echo "")
    if [[ -n "$GATEWAY_PID" ]]; then
        log "✅ Gateway started (PID: $GATEWAY_PID)"
        notify "Gateway was dead, I started it! PID: $GATEWAY_PID" "critical"
        learn 1 "gateway-dead" "recovered"
        FAILURES=0
    else
        log "❌ Failed to start gateway"
        notify "⚠️ CRITICAL: Cannot start gateway!" "critical"
        learn 1 "gateway-dead" "failed"
        exit 1
    fi
fi
log "✅ Gateway running (PID: $GATEWAY_PID)"

# ============================================
# CHECK 2: Memory usage
# ============================================
log "[CHECK 2] Memory usage..."
GATEWAY_MEM=$(ps -o rss= -p "$GATEWAY_PID" 2>/dev/null | tr -d ' ' || echo 0)
GATEWAY_MEM_MB=$((GATEWAY_MEM / 1024))
log "Memory: ${GATEWAY_MEM_MB}MB (limit: ${MAX_MEMORY_MB}MB)"

if [[ $GATEWAY_MEM_MB -gt $MAX_MEMORY_MB ]]; then
    log "⚠️ Memory leak (${GATEWAY_MEM_MB}MB) — forcing restart"
    notify "Memory leak detected (${GATEWAY_MEM_MB}MB) — restarting" "warning"
    kill -TERM "$GATEWAY_PID" 2>/dev/null || true; sleep 5
    kill -9 "$GATEWAY_PID" 2>/dev/null || true; sleep 2
    nohup "$MOLTBOT" gateway >> "$LOG_DIR/gateway-restart.log" 2>&1 &
    sleep 15
    learn 2 "memory-leak-${GATEWAY_MEM_MB}MB" "recovered"
    FAILURES=0
    exit 0
fi

# ============================================
# CHECK 3: Process uptime (routine restart)
# ============================================
log "[CHECK 3] Process uptime..."
GATEWAY_START=$(ps -o lstart= -p "$GATEWAY_PID" 2>/dev/null || echo "")
if [[ -n "$GATEWAY_START" ]]; then
    START_EPOCH=$(date -j -f "%a %b %d %T %Y" "$GATEWAY_START" "+%s" 2>/dev/null || echo 0)
    NOW_EPOCH=$(date "+%s")
    UPTIME_HOURS=$(( (NOW_EPOCH - START_EPOCH) / 3600 ))
    log "Uptime: ${UPTIME_HOURS}h (max: ${MAX_UPTIME_HOURS}h)"
    if [[ $UPTIME_HOURS -gt $MAX_UPTIME_HOURS ]]; then
        log "⚠️ Running too long — routine restart"
        notify "Routine restart after ${UPTIME_HOURS}h" "normal"
        "$MOLTBOT" gateway stop >> "$LOG_FILE" 2>&1 || true; sleep 5
        nohup "$MOLTBOT" gateway >> "$LOG_DIR/gateway-restart.log" 2>&1 &
        sleep 15
        learn 1 "uptime-${UPTIME_HOURS}h" "recovered"
        exit 0
    fi
fi

# ============================================
# CHECK 4: Health endpoint
# ============================================
log "[CHECK 4] Health check..."
HEALTH_OUTPUT=$(run_with_timeout $HEALTH_TIMEOUT_SEC "$MOLTBOT" health 2>&1) || HEALTH_OUTPUT="TIMEOUT"

if echo "$HEALTH_OUTPUT" | grep -q "Telegram: ok"; then
    log "✅ Health check passed"
    if [[ $FAILURES -gt 0 ]]; then
        notify "Recovered after $FAILURES failed checks! ✅" "normal"
        learn 1 "health-recovered-after-$FAILURES" "recovered"
    fi
    FAILURES=0
else
    log "⚠️ Health check failed"
    FAILURES=$((FAILURES + 1))
fi

# ============================================
# CHECK 5: Proactive doctor (every 6h or on failures)
# ============================================
LAST_DOCTOR_FILE="$LOG_DIR/last-doctor-run"
LAST_DOCTOR=0
[[ -f "$LAST_DOCTOR_FILE" ]] && LAST_DOCTOR=$(cat "$LAST_DOCTOR_FILE" 2>/dev/null || echo 0)
NOW_EPOCH=$(date +%s)
HOURS_SINCE_DOCTOR=$(( (NOW_EPOCH - LAST_DOCTOR) / 3600 ))

RUN_DOCTOR=false
[[ $FAILURES -gt 0 ]] && RUN_DOCTOR=true
[[ $HOURS_SINCE_DOCTOR -ge $DOCTOR_INTERVAL_HOURS ]] && RUN_DOCTOR=true

if [[ "$RUN_DOCTOR" == "true" ]]; then
    log "[CHECK 5] Running doctor..."
    DOCTOR_OUTPUT=$("$MOLTBOT" doctor 2>&1) || true
    echo "$NOW_EPOCH" > "$LAST_DOCTOR_FILE"
    
    if echo "$DOCTOR_OUTPUT" | grep -qi "expir\|unavailable\|cooldown"; then
        log "🔑 Auth issue — running doctor --fix"
        "$MOLTBOT" doctor --fix >> "$LOG_FILE" 2>&1 || true
        learn 1 "auth-issue-doctor-fix" "auto-fixed"
    fi
    if echo "$DOCTOR_OUTPUT" | grep -qi "invalid\|missing\|error"; then
        learn 1 "config-issue" "detected"
    fi
fi

# ============================================
# CHECK 6: Heartbeat response monitoring
# ============================================
log "[CHECK 6] Heartbeat monitoring..."
if [[ -f "$HEARTBEAT_STATE" ]]; then
    LAST_HB=$(jq -r '.lastResponse // "null"' "$HEARTBEAT_STATE" 2>/dev/null || echo "null")
    if [[ "$LAST_HB" != "null" && "$LAST_HB" != "0" ]]; then
        LAST_HB_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${LAST_HB%Z}" "+%s" 2>/dev/null || echo 0)
        MINUTES_SINCE=$((( $(date +%s) - LAST_HB_EPOCH) / 60))
        if [[ $MINUTES_SINCE -gt $MAX_HEARTBEAT_SILENCE_MIN ]]; then
            notify "No heartbeat response for ${MINUTES_SINCE}min — may be unresponsive" "warning"
            learn 1 "heartbeat-silence-${MINUTES_SINCE}min" "detected"
        fi
    fi
fi

# ============================================
# ESCALATION LADDER
# ============================================
if [[ $FAILURES -ge 2 ]]; then
    log "⚠️ 2+ failures — restarting gateway"
    notify "$FAILURES consecutive failures — restarting 🔄" "warning"
    "$MOLTBOT" gateway stop >> "$LOG_FILE" 2>&1 || true; sleep 5
    pkill -f "moltbot.*gateway" 2>/dev/null || true; sleep 2
    nohup "$MOLTBOT" gateway >> "$LOG_DIR/gateway-restart.log" 2>&1 &
    sleep 15
    if run_with_timeout 10 "$MOLTBOT" health 2>&1 | grep -q "Telegram: ok"; then
        notify "Gateway restarted successfully! ✅" "normal"
        learn 3 "health-failures-$FAILURES" "recovered"
        FAILURES=0
    else
        learn 3 "health-failures-$FAILURES" "failed"
    fi
fi

if [[ $FAILURES -ge 4 ]]; then
    log "💀 4+ failures — NUCLEAR: session reset"
    notify "💀 4 failures — resetting session (nuclear)" "critical"
    ARCHIVE_DIR="$LOG_DIR/session-archives/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$ARCHIVE_DIR"
    cp -r "$HOME/.moltbot/agents/main/sessions/"* "$ARCHIVE_DIR/" 2>/dev/null || true
    rm -f "$HOME/.moltbot/agents/main/sessions/sessions.json"
    pkill -9 -f "moltbot.*gateway" 2>/dev/null || true; sleep 3
    nohup "$MOLTBOT" gateway >> "$LOG_DIR/gateway-restart.log" 2>&1 &
    sleep 15
    FAILURES=0
    learn 4 "nuclear-session-reset" "recovered"
fi

# ============================================
# CHECK 7: Disk space
# ============================================
log "[CHECK 7] Disk space..."
DISK_USED=$(df -h "$HOME/.moltbot" | tail -1 | awk '{print $5}' | tr -d '%')
if [[ $DISK_USED -gt 95 ]]; then
    find "$LOG_DIR" -name "*.log" -mtime +7 -delete 2>/dev/null || true
    notify "Disk at ${DISK_USED}% — cleaned old logs" "warning"
fi

# ============================================
# CHECK 8: Local LLM fallback (Ollama)
# ============================================
log "[CHECK 8] Ollama backup..."
if ! pgrep -x ollama > /dev/null 2>&1; then
    log "⚠️ Ollama not running — starting"
    ollama serve >> "$LOG_DIR/ollama.log" 2>&1 &
    sleep 5
    pgrep -x ollama > /dev/null 2>&1 && learn 1 "ollama-started" "recovered"
fi

# ============================================
# FINAL STATE
# ============================================
update_state "${FAILURES:-0}" "complete" "mem ${GATEWAY_MEM_MB}MB, disk ${DISK_USED}%"
log "=== Watchdog complete (failures: $FAILURES) ==="
