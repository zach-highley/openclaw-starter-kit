#!/bin/bash
# Watchdog Learning Script v2 — Analyze failures, improve over time
# Called by watchdog.sh after every intervention
#
# How it works:
# 1. Receives trigger info from watchdog
# 2. Analyzes root cause (checks trigger FIRST, then logs)
# 3. Logs incident to WATCHDOG.md
# 4. Tracks patterns for future prevention

set -euo pipefail

LOG_DIR="$HOME/.moltbot/logs"
LEARN_LOG="$LOG_DIR/watchdog-learn.log"
TODAY_LOG="/tmp/moltbot/moltbot-$(date +%Y-%m-%d).log"
WATCHDOG_MD="${WATCHDOG_MD:-$HOME/clawd/WATCHDOG.md}"

LEVEL="${1:-1}"
TRIGGER="${2:-unknown}"
OUTCOME="${3:-unknown}"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LEARN_LOG"; }

log "=== Learning: Level $LEVEL, Trigger: $TRIGGER, Outcome: $OUTCOME ==="

# === ANALYZE ROOT CAUSE (v2: trigger-first, not log-first) ===
ROOT_CAUSE="Unknown"
PREVENTION=""

if [[ "$TRIGGER" == *"model-errors"* ]]; then
    MODEL_ERRORS="${TRIGGER#model-errors:}"
    ROOT_CAUSE="Model errors: ${MODEL_ERRORS//+/, }"
    PREVENTION="Monitor provider status; automated recovery attempted"
elif [[ "$TRIGGER" == *"auth-issue"* ]]; then
    ROOT_CAUSE="Authentication token expired or unavailable"
    PREVENTION="Doctor --fix auto-resolved; consider API key auth"
elif [[ "$TRIGGER" == *"config-issue"* ]]; then
    ROOT_CAUSE="Configuration problem detected by doctor"
    PREVENTION="Review config changes; avoid rapid config patches"
elif [[ "$TRIGGER" == *"model-fallback"* ]]; then
    ROOT_CAUSE="Primary model failed, fallback triggered"
    PREVENTION="Ensure fallback chain is healthy"
elif [[ "$TRIGGER" == *"disk-cleanup"* ]]; then
    ROOT_CAUSE="Disk space exceeded 95%"
    PREVENTION="Review log retention; consider more aggressive cleanup"
elif [[ "$TRIGGER" == *"memory-leak"* ]]; then
    ROOT_CAUSE="Gateway memory exceeded limit"
    PREVENTION="Check for context bloat; consider shorter session TTL"
elif [[ "$TRIGGER" == *"gateway-dead"* ]]; then
    ROOT_CAUSE="Gateway process not found"
    PREVENTION="Check launchd config; verify node installation"
elif [[ "$TRIGGER" == *"heartbeat-silence"* ]]; then
    ROOT_CAUSE="No heartbeat response for extended period"
    PREVENTION="Check if session is stuck; may need context reset"
elif [[ "$TRIGGER" == *"nuclear"* ]]; then
    ROOT_CAUSE="4+ consecutive failures, all recovery failed"
    PREVENTION="Manual investigation needed"
else
    # Fallback: scan logs for clues
    if [[ -f "$TODAY_LOG" ]]; then
        ERRORS=$(tail -100 "$TODAY_LOG" | grep -i "ERROR\|error" | tail -3)
        if echo "$ERRORS" | grep -qi "rate.limit\|429"; then
            ROOT_CAUSE="Rate limit hit"
            PREVENTION="Reduce request frequency or wait for reset"
        elif echo "$ERRORS" | grep -qi "timeout\|timed.out"; then
            ROOT_CAUSE="LLM request timeout"
            PREVENTION="Check network; consider model switch"
        elif echo "$ERRORS" | grep -qi "auth\|token\|expire"; then
            ROOT_CAUSE="Authentication failure"
            PREVENTION="Run doctor --fix"
        fi
    fi
fi

log "Root cause: $ROOT_CAUSE"
log "Prevention: $PREVENTION"

# === LOG INCIDENT TO WATCHDOG.MD ===
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
ERROR_SNIPPET=""
if [[ -f "$TODAY_LOG" ]]; then
    ERROR_SNIPPET=$(tail -5 "$TODAY_LOG" | head -2 | tr '\n' ' ' | cut -c1-200)
fi

INCIDENT_ENTRY="
### Incident: $TIMESTAMP
- **Trigger:** $TRIGGER
- **Level:** $LEVEL
- **Root Cause:** $ROOT_CAUSE
- **Prevention:** $PREVENTION
- **Status:** $OUTCOME
"

# Insert after the incident log marker
if [[ -f "$WATCHDOG_MD" ]]; then
    if grep -q "<!-- New incidents are prepended here" "$WATCHDOG_MD"; then
        sed -i.bak "/<!-- New incidents are prepended here/a\\
$INCIDENT_ENTRY" "$WATCHDOG_MD" 2>/dev/null || true
        rm -f "${WATCHDOG_MD}.bak"
        log "Updated WATCHDOG.md with incident"
    fi
fi

log "=== Learning complete ==="
