#!/usr/bin/env python3
"""
System monitoring script for Moltbot/Moltbot.
Checks: disk, battery, Time Machine, brew outdated, security.
Returns JSON with status and alerts.
"""

import json
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

STATE_FILE = Path.home() / "clawd" / "memory" / "system-state.json"

def run_cmd(cmd, timeout=30):
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except:
        return ""

def get_disk_usage():
    """Get disk usage for root volume."""
    total, used, free = shutil.disk_usage("/")
    pct = (used / total) * 100
    return {
        "total_gb": round(total / (1024**3), 1),
        "used_gb": round(used / (1024**3), 1),
        "free_gb": round(free / (1024**3), 1),
        "percent_used": round(pct, 1)
    }

def get_battery():
    """Get battery info from system_profiler."""
    raw = run_cmd("system_profiler SPPowerDataType 2>/dev/null")
    info = {
        "charge_percent": None,
        "max_capacity_percent": None,
        "cycle_count": None,
        "condition": None,
        "charging": None
    }
    for line in raw.split("\n"):
        line = line.strip()
        if "State of Charge (%)" in line:
            info["charge_percent"] = int(line.split(":")[-1].strip())
        elif "Maximum Capacity" in line:
            val = line.split(":")[-1].strip().replace("%", "")
            info["max_capacity_percent"] = int(val) if val.isdigit() else None
        elif "Cycle Count" in line:
            info["cycle_count"] = int(line.split(":")[-1].strip())
        elif "Condition:" in line:
            info["condition"] = line.split(":")[-1].strip()
        elif "Charging:" in line:
            info["charging"] = "Yes" in line
    return info

def get_timemachine():
    """Get Time Machine backup status."""
    status_raw = run_cmd("tmutil status 2>/dev/null")
    latest_raw = run_cmd("tmutil latestbackup 2>/dev/null")
    
    running = "Running = 1" in status_raw
    percent = None
    if "Percent" in status_raw:
        for line in status_raw.split("\n"):
            if "Percent" in line and "=" in line:
                val = line.split("=")[-1].strip().rstrip(";").strip('"')
                try:
                    percent = float(val)
                    if percent < 0:
                        percent = None
                except:
                    pass
    
    return {
        "running": running,
        "progress_percent": percent,
        "latest_backup": latest_raw if latest_raw else None
    }

def get_brew_outdated():
    """Get list of outdated brew packages."""
    raw = run_cmd("brew outdated --json 2>/dev/null", timeout=60)
    if not raw:
        return {"formulae": [], "casks": [], "count": 0}
    try:
        data = json.loads(raw)
        formulae = data.get("formulae", [])
        casks = data.get("casks", [])
        return {
            "formulae": [f.get("name", f) if isinstance(f, dict) else f for f in formulae[:10]],
            "casks": [c.get("name", c) if isinstance(c, dict) else c for c in casks[:10]],
            "count": len(formulae) + len(casks)
        }
    except:
        return {"formulae": [], "casks": [], "count": 0}

def get_security_info():
    """Basic security checks."""
    # Check SIP status
    sip = run_cmd("csrutil status 2>/dev/null")
    sip_enabled = "enabled" in sip.lower()
    
    # Check FileVault
    fv = run_cmd("fdesetup status 2>/dev/null")
    filevault_on = "On" in fv
    
    # Check firewall
    fw = run_cmd("sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null || echo 'unknown'")
    firewall_on = "enabled" in fw.lower()
    
    return {
        "sip_enabled": sip_enabled,
        "filevault_on": filevault_on,
        "firewall_on": firewall_on
    }

def load_state():
    """Load previous state."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}

def save_state(state):
    """Save state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

def main():
    disk = get_disk_usage()
    battery = get_battery()
    timemachine = get_timemachine()
    brew = get_brew_outdated()
    security = get_security_info()
    
    alerts = []
    
    # Disk alerts
    if disk["percent_used"] > 90:
        alerts.append(f"🔴 CRITICAL: Disk {disk['percent_used']}% full!")
    elif disk["percent_used"] > 80:
        alerts.append(f"🟡 WARNING: Disk {disk['percent_used']}% full")
    
    # Battery alerts
    if battery["max_capacity_percent"] and battery["max_capacity_percent"] < 80:
        alerts.append(f"🔋 Battery health degraded: {battery['max_capacity_percent']}% max capacity")
    if battery["condition"] and battery["condition"] != "Normal":
        alerts.append(f"🔋 Battery condition: {battery['condition']}")
    
    # Brew updates
    if brew["count"] > 10:
        alerts.append(f"📦 {brew['count']} packages need updates")
    
    # Security
    if not security["sip_enabled"]:
        alerts.append("⚠️ System Integrity Protection is DISABLED")
    if not security["filevault_on"]:
        alerts.append("⚠️ FileVault disk encryption is OFF")
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "disk": disk,
        "battery": battery,
        "timemachine": timemachine,
        "brew_outdated": brew,
        "security": security,
        "alerts": alerts,
        "has_alerts": len(alerts) > 0
    }
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
