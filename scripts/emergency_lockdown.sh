#!/bin/bash
# EMERGENCY LOCKDOWN — Break glass in case of fire
# Kill everything, shut down, or restart. The nuclear option.
#
# Usage:
#   emergency_lockdown.sh kill       # Stop all OpenClaw processes
#   emergency_lockdown.sh shutdown   # Shut down computer in 60s
#   emergency_lockdown.sh restart    # Restart computer in 60s
#   emergency_lockdown.sh cancel     # Cancel pending shutdown
#   emergency_lockdown.sh status     # Check lockdown status

ACTION="${1:-status}"

case "$ACTION" in
  "kill")
    echo "🚨 KILLING ALL OPENCLAW PROCESSES..."
    pkill -f openclaw || true
    pkill -f "node.*gateway" || true
    echo "✅ OpenClaw stopped"
    ;;
  "shutdown")
    echo "🚨 SHUTTING DOWN COMPUTER IN 60 SECONDS..."
    echo "Run '$0 cancel' to abort"
    sudo shutdown -h +1 "Emergency shutdown initiated"
    ;;
  "restart")
    echo "🔄 RESTARTING COMPUTER IN 60 SECONDS..."
    echo "Run '$0 cancel' to abort"
    sudo shutdown -r +1 "Emergency restart initiated"
    ;;
  "cancel")
    echo "❌ CANCELLING SCHEDULED SHUTDOWN..."
    sudo shutdown -c 2>/dev/null || sudo killall shutdown 2>/dev/null || echo "No shutdown to cancel"
    echo "✅ Shutdown cancelled"
    ;;
  "status")
    echo "🔒 LOCKDOWN STATUS"
    echo "OpenClaw running: $(pgrep -f openclaw > /dev/null && echo 'YES' || echo 'NO')"
    echo "Pending shutdown: $(ps aux | grep -v grep | grep shutdown > /dev/null && echo 'YES' || echo 'NO')"
    ;;
  *)
    echo "Usage: emergency_lockdown.sh [kill|shutdown|restart|cancel|status]"
    ;;
esac
