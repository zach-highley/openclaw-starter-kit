#!/usr/bin/env python3
"""
Sprint Metric Logger
Tracks performance of autonomous work sprints: which agent, how long, success/fail.
Over time, this builds a dataset that helps you route tasks to the best model.

Usage:
  python3 log_sprint_metric.py --sprint S1 --agent codex --status success --duration 5.0 --notes "Search bar"
  python3 log_sprint_metric.py --summary

State file: state/work_metrics.json
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

METRICS_FILE = Path.home() / "clawd" / "state" / "work_metrics.json"


def load_metrics():
    if METRICS_FILE.exists():
        return json.loads(METRICS_FILE.read_text())
    return {"version": 1, "created": datetime.now(timezone.utc).isoformat(), "sprints": [], "summary": {}}


def save_metrics(data):
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    METRICS_FILE.write_text(json.dumps(data, indent=2, default=str))


def log_sprint(sprint, agent, status, duration, error=None, notes=None):
    data = load_metrics()
    entry = {
        "sprint": sprint,
        "agent": agent,
        "status": status,
        "durationMinutes": duration,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "errorType": error,
        "notes": notes,
    }
    data["sprints"].append(entry)
    data["summary"] = compute_summary(data["sprints"])
    save_metrics(data)
    print(f"✅ Logged: {sprint} | {agent} | {status} | {duration}min")


def compute_summary(sprints):
    completed = [s for s in sprints if s["status"] == "success"]
    failed = [s for s in sprints if s["status"] == "failed"]
    agents = {}
    for s in sprints:
        a = s["agent"]
        if a not in agents:
            agents[a] = {"completed": 0, "failed": 0, "durations": []}
        if s["status"] == "success":
            agents[a]["completed"] += 1
            agents[a]["durations"].append(s["durationMinutes"])
        elif s["status"] == "failed":
            agents[a]["failed"] += 1

    perf = {}
    for a, d in agents.items():
        total = d["completed"] + d["failed"]
        perf[a] = {
            "completed": d["completed"],
            "failed": d["failed"],
            "successRate": round(d["completed"] / total * 100, 1) if total else 0,
            "avgDurationMinutes": round(sum(d["durations"]) / len(d["durations"]), 1) if d["durations"] else 0,
        }

    return {
        "totalCompleted": len(completed),
        "totalFailed": len(failed),
        "avgDurationMinutes": round(sum(s["durationMinutes"] for s in completed) / len(completed), 1) if completed else 0,
        "agentPerformance": perf,
    }


def show_summary():
    data = load_metrics()
    s = data.get("summary", {})
    print("=== Sprint Metrics Summary ===")
    print(f"Total completed: {s.get('totalCompleted', 0)}")
    print(f"Total failed: {s.get('totalFailed', 0)}")
    print(f"Avg duration: {s.get('avgDurationMinutes', 0)} min")
    for agent, perf in s.get("agentPerformance", {}).items():
        print(f"\n  {agent}:")
        print(f"    Completed: {perf['completed']}, Failed: {perf['failed']}")
        print(f"    Success rate: {perf['successRate']}%")
        print(f"    Avg duration: {perf['avgDurationMinutes']} min")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log sprint metrics")
    parser.add_argument("--sprint", help="Sprint name (e.g., S1)")
    parser.add_argument("--agent", help="Agent used (codex, opus, gemini, etc.)")
    parser.add_argument("--status", choices=["success", "failed", "stalled"])
    parser.add_argument("--duration", type=float, help="Duration in minutes")
    parser.add_argument("--error", help="Error type if failed")
    parser.add_argument("--notes", help="Notes about the sprint")
    parser.add_argument("--summary", action="store_true", help="Show summary")

    args = parser.parse_args()
    if args.summary:
        show_summary()
    elif args.sprint and args.agent and args.status:
        log_sprint(args.sprint, args.agent, args.status, args.duration or 0, args.error, args.notes)
    else:
        parser.print_help()
