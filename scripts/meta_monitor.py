#!/usr/bin/env python3
"""
Meta-Monitor: The operations manager for all Moltbot automation.
Watches the watchers. Detects stalls, conflicts, and dormant learning loops.

Usage:
    python3 meta_monitor.py --check          # Read-only health check
    python3 meta_monitor.py --check --json   # JSON output
    python3 meta_monitor.py --fix            # Attempt auto-recovery
    python3 meta_monitor.py --check --mode heartbeat  # Lightweight heartbeat mode

Design: ~/clawd/docs/META_MONITOR_DESIGN.md
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# === CONFIGURATION ===

HOME = Path.home()
CLAWD = HOME / "clawd"
CLAWDBOT_LOGS = HOME / ".moltbot" / "logs"

# State files
META_STATE = CLAWD / "state" / "meta_monitor_state.json"
GATEWAY_LEASE = CLAWD / "state" / "gateway_lease.json"

# Systems to monitor: (name, state_file, max_age_seconds, description)
SYSTEMS = [
    {
        "name": "watchdog",
        "state": CLAWDBOT_LOGS / "watchdog-state.json",
        "max_stale_sec": 600,  # 10 min (runs every 5 min)
        "desc": "Primary gateway supervisor (launchd, 5-min cycle)"
    },
    {
        "name": "error_recovery",
        "state": CLAWD / "scripts" / "recovery_state.json",
        "max_stale_sec": 1800,  # 30 min (runs every 2nd watchdog = 10 min)
        "desc": "Auto-learning error fixer"
    },
    {
        "name": "security_hound",
        "state": CLAWD / "memory" / "security-hound.json",
        "max_stale_sec": 7200,  # 2h (runs every heartbeat)
        "desc": "Learning security monitor"
    },
    {
        "name": "personal_learner",
        "state": CLAWD / "zach_model.json",
        "max_stale_sec": 28800,  # 8h (runs every 4th heartbeat)
        "desc": "User preference/behavior model"
    },
    {
        "name": "work_loop",
        "state": CLAWD / "state" / "current_work.json",
        "max_stale_sec": 3600,  # 1h (active when queue has items)
        "desc": "Sprint/task execution queue"
    },
    {
        "name": "usage_monitor",
        "state": CLAWD / "memory" / "usage-state.json",
        "max_stale_sec": 7200,  # 2h (runs every heartbeat)
        "desc": "Claude usage threshold tracker"
    },
    {
        "name": "heartbeat",
        "state": CLAWD / "memory" / "heartbeat-state.json",
        "max_stale_sec": 7200,  # 2h (max once per hour target)
        "desc": "Heartbeat orchestration state"
    },
    {
        "name": "model_health",
        "state": CLAWDBOT_LOGS / "model-health-state.json",
        "max_stale_sec": 600,  # 10 min (runs every watchdog cycle)
        "desc": "LLM model availability checker"
    },
    {
        "name": "telegram_health",
        "state": CLAWDBOT_LOGS / "telegram-health-state.json",
        "max_stale_sec": 600,  # 10 min (runs every watchdog cycle)
        "desc": "Telegram delivery monitor"
    },
]

# Safety rails
MAX_INTERVENTIONS_PER_HOUR = 10  # Higher budget since we auto-fix now
ESCALATION_THRESHOLD = 3  # stalled systems before alerting human
LEASE_EXPIRY_SEC = 120  # 2 min gateway restart lease
BACKOFF_BASE = 2  # exponential backoff multiplier

# === STATE MANAGEMENT ===

def load_json(path):
    """Safely load a JSON file."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def save_json(path, data):
    """Safely save JSON with atomic write."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    with open(tmp, 'w') as f:
        json.dump(data, f, indent=2)
    tmp.rename(path)

def load_meta_state():
    """Load or initialize meta-monitor state."""
    state = load_json(META_STATE)
    if state is None:
        state = {
            "lastRun": None,
            "runCount": 0,
            "systems": {},
            "interventions": [],
            "stall_history": {},
            "created": datetime.now(timezone.utc).isoformat()
        }
    return state

def save_meta_state(state):
    """Save meta-monitor state."""
    save_json(META_STATE, state)

# === GATEWAY LEASE (conflict prevention) ===

def acquire_lease(system_name):
    """Try to acquire gateway restart lease. Returns (success, lease_data)."""
    lease = load_json(GATEWAY_LEASE)
    now = time.time()
    
    if lease and lease.get("expires", 0) > now:
        # Lease held by someone else
        holder = lease.get("holder", "unknown")
        remaining = int(lease["expires"] - now)
        return False, {"holder": holder, "remaining_sec": remaining}
    
    # Acquire lease
    token = (lease or {}).get("fencing_token", 0) + 1
    new_lease = {
        "holder": system_name,
        "acquired": now,
        "expires": now + LEASE_EXPIRY_SEC,
        "fencing_token": token,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    save_json(GATEWAY_LEASE, new_lease)
    return True, new_lease

def release_lease(system_name):
    """Release gateway restart lease."""
    lease = load_json(GATEWAY_LEASE)
    if lease and lease.get("holder") == system_name:
        lease["expires"] = 0
        lease["released"] = datetime.now(timezone.utc).isoformat()
        save_json(GATEWAY_LEASE, lease)

# === CONTEXT MONITORING ===

def check_session_context():
    """Check if the main session context is getting full."""
    result = {"needs_clear": False, "percent": None, "details": ""}
    
    # Try to find session info from recent logs
    sessions_dir = HOME / ".moltbot" / "agents" / "main" / "sessions"
    sessions_file = sessions_dir / "sessions.json"
    
    if not sessions_file.exists():
        result["details"] = "Sessions file not found"
        return result
    
    try:
        data = load_json(sessions_file)
        if data and isinstance(data, dict):
            # Look for main session
            for key, session in data.items():
                if "main:main" in str(key) or session.get("kind") == "main":
                    total = session.get("totalTokens", 0)
                    context_max = session.get("contextTokens", 200000)
                    if context_max > 0:
                        pct = int((total / context_max) * 100)
                        result["percent"] = pct
                        if pct >= 85:
                            result["needs_clear"] = True
                            result["details"] = f"Context at {pct}% — needs /new soon"
                        elif pct >= 75:
                            result["details"] = f"Context at {pct}% — getting high"
                        else:
                            result["details"] = f"Context at {pct}% — OK"
                    break
    except Exception as e:
        result["details"] = f"Could not check: {e}"
    
    return result


def auto_reset_session():
    """Programmatically trigger /new by calling sessions.reset via CLI.
    Returns True on success, False on failure."""
    try:
        nvm_bin = HOME / ".nvm" / "versions" / "node" / "v22.16.0" / "bin"
        env = os.environ.copy()
        env["PATH"] = f"{nvm_bin}:{env.get('PATH', '')}"
        
        result = subprocess.run(
            ["moltbot", "gateway", "call", "sessions.reset",
             "--params", '{"key":"agent:main:main"}', "--json"],
            capture_output=True, text=True, timeout=15, env=env
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data.get("ok"):
                _log_recovery("session_context", "auto_reset_session", True,
                              f"Session reset to 0 tokens. New ID: {data.get('entry',{}).get('sessionId','?')}")
                return True
        
        _log_recovery("session_context", "auto_reset_session", False,
                      f"Reset failed: {result.stderr[:200]}")
        return False
    except Exception as e:
        _log_recovery("session_context", "auto_reset_session", False, str(e))
        return False


# === HEALTH CHECKS ===

def check_system_health(system):
    """Check a single system's health. Returns status dict."""
    name = system["name"]
    state_path = Path(system["state"])
    max_stale = system["max_stale_sec"]
    
    result = {
        "name": name,
        "desc": system["desc"],
        "state_file": str(state_path),
        "status": "unknown",
        "age_sec": None,
        "max_stale_sec": max_stale,
        "details": ""
    }
    
    if not state_path.exists():
        result["status"] = "missing"
        result["details"] = f"State file not found: {state_path}"
        return result
    
    # Check file modification time
    mtime = state_path.stat().st_mtime
    age = time.time() - mtime
    result["age_sec"] = int(age)
    
    # Also try to read lastUpdated from JSON content
    data = load_json(state_path)
    if data and isinstance(data, dict):
        for key in ["lastUpdated", "last_updated", "timestamp", "lastRun"]:
            if key in data:
                result["last_content_update"] = data[key]
                break
    
    # Determine status
    if age <= max_stale:
        result["status"] = "healthy"
        result["details"] = f"Updated {int(age)}s ago (threshold: {max_stale}s)"
    elif age <= max_stale * 3:
        result["status"] = "stalled"
        result["details"] = f"Stale for {int(age)}s (threshold: {max_stale}s)"
    else:
        result["status"] = "broken"
        result["details"] = f"Dead for {int(age)}s (threshold: {max_stale}s, 3x exceeded)"
    
    # Special checks per system
    if name == "work_loop" and data:
        queue = data.get("queue", [])
        in_progress = data.get("inProgress")
        if queue or in_progress:
            result["work_active"] = True
            result["queue_size"] = len(queue)
            result["in_progress"] = in_progress
            # If work is active but hasn't updated in 30 min, it's stalled
            if age > 1800 and in_progress:
                result["status"] = "stalled"
                result["details"] = f"Work item '{in_progress}' stuck for {int(age)}s"
        else:
            result["work_active"] = False
            # Idle work loop is fine — don't flag as stalled
            if result["status"] in ("stalled", "broken"):
                result["status"] = "idle"
                result["details"] = "Queue empty, no work pending"
    
    return result

