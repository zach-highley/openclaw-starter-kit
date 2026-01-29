#!/usr/bin/env python3
"""
Auto-update script for brew packages.
Returns JSON with what was updated.
"""

import json
import subprocess
from datetime import datetime

def run_cmd(cmd, timeout=300):
    """Run command and return stdout, stderr, returncode."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout", -1
    except Exception as e:
        return "", str(e), -1

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated")
    args = parser.parse_args()
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": args.dry_run,
        "steps": [],
        "success": True,
        "errors": []
    }
    
    # Step 1: Update brew itself
    results["steps"].append({"name": "brew update", "status": "running"})
    stdout, stderr, code = run_cmd("brew update")
    results["steps"][-1]["status"] = "ok" if code == 0 else "error"
    if code != 0:
        results["errors"].append(f"brew update failed: {stderr}")
        results["success"] = False
    
    # Step 2: Get outdated
    stdout, stderr, code = run_cmd("brew outdated --json")
    outdated = {"formulae": [], "casks": []}
    if stdout:
        try:
            data = json.loads(stdout)
            outdated["formulae"] = [f.get("name", str(f)) if isinstance(f, dict) else str(f) for f in data.get("formulae", [])]
            outdated["casks"] = [c.get("name", str(c)) if isinstance(c, dict) else str(c) for c in data.get("casks", [])]
        except:
            pass
    
    results["outdated_count"] = len(outdated["formulae"]) + len(outdated["casks"])
    results["outdated"] = outdated
    
    if args.dry_run:
        results["steps"].append({"name": "upgrade (dry-run)", "status": "skipped"})
        print(json.dumps(results, indent=2))
        return
    
    # Step 3: Upgrade formulae
    if outdated["formulae"]:
        results["steps"].append({"name": "brew upgrade (formulae)", "status": "running"})
        stdout, stderr, code = run_cmd("brew upgrade", timeout=600)
        results["steps"][-1]["status"] = "ok" if code == 0 else "error"
        results["steps"][-1]["output"] = stdout[:500] if stdout else ""
        if code != 0:
            results["errors"].append(f"brew upgrade failed: {stderr[:200]}")
    
    # Step 4: Upgrade casks
    if outdated["casks"]:
        results["steps"].append({"name": "brew upgrade --cask", "status": "running"})
        stdout, stderr, code = run_cmd("brew upgrade --cask", timeout=600)
        results["steps"][-1]["status"] = "ok" if code == 0 else "error"
        if code != 0:
            results["errors"].append(f"brew cask upgrade failed: {stderr[:200]}")
    
    # Step 5: Cleanup
    results["steps"].append({"name": "brew cleanup", "status": "running"})
    stdout, stderr, code = run_cmd("brew cleanup")
    results["steps"][-1]["status"] = "ok" if code == 0 else "error"
    
    results["success"] = len(results["errors"]) == 0
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
