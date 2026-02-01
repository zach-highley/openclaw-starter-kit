#!/usr/bin/env python3
"""autonomous_work_loop.py — Self-propelling sprint chain.

The Problem:
    Crons fire individual events but nothing CHAINS tasks. When one sprint
    finishes, nobody starts the next. At best 1-2 sprints per session
    instead of continuous throughput.

The Solution:
    This script reads the sprint queue from current_work.json, checks if
    anything is actively running, and outputs whether the next task should fire.

    Designed to be called by a cron job (every 30 min) that spawns subagents:
    1. Cron fires → runs this script
    2. If should_fire=true → cron session spawns a subagent for the next task
    3. subagent_watcher.py detects completion → marks sprint done
    4. Next cron cycle → this script sees queue has items, no active sprint → fires again
    5. Repeat forever

Usage:
    python3 autonomous_work_loop.py --json          # Check queue status
    python3 autonomous_work_loop.py --next           # Get next task details
    python3 autonomous_work_loop.py --complete NAME  # Mark a sprint complete
    python3 autonomous_work_loop.py --add "task"     # Add to queue

State:
    Reads/writes: state/current_work.json
    Writes: state/work_metrics.json (sprint metrics)

Optional env:
    OPENCLAW_WORKSPACE: override workspace detection

Requires: Python 3.9+
No external dependencies.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def detect_workspace() -> Path:
    env = os.environ.get("OPENCLAW_WORKSPACE")
    if env:
        return Path(env).expanduser().resolve()
    for candidate in [Path.home() / ".openclaw" / "workspace"]:
        if candidate.is_dir():
            return candidate
    return Path.cwd()


WORKSPACE = detect_workspace()
WORK_FILE = WORKSPACE / "state" / "current_work.json"
METRICS_FILE = WORKSPACE / "state" / "work_metrics.json"


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_queue(work: Dict[str, Any]) -> List[str]:
    return work.get("sprint_queue", [])


def get_completed(work: Dict[str, Any]) -> List[str]:
    return work.get("completed_today", [])


def should_fire_next(work: Dict[str, Any]) -> Dict[str, Any]:
    """Determine if we should fire the next sprint."""
    queue = get_queue(work)
    active = work.get("active_subagent")
    active_sprint = work.get("active_sprint", "")

    if active and active != "null" and active is not None:
        return {
            "should_fire": False,
            "reason": f"Active subagent running: {active}",
            "active_sprint": active_sprint,
            "queue_length": len(queue),
        }

    if not queue:
        return {
            "should_fire": False,
            "reason": "Sprint queue is empty",
            "queue_length": 0,
        }

    next_task = queue[0]
    return {
        "should_fire": True,
        "reason": "Queue has items and no active sprint",
        "next_task": next_task,
        "queue_length": len(queue),
    }


def mark_complete(work: Dict[str, Any], name: str) -> Dict[str, Any]:
    """Mark a sprint as complete and shift queue."""
    completed = get_completed(work)
    if name not in completed:
        completed.append(name)
    work["completed_today"] = completed

    queue = get_queue(work)
    work["sprint_queue"] = [q for q in queue if name.lower() not in q.lower()]

    work["active_sprint"] = None
    work["active_subagent"] = None
    work["active_subagent_session"] = None
    return work


def add_to_queue(work: Dict[str, Any], task: str) -> Dict[str, Any]:
    """Add a task to the sprint queue."""
    queue = get_queue(work)
    queue.append(task)
    work["sprint_queue"] = queue
    return work


def log_metric(sprint_name: str, duration_s: int = 0, success: bool = True) -> None:
    """Log sprint completion to work_metrics.json."""
    metrics = load_json(METRICS_FILE)
    if "sprints" not in metrics:
        metrics["sprints"] = []

    metrics["sprints"].append({
        "name": sprint_name,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": duration_s,
        "success": success,
    })

    metrics["sprints"] = metrics["sprints"][-200:]
    metrics["last_updated"] = datetime.now(timezone.utc).isoformat()
    metrics["total_completed"] = len([s for s in metrics["sprints"] if s["success"]])
    save_json(METRICS_FILE, metrics)


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous work loop controller")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--next", action="store_true", help="Get next task to fire")
    parser.add_argument("--complete", type=str, help="Mark a sprint as complete")
    parser.add_argument("--add", type=str, help="Add a task to the queue")
    parser.add_argument("--status", action="store_true", help="Show queue status")
    args = parser.parse_args()

    work = load_json(WORK_FILE)

    if args.complete:
        work = mark_complete(work, args.complete)
        log_metric(args.complete, success=True)
        save_json(WORK_FILE, work)
        if args.json_output:
            print(json.dumps({"completed": args.complete, "queue_remaining": len(get_queue(work))}))
        else:
            print(f"Marked '{args.complete}' as complete. {len(get_queue(work))} items remaining.")
        sys.exit(0)

    if args.add:
        work = add_to_queue(work, args.add)
        save_json(WORK_FILE, work)
        if args.json_output:
            print(json.dumps({"added": args.add, "queue_length": len(get_queue(work))}))
        else:
            print(f"Added '{args.add}' to queue. {len(get_queue(work))} items total.")
        sys.exit(0)

    result = should_fire_next(work)

    if args.json_output or args.next:
        print(json.dumps(result, indent=2))
    else:
        if result["should_fire"]:
            print(f"Ready to fire: {result['next_task']}")
            print(f"   Queue: {result['queue_length']} items")
        else:
            print(f"Paused: {result['reason']}")
            print(f"   Queue: {result.get('queue_length', 0)} items")

    sys.exit(0 if not result["should_fire"] else 1)


if __name__ == "__main__":
    main()
