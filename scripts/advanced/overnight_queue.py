#!/usr/bin/env python3
"""overnight_queue.py — OC-014 Overnight Build Pipeline queue runner.

Reads tasks from state/overnight_queue.json and executes them until the stop
window (default 05:00 America/New_York) or token budget is exhausted.

Task types:
  - codex: run an OpenClaw agent turn (expects the agent to use Codex for coding)
  - opus:  run an OpenClaw agent turn (planning/research)
  - local: run a local command (array) or python script

Progress is appended to state/overnight_progress.jsonl.

Usage:
  python3 scripts/overnight_queue.py
  python3 scripts/overnight_queue.py --dry-run

Notes:
- Safety: this runner refuses tasks that look like production deploys unless
  explicitly allowed per-task.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore

CLAWD = Path.home() / ".openclaw" / "workspace"
STATE_DIR = CLAWD / "state"
QUEUE_PATH = STATE_DIR / "overnight_queue.json"
PROGRESS_PATH = STATE_DIR / "overnight_progress.jsonl"
RUN_STATE_PATH = STATE_DIR / "overnight_run.json"

DEFAULT_CONFIG = {
    "start_hour": 22,
    "stop_hour": 5,
    "max_parallel": 3,
    "timezone": "America/New_York",
    "max_tokens": 120_000,
    "agent_id": "main",
}


def now_tz(tz_name: str) -> datetime:
    if ZoneInfo is None:
        return datetime.now()
    try:
        return datetime.now(ZoneInfo(tz_name))
    except Exception:
        return datetime.now()


def append_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def get_usage_total_tokens() -> int:
    """Return total tokens from scripts/check_usage.py --json.

    This is best-effort and returns 0 if unavailable.
    """

    script = CLAWD / "scripts" / "check_usage.py"
    if not script.exists():
        return 0
    try:
        r = subprocess.run(
            [sys.executable, str(script), "--json"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if r.returncode != 0:
            return 0
        data = json.loads(r.stdout)
        return int(((data.get("session") or {}).get("total_tokens")) or 0)
    except Exception:
        return 0


def looks_like_production_deploy(cmd_str: str) -> bool:
    needles = [
        "deploy",
        "production",
        "prod",
        "terraform apply",
        "kubectl apply",
        "helm upgrade",
        "vercel --prod",
        "fly deploy",
        "railway up",
    ]
    s = cmd_str.lower()
    return any(n in s for n in needles)


def score_task(task: Dict[str, Any]) -> Tuple[float, int]:
    """Higher score sorts first.

    Supports optional value/effort fields. Otherwise uses priority.
    """

    prio = int(task.get("priority", 9999) or 9999)
    value = task.get("value")
    effort = task.get("effort")

    if isinstance(value, (int, float)) and isinstance(effort, (int, float)) and effort > 0:
        return (float(value) / float(effort), -prio)

    # Fallback: treat lower priority number as more important.
    return (1.0 / max(prio, 1), -prio)


@dataclass
class TaskResult:
    task_id: str
    name: str
    ok: bool
    stdout: str = ""
    stderr: str = ""
    duration_s: float = 0.0
    commit_hashes: List[str] = None


async def run_local_task(task: Dict[str, Any], dry_run: bool) -> TaskResult:
    task_id = str(task.get("id") or "")
    name = str(task.get("name") or task_id)

    cmd = task.get("command")
    if isinstance(cmd, str):
        cmd_list = shlex.split(cmd)
        cmd_str = cmd
    elif isinstance(cmd, list) and all(isinstance(x, str) for x in cmd):
        cmd_list = cmd
        cmd_str = " ".join(shlex.quote(x) for x in cmd)
    else:
        return TaskResult(task_id=task_id, name=name, ok=False, stderr="local task missing command")

    allow_deploy = bool(task.get("allow_deploy"))
    if looks_like_production_deploy(cmd_str) and not allow_deploy:
        return TaskResult(task_id=task_id, name=name, ok=False, stderr=f"refused potential production deploy command: {cmd_str}")

    start = time.time()
    if dry_run:
        return TaskResult(task_id=task_id, name=name, ok=True, stdout=f"DRY RUN: would run {cmd_str}", duration_s=time.time() - start)

    proc = await asyncio.create_subprocess_exec(
        *cmd_list,
        cwd=str(CLAWD),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out_b, err_b = await proc.communicate()
    out = out_b.decode("utf-8", errors="replace") if out_b else ""
    err = err_b.decode("utf-8", errors="replace") if err_b else ""
    ok = proc.returncode == 0
    return TaskResult(task_id=task_id, name=name, ok=ok, stdout=out.strip(), stderr=err.strip(), duration_s=time.time() - start)


def build_openclaw_message(task: Dict[str, Any]) -> str:
    lines = []
    lines.append("You are running as part of the OC-014 overnight pipeline.")
    lines.append("SAFETY: Do NOT deploy to production. Do NOT run destructive commands. Prefer small scoped changes.")
    lines.append("When finished: summarize what changed, what to review, and list any commits made.")
    lines.append("")
    lines.append(f"Task: {task.get('name','(unnamed)')} ({task.get('id','')})")

    spec_path = task.get("spec")
    if spec_path:
        lines.append(f"Spec path: {spec_path}")
        try:
            p = (CLAWD / spec_path).expanduser() if not str(spec_path).startswith("/") else Path(spec_path)
            if p.exists() and p.is_file():
                content = p.read_text(encoding="utf-8")
                lines.append("\n--- SPEC ---\n" + content + "\n--- END SPEC ---\n")
        except Exception:
            pass

    extra = task.get("prompt")
    if extra:
        lines.append("\nAdditional instructions:\n" + str(extra))

    return "\n".join(lines)


async def run_agent_task(task: Dict[str, Any], dry_run: bool, agent_id: str, session_id: str) -> TaskResult:
    task_id = str(task.get("id") or "")
    name = str(task.get("name") or task_id)
    msg = build_openclaw_message(task)

    cmd = [
        "openclaw",
        "agent",
        "--agent",
        agent_id,
        "--session-id",
        session_id,
        "--message",
        msg,
        "--json",
    ]

    start = time.time()
    if dry_run:
        return TaskResult(task_id=task_id, name=name, ok=True, stdout=f"DRY RUN: would run {' '.join(shlex.quote(x) for x in cmd[:8])} ...", duration_s=time.time() - start)

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(CLAWD),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out_b, err_b = await proc.communicate()
    out = out_b.decode("utf-8", errors="replace") if out_b else ""
    err = err_b.decode("utf-8", errors="replace") if err_b else ""
    ok = proc.returncode == 0

    # Best-effort parse to surface agent reply.
    try:
        data = json.loads(out) if out.strip() else {}
        reply = data.get("reply") or data.get("output") or data.get("text")
        if reply:
            out = str(reply)
    except Exception:
        pass

    return TaskResult(task_id=task_id, name=name, ok=ok, stdout=out.strip(), stderr=err.strip(), duration_s=time.time() - start)


def git_commits_since(base_rev: str) -> List[str]:
    try:
        r = subprocess.run(
            ["git", "log", "--pretty=%H %s", f"{base_rev}..HEAD"],
            cwd=str(CLAWD),
            capture_output=True,
            text=True,
            timeout=20,
        )
        if r.returncode != 0:
            return []
        lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
        return lines
    except Exception:
        return []


def current_git_head() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(CLAWD), capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return ""


def within_run_window(cfg: Dict[str, Any]) -> bool:
    tz = str(cfg.get("timezone") or DEFAULT_CONFIG["timezone"])
    start_h = int(cfg.get("start_hour", DEFAULT_CONFIG["start_hour"]))
    stop_h = int(cfg.get("stop_hour", DEFAULT_CONFIG["stop_hour"]))

    n = now_tz(tz)
    hour = n.hour

    # Window can span midnight: e.g. 22 -> 5
    if start_h <= stop_h:
        return start_h <= hour < stop_h
    return hour >= start_h or hour < stop_h


def should_stop_now(cfg: Dict[str, Any]) -> bool:
    tz = str(cfg.get("timezone") or DEFAULT_CONFIG["timezone"])
    stop_h = int(cfg.get("stop_hour", DEFAULT_CONFIG["stop_hour"]))
    n = now_tz(tz)
    return n.hour >= stop_h and not within_run_window(cfg)


async def run_queue(dry_run: bool) -> int:
    q = load_json(QUEUE_PATH)
    tasks = q.get("tasks") if isinstance(q.get("tasks"), list) else []
    cfg = DEFAULT_CONFIG.copy()
    cfg.update(q.get("config") if isinstance(q.get("config"), dict) else {})

    if not tasks:
        print(f"No tasks found in {QUEUE_PATH}.")
        return 0

    if not within_run_window(cfg) and not dry_run:
        print("Outside configured run window; exiting.")
        return 0

    agent_id = str(cfg.get("agent_id") or DEFAULT_CONFIG["agent_id"])
    session_id = f"overnight-{now_tz(str(cfg.get('timezone'))).strftime('%Y%m%d')}"

    base_rev = current_git_head()
    start_tokens = get_usage_total_tokens()

    run_state = {
        "started_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "timezone": cfg.get("timezone"),
        "session_id": session_id,
        "base_rev": base_rev,
        "start_total_tokens": start_tokens,
        "dry_run": bool(dry_run),
    }
    RUN_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    RUN_STATE_PATH.write_text(json.dumps(run_state, indent=2), encoding="utf-8")

    append_jsonl(PROGRESS_PATH, {"event": "run_start", **run_state})

    # Sort by score (desc)
    tasks_sorted = sorted(tasks, key=score_task, reverse=True)

    max_parallel = int(cfg.get("max_parallel", 1) or 1)
    max_tokens = int(cfg.get("max_tokens", DEFAULT_CONFIG["max_tokens"]) or DEFAULT_CONFIG["max_tokens"])

    completed: List[TaskResult] = []
    errors: List[TaskResult] = []

    sem = asyncio.Semaphore(max_parallel)

    async def run_one(task: Dict[str, Any]) -> TaskResult:
        async with sem:
            t0 = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            append_jsonl(PROGRESS_PATH, {"event": "task_start", "ts": t0, "task": task})

            ttype = str(task.get("type") or "codex").lower()
            timeout_minutes = int(task.get("timeout_minutes", 30) or 30)
            try:
                if ttype == "local":
                    coro = run_local_task(task, dry_run)
                else:
                    coro = run_agent_task(task, dry_run, agent_id=agent_id, session_id=session_id)

                res: TaskResult = await asyncio.wait_for(coro, timeout=timeout_minutes * 60)
            except asyncio.TimeoutError:
                res = TaskResult(task_id=str(task.get("id")), name=str(task.get("name")), ok=False, stderr=f"timeout after {timeout_minutes}m")
            except Exception as e:
                res = TaskResult(task_id=str(task.get("id")), name=str(task.get("name")), ok=False, stderr=str(e))

            t1 = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            payload = {
                "event": "task_end",
                "ts": t1,
                "task_id": res.task_id,
                "name": res.name,
                "ok": res.ok,
                "duration_s": round(res.duration_s, 2),
                "stdout": res.stdout[:8000],
                "stderr": res.stderr[:8000],
            }
            append_jsonl(PROGRESS_PATH, payload)
            return res

    pending: List[asyncio.Task] = []

    for task in tasks_sorted:
        if should_stop_now(cfg) and not dry_run:
            append_jsonl(PROGRESS_PATH, {"event": "stop_window_reached", "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")})
            break

        # Token budget check (best-effort)
        if not dry_run:
            cur_tokens = get_usage_total_tokens()
            if cur_tokens and start_tokens and (cur_tokens - start_tokens) >= max_tokens:
                append_jsonl(PROGRESS_PATH, {
                    "event": "token_budget_reached",
                    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "start_total_tokens": start_tokens,
                    "current_total_tokens": cur_tokens,
                    "budget": max_tokens,
                })
                break

        pending.append(asyncio.create_task(run_one(task)))

        # Keep the pending list bounded so we can stop in-between.
        if len(pending) >= max_parallel:
            done, still = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            pending = list(still)
            for d in done:
                res = d.result()
                (completed if res.ok else errors).append(res)

    # drain
    if pending:
        done, _ = await asyncio.wait(pending)
        for d in done:
            res = d.result()
            (completed if res.ok else errors).append(res)

    end_tokens = get_usage_total_tokens()
    commits = git_commits_since(base_rev)

    run_end = {
        "event": "run_end",
        "ended_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "completed": [{"id": r.task_id, "name": r.name} for r in completed],
        "errors": [{"id": r.task_id, "name": r.name, "stderr": r.stderr} for r in errors],
        "commits": commits,
        "start_total_tokens": start_tokens,
        "end_total_tokens": end_tokens,
        "delta_tokens": (end_tokens - start_tokens) if end_tokens and start_tokens else None,
        "dry_run": bool(dry_run),
    }
    append_jsonl(PROGRESS_PATH, run_end)

    # Update run state file for morning_summary.py
    run_state.update({
        "ended_at": run_end["ended_at"],
        "completed": run_end["completed"],
        "errors": run_end["errors"],
        "commits": commits,
        "end_total_tokens": end_tokens,
        "delta_tokens": run_end["delta_tokens"],
    })
    RUN_STATE_PATH.write_text(json.dumps(run_state, indent=2), encoding="utf-8")

    print(f"Completed: {len(completed)} | Errors: {len(errors)} | Commits: {len(commits)}")
    if errors:
        print("Errors:")
        for e in errors[:5]:
            print(f"- {e.name}: {e.stderr}")

    return 0 if not errors else 2


def main() -> None:
    ap = argparse.ArgumentParser(description="OC-014 overnight queue runner")
    ap.add_argument("--dry-run", action="store_true", help="Do not execute tasks; just log what would happen")
    args = ap.parse_args()

    try:
        rc = asyncio.run(run_queue(dry_run=args.dry_run))
    except KeyboardInterrupt:
        append_jsonl(PROGRESS_PATH, {"event": "run_interrupt", "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")})
        rc = 130
    raise SystemExit(rc)


if __name__ == "__main__":
    main()
