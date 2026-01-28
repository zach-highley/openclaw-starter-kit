#!/usr/bin/env python3
"""
Security Hound v2 — Lightweight, Learning Security Monitor

Runs fast, learns what's normal, only alerts on real anomalies.

Features:
- File integrity monitoring (SHA256 of critical files)
- Network intrusion detection (unusual connections)
- Suspicious process scanning
- Alert deduplication (won't spam same alert within 60 min)
- Learning: mark false positives, reduces noise over time

Usage:
    python3 security_hound.py              # Normal scan
    python3 security_hound.py --learn-fp "alert text"  # Mark false positive
"""

import json
import subprocess
import os
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# === CONFIGURATION (customize these paths) ===
WORKSPACE = Path.home() / "clawd"
MEMORY_FILE = WORKSPACE / "memory" / "security-hound.json"

# Critical files to monitor for unauthorized changes
CRITICAL_FILES = [
    Path.home() / ".zshrc",
    Path.home() / ".ssh" / "authorized_keys",
    Path.home() / ".moltbot" / "config.yaml",
    Path("/etc/hosts"),
]

# Known safe network connections
SAFE_PORTS = {22, 80, 443, 8080, 3000, 5000}
SAFE_PROCESSES = {"node", "python", "ruby", "ollama", "ssh", "curl", "git"}


def load_memory():
    """Load learned patterns and known-good items."""
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text())
        except Exception:
            pass
    return {
        "known_devices": [],
        "known_locations": [],
        "known_ips": [],
        "alert_history": [],
        "false_positives": [],
        "last_checks": {},
        "file_hashes": {},
        "known_connections": [],
        "recent_alerts": [],
        "thresholds": {
            "max_failed_logins_per_hour": 5,
            "suspicious_hours": [2, 3, 4, 5],
            "new_device_alert": True,
            "new_location_alert": True,
            "dedup_window_minutes": 60,
        },
        "learned_at": datetime.now().isoformat(),
    }


def save_memory(memory):
    """Persist learned patterns."""
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(memory, indent=2, default=str))


def is_duplicate_alert(memory, alert_text):
    """Check if we've already sent this alert recently."""
    dedup_window = memory.get("thresholds", {}).get("dedup_window_minutes", 60)
    cutoff = datetime.now() - timedelta(minutes=dedup_window)
    for recent in memory.get("recent_alerts", []):
        try:
            alert_time = datetime.fromisoformat(recent.get("timestamp", "2000-01-01"))
            if alert_time > cutoff and recent.get("text", "").lower() == alert_text.lower():
                return True
        except Exception:
            pass
    return False


def record_alert(memory, alert_text):
    """Record alert for deduplication."""
    memory.setdefault("recent_alerts", []).append({
        "text": alert_text,
        "timestamp": datetime.now().isoformat(),
    })
    memory["recent_alerts"] = memory["recent_alerts"][-100:]


def is_false_positive(memory, alert_text):
    """Check if this alert was previously marked as false positive."""
    for fp in memory.get("false_positives", []):
        if fp.lower() in alert_text.lower():
            return True
    return False


def check_file_integrity(memory):
    """Monitor critical files for unexpected changes."""
    alerts, info = [], []
    stored_hashes = memory.get("file_hashes", {})
    new_hashes = {}

    for filepath in CRITICAL_FILES:
        if not filepath.exists():
            continue
        try:
            content = filepath.read_bytes()
            current_hash = hashlib.sha256(content).hexdigest()[:16]
            new_hashes[str(filepath)] = current_hash
            stored_hash = stored_hashes.get(str(filepath))
            if stored_hash and stored_hash != current_hash:
                alerts.append(f"📁 CRITICAL FILE CHANGED: {filepath.name}")
            elif not stored_hash:
                info.append(f"Baseline recorded: {filepath.name}")
        except Exception:
            pass

    memory["file_hashes"] = new_hashes
    return {"alerts": alerts, "info": info}


def check_network_connections(memory):
    """Check for suspicious network connections."""
    alerts, info = [], []
    known = set(memory.get("known_connections", []))

    try:
        result = subprocess.run(
            ["lsof", "-i", "-n", "-P"],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.split("\n")[1:]:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) < 9:
                continue
            process = parts[0].lower()
            if process in SAFE_PROCESSES:
                continue
            connection = parts[8] if len(parts) > 8 else ""
            if "ESTABLISHED" in line and connection not in known:
                alert = f"🌐 New connection: {process} → {connection}"
                if not is_false_positive(memory, alert):
                    alerts.append(alert)
                # Learn this connection
                memory.setdefault("known_connections", []).append(connection)
    except Exception:
        pass

    # Keep known connections list manageable
    memory["known_connections"] = memory.get("known_connections", [])[-500:]
    return {"alerts": alerts, "info": info}


def check_suspicious_processes(memory):
    """Scan for known-bad process patterns."""
    alerts = []
    suspicious_patterns = ["cryptominer", "xmrig", "keylogger", "backdoor", "reverse_shell"]

    try:
        result = subprocess.run(
            ["ps", "aux"], capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.lower().split("\n"):
            for pattern in suspicious_patterns:
                if pattern in line:
                    alerts.append(f"🚨 SUSPICIOUS PROCESS: {pattern} detected!")
    except Exception:
        pass

    return {"alerts": alerts, "info": []}


def main():
    memory = load_memory()

    # Handle --learn-fp flag
    if len(sys.argv) > 2 and sys.argv[1] == "--learn-fp":
        fp_text = " ".join(sys.argv[2:])
        memory.setdefault("false_positives", []).append(fp_text)
        save_memory(memory)
        print(json.dumps({"action": "learned_false_positive", "text": fp_text}))
        return

    # Run all checks
    all_alerts = []
    all_info = []

    for check_fn in [check_file_integrity, check_network_connections, check_suspicious_processes]:
        result = check_fn(memory)
        all_alerts.extend(result.get("alerts", []))
        all_info.extend(result.get("info", []))

    # Filter duplicates and false positives
    new_alerts = []
    for alert in all_alerts:
        if not is_duplicate_alert(memory, alert) and not is_false_positive(memory, alert):
            new_alerts.append(alert)
            record_alert(memory, alert)

    # Update last check time
    memory["last_checks"]["security_hound"] = datetime.now().isoformat()

    save_memory(memory)

    # Output
    output = {
        "timestamp": datetime.now().isoformat(),
        "alerts": new_alerts,
        "info": all_info,
        "should_alert": bool(new_alerts),
        "total_known_connections": len(memory.get("known_connections", [])),
        "total_false_positives": len(memory.get("false_positives", [])),
        "files_monitored": len(memory.get("file_hashes", {})),
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
