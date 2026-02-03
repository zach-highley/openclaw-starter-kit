#!/bin/bash
# Daily 5 AM maintenance routine
# - Run openclaw doctor
# - Run openclaw doctor --fix
# - Reset gateway
# - Trigger /new session
#
# This is the ONLY scheduled maintenance. No watchdogs, no guardians.

set -euo pipefail

LOG_FILE="$HOME/.openclaw/logs/daily-maintenance.log"
TELEGRAM_SCRIPT="$HOME/.openclaw/workspace/scripts/health_notify_telegram.py"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

notify_telegram() {
  # Simple out-of-band Telegram notification (doesn't need gateway)
  local msg="$1"
  python3 "$HOME/.openclaw/workspace/scripts/simple_telegram_notify.py" "$msg" 2>/dev/null || true
}

log "=== Daily 5 AM maintenance starting ==="

# Step 1: Check gateway status
log "Step 1: Checking gateway status..."
if curl -s --max-time 5 http://127.0.0.1:18789 >/dev/null 2>&1; then
  log "Gateway is running"
else
  log "Gateway was DOWN - will be fixed by doctor --fix"
  notify_telegram "🔴 Daily 5 AM: Gateway was down. Running doctor --fix..."
fi

# Step 2: Run openclaw doctor
log "Step 2: Running openclaw doctor..."
openclaw doctor 2>&1 | tee -a "$LOG_FILE" || true

# Step 3: Run openclaw doctor --fix
log "Step 3: Running openclaw doctor --fix..."
openclaw doctor --fix 2>&1 | tee -a "$LOG_FILE" || true

# Step 4: Wait for gateway to be ready
log "Step 4: Waiting for gateway..."
sleep 10

# Step 5: Verify gateway is up
if curl -s --max-time 5 http://127.0.0.1:18789 >/dev/null 2>&1; then
  log "✅ Gateway is healthy"
  notify_telegram "🟢 Daily 5 AM maintenance complete. Gateway healthy. Starting fresh session."
else
  log "❌ Gateway still not responding after doctor --fix"
  notify_telegram "🔴 Daily 5 AM: Gateway STILL DOWN after doctor --fix. Manual intervention needed."
  exit 1
fi

# Step 6: Trigger /new session via gateway
log "Step 6: Triggering /new session..."
# This will be handled by the cron job that triggers the agent

log "=== Daily 5 AM maintenance complete ==="
