#!/bin/bash
# Telegram Echo Test
# actively sends a test message to verify API reachability
# 
# Requires: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars

set -euo pipefail

if [[ -z "$TELEGRAM_BOT_TOKEN" || -z "$TELEGRAM_CHAT_ID" ]]; then
    echo '{"status": "skipped", "reason": "missing_credentials"}'
    exit 0
fi

# Send test message
RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d chat_id="${TELEGRAM_CHAT_ID}" \
    -d text="🔧 Echo test (auto-deleted)" \
    -d disable_notification=true)

if echo "$RESPONSE" | grep -q '"ok":true'; then
    # Extract message ID to delete it
    MSG_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['result']['message_id'])")
    
    # Delete it immediately
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/deleteMessage" \
        -d chat_id="${TELEGRAM_CHAT_ID}" \
        -d message_id="$MSG_ID" > /dev/null
        
    echo '{"status": "healthy"}'
else
    echo '{"status": "unhealthy", "response": "'"$RESPONSE"'"}'
fi