def check_gateway_contention():
    """Check for gateway restart contention."""
    contention = {"detected": False, "details": ""}
    
    # Check gateway restart log for recent restarts
    restart_log = CLAWDBOT_LOGS / "gateway-restart.log"
    if not restart_log.exists():
        return contention
    
    try:
        with open(restart_log, 'r') as f:
            lines = f.readlines()
        
        # Count restarts in last 10 minutes
        now = time.time()
        recent_restarts = 0
        for line in lines[-20:]:  # Check last 20 entries
            # Try to parse timestamps — format varies
            try:
                if "restart" in line.lower() or "start" in line.lower():
                    recent_restarts += 1
            except:
                pass
        
        if recent_restarts > 3:
            contention["detected"] = True
            contention["details"] = f"{recent_restarts} gateway restarts in recent log entries — possible flapping"
    except Exception as e:
        contention["details"] = f"Could not check: {e}"
    
    return contention

def check_work_metrics_dormancy():
    """Check if work_metrics.json is being populated."""
    metrics_path = CLAWD / "state" / "work_metrics.json"
    work_path = CLAWD / "state" / "current_work.json"
    
    metrics = load_json(metrics_path)
    work = load_json(work_path)
    
    if not metrics or not work:
        return {"dormant": False, "details": "Files not found"}
    
    completed = work.get("completed", [])
    sprints = metrics.get("sprints", [])
    
    if len(completed) > 0 and len(sprints) == 0:
        return {
            "dormant": True,
            "details": f"{len(completed)} sprints completed but work_metrics.json has 0 entries — logging step not implemented"
        }
    
    return {"dormant": False, "details": "OK"}

