# HEARTBEAT.md

## ⏰ Heartbeat Frequency
**MAX once per hour** to conserve tokens. Skip redundant checks.

## Usage Monitoring (EVERY HEARTBEAT - CRITICAL)
Run `python3 ~/clawd/scripts/check_usage.py` and check the result:
- If `should_alert` is true, message [USER] IMMEDIATELY with the new threshold(s) crossed
- Format: "⚡ [PROVIDER] usage: {percent}% of limit"
- Thresholds: 20%, 40%, 60%, 80%, 90%, 95%, 100%
- At 80%+: Add warning "⚠️ Running low!"
- At 90%+: **CODE RED** - visual indicator if available
- At 95%+: Add warning "🚨 Almost out!"
- At 100%: Add "❌ LIMIT HIT - wait for reset or use API"

## System Monitoring (run every 4th heartbeat / ~4 hours)
Run `python3 ~/clawd/scripts/system_monitor.py` (if set up) and check `has_alerts`:
- If `has_alerts` is true AND alerts are CRITICAL (disk >95%, security issues): message [USER]
- Otherwise: log silently to memory/audit-log.md
- Track last system check in memory/heartbeat-state.json

## 🐕 Security Hound (every heartbeat - FAST)
Run `python3 ~/clawd/scripts/security_hound.py`:
- Lightweight, learning security monitor
- Only alerts if `should_alert` is true (real threats, not noise)
- Learns your devices/locations over time → fewer false positives
- To mark false positive: `python3 ~/clawd/scripts/security_hound.py --learn-fp "alert text"`
- Memory: `memory/security-hound.json`

## Security Audit (SILENT - daily, HEAVY)
Run `python3 ~/clawd/scripts/daily_audit.py`:
- ONLY message [USER] if something is actually scary (unauthorized access, suspicious logins from unknown locations)
- Normal security alerts from known devices = ignore
- Log all results to memory/audit-log.md

## Weekly Tasks (Sunday mornings)
- Run `python3 ~/clawd/scripts/auto_update.py` to update packages
- Run `python3 ~/clawd/scripts/auto_cleanup.py` to clean temp files
- Report summary to [USER]

## 🧠 Incident Learning (every 4th heartbeat)
Check `memory/incidents.md` and `watchdog_metrics.json` for:
- New patterns that need attention
- Recurring issues (3+ same problem = adapt, don't just log)
- Pending "fluke?" determinations to resolve
If a pattern emerges that I haven't adapted to yet, figure out the fix and apply it.