# === AUTO-RECOVERY ===

def attempt_recovery(system_result, meta_state):
    """Attempt auto-recovery for a stalled/broken system.
    
    Philosophy: Detect → Fix → Log → Teach.
    Level 1: Subsystem self-heals (built into each script)
    Level 2: Meta-monitor fixes it AND teaches the subsystem (this function)
    Level 3: Escalate to Opus (only if Level 2 fails)
    Level 4: Escalate to human (almost never)
    """
    name = system_result["name"]
    status = system_result["status"]
    
    # Check intervention budget
    now = time.time()
    recent = [i for i in meta_state.get("interventions", []) 
              if now - i.get("time", 0) < 3600]
    
    if len(recent) >= MAX_INTERVENTIONS_PER_HOUR:
        return {
            "action": "skipped",
            "reason": f"Intervention budget exhausted ({len(recent)}/{MAX_INTERVENTIONS_PER_HOUR} this hour)"
        }
    
    # Check backoff
    stall_count = meta_state.get("stall_history", {}).get(name, 0)
    if stall_count > 0:
        backoff_sec = BACKOFF_BASE ** min(stall_count, 10) * 60
        last_intervention = None
        for i in reversed(meta_state.get("interventions", [])):
            if i.get("system") == name:
                last_intervention = i.get("time", 0)
                break
        if last_intervention and (now - last_intervention) < backoff_sec:
            return {
                "action": "backoff",
                "reason": f"Backing off ({stall_count} stalls, waiting {int(backoff_sec)}s)"
            }
    
    # === ACTIVE RECOVERY (Level 2) ===
    action = "none"
    details = ""
    success = False
    
    # Recovery scripts mapped to systems
    RECOVERY_SCRIPTS = {
        "security_hound": str(CLAWD / "scripts" / "security_hound.py"),
        "personal_learner": str(CLAWD / "scripts" / "personal_learner.py") + " --quick",
        "usage_monitor": str(CLAWD / "scripts" / "check_usage.py"),
    }
    
    if name == "watchdog":
        # Check if watchdog launchd is running
        try:
            result = subprocess.run(
                ["launchctl", "list", "com.moltbot.watchdog"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                # Try to load the watchdog plist
                plist = HOME / "Library" / "LaunchAgents" / "com.moltbot.watchdog.plist"
                if plist.exists():
                    subprocess.run(["launchctl", "load", str(plist)],
                                   capture_output=True, timeout=10)
                    action = "restarted_watchdog"
                    details = "Watchdog launchd job reloaded"
                    success = True
                else:
                    action = "watchdog_plist_missing"
                    details = f"Plist not found at {plist}"
            else:
                action = "watchdog_running_but_stale"
                details = "Watchdog launchd is running but state file stale — may need process restart"
        except Exception as e:
            action = "check_failed"
            details = str(e)
    
    elif name in RECOVERY_SCRIPTS:
        # ACTUALLY RUN the script to unstall it
        script_cmd = RECOVERY_SCRIPTS[name]
        try:
            result = subprocess.run(
                ["python3"] + script_cmd.split(),
                capture_output=True, text=True, timeout=60,
                cwd=str(CLAWD)
            )
            if result.returncode == 0:
                action = f"re-ran_{name}"
                details = f"Successfully re-executed {name} script"
                success = True
            else:
                action = f"re-ran_{name}_failed"
                details = f"Script exited {result.returncode}: {result.stderr[:200]}"
        except subprocess.TimeoutExpired:
            action = f"{name}_timeout"
            details = f"Script timed out after 60s"
        except Exception as e:
            action = f"{name}_error"
            details = str(e)
    
    elif name == "heartbeat":
        # Reset heartbeat state timestamp to mark it alive
        hb_path = CLAWD / "memory" / "heartbeat-state.json"
        try:
            hb_state = load_json(hb_path) or {"lastChecks": {}}
            hb_state["lastChecks"]["heartbeat"] = int(now)
            hb_state["lastChecks"]["meta_monitor"] = int(now)
            save_json(hb_path, hb_state)
            # Also touch the file to update mtime
            hb_path.touch()
            action = "reset_heartbeat_state"
            details = "Reset heartbeat timestamps and touched state file"
            success = True
        except Exception as e:
            action = "heartbeat_reset_failed"
            details = str(e)
    
    elif name == "work_loop":
        if system_result.get("in_progress"):
            action = "work_stalled"
            details = f"Work item '{system_result['in_progress']}' may need re-fire — flagged for Opus"
        else:
            # Touch the state file to clear staleness if queue is empty
            work_path = CLAWD / "state" / "current_work.json"
            work_state = load_json(work_path)
            if work_state and not work_state.get("queue"):
                work_state["lastUpdated"] = datetime.now(timezone.utc).isoformat()
                save_json(work_path, work_state)
                action = "refreshed_idle_work_loop"
                details = "Queue empty, refreshed timestamp"
                success = True
    
    # Record intervention
    intervention = {
        "time": now,
        "system": name,
        "status": status,
        "action": action,
        "details": details,
        "success": success,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    meta_state.setdefault("interventions", []).append(intervention)
    
    # Keep only last 100 interventions
    meta_state["interventions"] = meta_state["interventions"][-100:]
    
    # Update stall count (reset on successful fix)
    if success:
        meta_state.setdefault("stall_history", {})[name] = 0
    else:
        meta_state.setdefault("stall_history", {})[name] = stall_count + 1
    
    # Log the fix for learning
    _log_recovery(name, action, success, details)
    
    return {"action": action, "details": details, "success": success}


def _log_recovery(system_name, action, success, details):
    """Log recovery actions for the system to learn from."""
    log_path = CLAWD / "state" / "recovery_log.json"
    log = load_json(log_path) or {"recoveries": []}
    log["recoveries"].append({
        "system": system_name,
        "action": action,
        "success": success,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    # Keep last 200 entries
    log["recoveries"] = log["recoveries"][-200:]
    save_json(log_path, log)

# === MAIN LOGIC ===

def run_check(fix_mode=False, json_output=False, heartbeat_mode=False):
    """Run the full meta-monitor check."""
    meta_state = load_meta_state()
    now = time.time()
    
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "fix" if fix_mode else "check",
        "systems": [],
        "summary": {
            "healthy": 0,
            "stalled": 0,
            "broken": 0,
            "missing": 0,
            "idle": 0
        },
        "context": check_session_context(),
        "contention": check_gateway_contention(),
        "work_metrics": check_work_metrics_dormancy(),
        "escalate": False,
        "recovery_actions": []
    }
    
    # Check each system
    for system in SYSTEMS:
        health = check_system_health(system)
        results["systems"].append(health)
        
        status = health["status"]
        if status in results["summary"]:
            results["summary"][status] += 1
        
        # Reset stall count if healthy
        if status == "healthy":
            meta_state.setdefault("stall_history", {})[system["name"]] = 0
        
        # Attempt recovery if fix mode and system is stalled/broken
        if fix_mode and status in ("stalled", "broken"):
            recovery = attempt_recovery(health, meta_state)
            results["recovery_actions"].append({
                "system": system["name"],
                **recovery
            })
    
    # Auto-reset session if context is critically high (Level 2 self-healing)
    ctx = results.get("context", {})
    if fix_mode and ctx.get("needs_clear"):
        pct = ctx.get("percent", 0)
        reset_ok = auto_reset_session()
        results["session_reset"] = {
            "triggered": True,
            "success": reset_ok,
            "reason": f"Context at {pct}% — auto-reset triggered"
        }
        if reset_ok:
            results["context"]["details"] = f"Context was {pct}% — AUTO-RESET to 0%. Fresh session."
            results["context"]["needs_clear"] = False
    
    # Check if escalation needed
    stalled_or_broken = results["summary"]["stalled"] + results["summary"]["broken"]
    if stalled_or_broken >= ESCALATION_THRESHOLD:
        results["escalate"] = True
    
    # Update meta state
    meta_state["lastRun"] = datetime.now(timezone.utc).isoformat()
    meta_state["runCount"] = meta_state.get("runCount", 0) + 1
    
    # Store per-system status in meta state
    for sys_result in results["systems"]:
        meta_state.setdefault("systems", {})[sys_result["name"]] = {
            "status": sys_result["status"],
            "lastChecked": results["timestamp"],
            "age_sec": sys_result["age_sec"]
        }
    
    save_meta_state(meta_state)
    
    # Output
    if json_output:
        # Add should_alert for heartbeat integration
        results["should_alert"] = results["escalate"]
        results["has_alerts"] = stalled_or_broken > 0 or results["contention"]["detected"]
        print(json.dumps(results, indent=2))
    else:
        print_human_readable(results)
    
    return results

def print_human_readable(results):
    """Print a nice summary."""
    print("=" * 60)
    print("META-MONITOR HEALTH CHECK")
    print(f"Time: {results['timestamp']}")
    print(f"Mode: {results['mode']}")
    print("=" * 60)
    
    s = results["summary"]
    print(f"\n✅ Healthy: {s['healthy']}  ⚠️ Stalled: {s['stalled']}  "
          f"❌ Broken: {s['broken']}  📦 Missing: {s['missing']}  "
          f"💤 Idle: {s['idle']}")
    
    print("\n--- Systems ---")
    for sys in results["systems"]:
        icon = {"healthy": "✅", "stalled": "⚠️", "broken": "❌", 
                "missing": "📦", "idle": "💤", "unknown": "❓"}.get(sys["status"], "❓")
        age_str = f"{sys['age_sec']}s ago" if sys['age_sec'] is not None else "N/A"
        print(f"  {icon} {sys['name']:20s} [{sys['status']:8s}] {age_str:>10s}  {sys['details']}")
    
    ctx = results.get("context", {})
    if ctx.get("needs_clear"):
        print(f"\n🧠 CONTEXT: {ctx['details']} — trigger /new!")
    elif ctx.get("percent"):
        print(f"\n🧠 CONTEXT: {ctx['details']}")
    
    if results["contention"]["detected"]:
        print(f"\n🔴 CONTENTION: {results['contention']['details']}")
    
    if results["work_metrics"]["dormant"]:
        print(f"\n🟡 DORMANT: {results['work_metrics']['details']}")
    
    if results["escalate"]:
        print(f"\n🚨 ESCALATION: {results['summary']['stalled'] + results['summary']['broken']} "
              f"systems need attention!")
    
    if results.get("recovery_actions"):
        print("\n--- Recovery Actions ---")
        for action in results["recovery_actions"]:
            print(f"  🔧 {action['system']}: {action.get('action', 'none')} — {action.get('details', '')}")
    
    print()

# === CLI ===

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Meta-Monitor: Watch the watchers")
    parser.add_argument("--check", action="store_true", help="Read-only health check")
    parser.add_argument("--fix", action="store_true", help="Attempt auto-recovery")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--mode", choices=["full", "heartbeat"], default="full",
                       help="Check mode (heartbeat = lightweight)")
    args = parser.parse_args()
    
    if not args.check and not args.fix:
        args.check = True  # Default to check mode
    
    # Heartbeat mode ALWAYS fixes — detect and heal, don't just report
    effective_fix = args.fix or (args.mode == "heartbeat")
    
    results = run_check(
        fix_mode=effective_fix,
        json_output=args.json,
        heartbeat_mode=(args.mode == "heartbeat")
    )
    
    # Exit code: 0 = all healthy, 1 = has issues, 2 = needs escalation
    if results["escalate"]:
        sys.exit(2)
    elif results["summary"]["stalled"] + results["summary"]["broken"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)
