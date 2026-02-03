#!/usr/bin/env python3
"""overnight_builder.py — Queue-driven overnight Codex build runner.

Reads:   ~/openclaw-workspace/state/overnight_queue.json
Writes:  ~/openclaw-workspace/state/overnight_build_results.json
Reads:   ~/openclaw-workspace/state/codex_status.json
Sends:   Telegram summary via scripts/simple_telegram_notify.py

Key constraints (hard defaults):
- Check Codex availability before spawning.
- Max 3 concurrent tasks.
- 10-minute timeout per task.

This script is intended to be invoked by launchd/cron.

"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# Workspace root
# Default: ~/.openclaw/workspace
# Override: set OPENCLAW_WORKSPACE=/path/to/workspace
CLAWD = Path(os.environ.get("OPENCLAW_WORKSPACE", str(Path.home() / ".openclaw" / "workspace")))
STATE_DIR = CLAWD / "state"
SCRIPTS_DIR = CLAWD / "scripts"

QUEUE_PATH = STATE_DIR / "overnight_queue.json"
CODEX_STATUS_PATH = STATE_DIR / "codex_status.json"
RESULTS_PATH = STATE_DIR / "overnight_build_results.json"
LOCK_PATH = STATE_DIR / "overnight_builder.lock"

DEFAULT_AGENT_NAME = "codex"
DEFAULT_AGENT_MODEL = "openai-codex/gpt-5.2"
DEFAULT_MAX_CONCURRENCY = 3
DEFAULT_TIMEOUT_S = 600


_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _run(cmd: List[str], *, cwd: Optional[Path] = None, timeout_s: Optional[int] = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout_s,
    )


def _acquire_lock() -> Optional[int]:
    """Returns file descriptor if lock acquired, else None."""
    import fcntl

    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(LOCK_PATH), os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(fd)
        return None

    os.ftruncate(fd, 0)
    os.write(fd, f"pid={os.getpid()} started_at={_iso(_utc_now())}\n".encode("utf-8"))
    os.fsync(fd)
    return fd


def _release_lock(fd: int) -> None:
    import fcntl

    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def codex_available() -> bool:
    state = _load_json(CODEX_STATUS_PATH)
    if not state:
        return False

    if state.get("exhausted") is True:
        return False
    if state.get("available") is False:
        return False

    # If neither field exists, fail closed.
    if "available" not in state and "exhausted" not in state:
        return False

    return True


def ensure_codex_agent(*, agent_name: str, model: str, workspace: Path) -> None:
    """Ensure an OpenClaw isolated agent exists for Codex runs.

    We use an isolated agent so the session can be separated logically, while
    still pointing at the same workspace so file edits land in ~/openclaw-workspace.
    """
    p = _run(["openclaw", "agents", "list"], timeout_s=30)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or "openclaw agents list failed")

    if re.search(rf"^- {re.escape(agent_name)}\b", p.stdout, re.MULTILINE):
        return

    add_cmd = [
        "openclaw",
        "agents",
        "add",
        agent_name,
        "--workspace",
        str(workspace),
        "--model",
        model,
        "--non-interactive",
    ]
    p2 = _run(add_cmd, timeout_s=60)
    if p2.returncode != 0:
        raise RuntimeError(p2.stderr.strip() or p2.stdout.strip() or f"Failed to create agent '{agent_name}'")


def _git_head(repo: Path) -> str:
    p = _run(["git", "rev-parse", "HEAD"], cwd=repo, timeout_s=10)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or "git rev-parse HEAD failed")
    return p.stdout.strip()


def _git_commits_between(repo: Path, a: str, b: str) -> List[str]:
    if a == b:
        return []
    p = _run(["git", "log", "--oneline", f"{a}..{b}"], cwd=repo, timeout_s=20)
    if p.returncode != 0:
        return []
    return [line.strip() for line in p.stdout.splitlines() if line.strip()]


def _git_files_between(repo: Path, a: str, b: str) -> List[str]:
    if a == b:
        return []
    p = _run(["git", "diff", "--name-only", f"{a}..{b}"], cwd=repo, timeout_s=20)
    if p.returncode != 0:
        return []
    return [line.strip() for line in p.stdout.splitlines() if line.strip()]


def _git_uncommitted_files(repo: Path) -> List[str]:
    p = _run(["git", "status", "--porcelain"], cwd=repo, timeout_s=20)
    if p.returncode != 0:
        return []
    files: List[str] = []
    for line in p.stdout.splitlines():
        if not line.strip():
            continue
        # porcelain format: XY <path>
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            files.append(parts[1])
    return sorted(set(files))


def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    t = text.strip()
    t = _JSON_FENCE_RE.sub("", t).strip()

    if not (t.startswith("{") and t.endswith("}")):
        start = t.find("{")
        end = t.rfind("}")
        if start != -1 and end != -1 and end > start:
            t = t[start : end + 1]

    try:
        obj = json.loads(t)
        if isinstance(obj, dict):
            return obj
    except Exception:
        return None

    return None


def _build_prompt(item: Dict[str, Any]) -> str:
    item_id = item.get("id", "")
    item_type = item.get("type", "")
    spec = (item.get("spec") or "").strip()
    repo = (item.get("repo") or "workspace").strip()

    # We want the sub-agent to *do work* in the workspace and then report.
    # The orchestrator also computes commits/files independently.
    return (
        "You are Codex running an overnight build task in the user’s OpenClaw workspace.\n"
        "Work carefully, make changes directly in the repository, run quick sanity checks, and commit if appropriate.\n\n"
        "Return TWO parts in your final message:\n"
        "(1) A brief human summary (2-6 sentences).\n"
        "(2) A single JSON object (no code fences) with this schema:\n"
        "{\n"
        "  \"success\": true|false,\n"
        "  \"summary\": <string>,\n"
        "  \"files_changed\": [<string>...],\n"
        "  \"commits_made\": [<string>...],\n"
        "  \"notes\": <string>\n"
        "}\n\n"
        "Task metadata:\n"
        f"- id: {item_id}\n"
        f"- type: {item_type}\n"
        f"- repo_hint: {repo}\n\n"
        "Task spec:\n"
        f"{spec}\n"
    )


@dataclass
class TaskResult:
    task: Dict[str, Any]
    status: str  # success|fail
    started_at: str
    finished_at: str
    duration_seconds: float
    files_changed: List[str]
    commits_made: List[str]
    agent: str
    session_id: str
    model_report: Optional[Dict[str, Any]]
    raw_reply: str
    error: Optional[str] = None


async def run_one_item(
    *,
    item: Dict[str, Any],
    agent_name: str,
    timeout_s: int,
    repo_root: Path,
    dry_run: bool,
) -> TaskResult:
    started = _utc_now()
    session_id = f"overnight:{item.get('id','item')}".replace(" ", "_")

    # Snapshot git state for the workspace repo.
    start_head = _git_head(repo_root)

    raw_reply = ""
    model_report: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    if dry_run:
        await asyncio.sleep(0.01)
        finished = _utc_now()
        return TaskResult(
            task=item,
            status="success",
            started_at=_iso(started),
            finished_at=_iso(finished),
            duration_seconds=(finished - started).total_seconds(),
            files_changed=[],
            commits_made=[],
            agent=agent_name,
            session_id=session_id,
            model_report={"success": True, "summary": "dry-run (no execution)", "files_changed": [], "commits_made": [], "notes": ""},
            raw_reply="dry-run",
        )

    prompt = _build_prompt(item)

    cmd = [
        "openclaw",
        "agent",
        "--agent",
        agent_name,
        "--session-id",
        session_id,
        "--message",
        prompt,
        "--json",
        "--timeout",
        str(timeout_s),
    ]

    try:
        # run in thread to avoid blocking event loop
        proc = await asyncio.to_thread(_run, cmd, cwd=repo_root, timeout_s=timeout_s + 30)
        if proc.returncode != 0:
            error = proc.stderr.strip() or proc.stdout.strip() or "openclaw agent failed"
        else:
            payload = json.loads(proc.stdout)
            payloads = (payload.get("result") or {}).get("payloads") or []
            raw_reply = (payloads[0].get("text") if payloads else "") or ""
            model_report = _extract_json_object(raw_reply)
    except subprocess.TimeoutExpired:
        error = f"timeout after {timeout_s}s"
    except Exception as exc:
        error = str(exc)

    finished = _utc_now()

    # Compute repo deltas regardless of agent output.
    end_head = _git_head(repo_root)
    commits = _git_commits_between(repo_root, start_head, end_head)
    files = sorted(set(_git_files_between(repo_root, start_head, end_head) + _git_uncommitted_files(repo_root)))

    # Determine success/fail.
    status = "success"
    if error:
        status = "fail"
    elif model_report and model_report.get("success") is False:
        status = "fail"

    return TaskResult(
        task=item,
        status=status,
        started_at=_iso(started),
        finished_at=_iso(finished),
        duration_seconds=(finished - started).total_seconds(),
        files_changed=files,
        commits_made=commits,
        agent=agent_name,
        session_id=session_id,
        model_report=model_report,
        raw_reply=raw_reply,
        error=error,
    )


def _sort_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def key(it: Dict[str, Any]) -> Tuple[float, int]:
        pr = it.get("priority")
        try:
            pr_val = float(pr)
        except Exception:
            pr_val = 1e9
        # Preserve stable order among equal priorities by using original index later.
        return (pr_val, 0)

    # Stable sort by priority only
    return sorted(items, key=key)


def _append_results(run_results: List[TaskResult]) -> Dict[str, Any]:
    existing = _load_json(RESULTS_PATH) or {"runs": [], "last_run_at": None}
    runs = existing.get("runs") if isinstance(existing.get("runs"), list) else []

    for r in run_results:
        runs.append(
            {
                "run_id": _iso(_utc_now()),
                "task": r.task,
                "status": r.status,
                "started_at": r.started_at,
                "finished_at": r.finished_at,
                "duration_seconds": r.duration_seconds,
                "files_changed": r.files_changed,
                "commits_made": r.commits_made,
                "agent": r.agent,
                "session_id": r.session_id,
                "model_report": r.model_report,
                "raw_reply": r.raw_reply,
                "error": r.error,
            }
        )

    existing["runs"] = runs[-2000:]  # cap history
    existing["last_run_at"] = _iso(_utc_now())
    _save_json(RESULTS_PATH, existing)
    return existing


def _format_summary(results: List[TaskResult]) -> str:
    ok = sum(1 for r in results if r.status == "success")
    fail = sum(1 for r in results if r.status != "success")

    lines: List[str] = []
    lines.append("🌙 Overnight build summary")
    lines.append(f"Tasks: {len(results)} (✅ {ok} / ❌ {fail})")
    lines.append("")

    for r in results:
        tid = r.task.get("id", "(no-id)")
        pr = r.task.get("priority", "?")
        t = r.task.get("type", "")
        spec = (r.task.get("spec") or "").strip().split("\n")[0]
        status = "✅" if r.status == "success" else "❌"
        dur = int(r.duration_seconds)
        lines.append(f"{status} {tid} (p{pr}, {t}, {dur}s): {spec}")
        if r.commits_made:
            lines.append(f"  commits: {len(r.commits_made)}")
        if r.files_changed:
            lines.append(f"  files: {len(r.files_changed)}")
        if r.error:
            lines.append(f"  error: {r.error}")

    return "\n".join(lines).strip() + "\n"


def _send_telegram(text: str) -> None:
    script = SCRIPTS_DIR / "simple_telegram_notify.py"
    if not script.exists():
        raise RuntimeError("simple_telegram_notify.py not found")
    p = _run([sys.executable, str(script), text], cwd=CLAWD, timeout_s=30)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip() or "Failed to send Telegram")


async def main_async() -> int:
    global QUEUE_PATH, RESULTS_PATH

    ap = argparse.ArgumentParser(description="Overnight build runner (queue → Codex → results → Telegram)")
    ap.add_argument("--queue", default=str(QUEUE_PATH), help="Path to overnight queue JSON")
    ap.add_argument("--results", default=str(RESULTS_PATH), help="Path to results JSON")
    ap.add_argument("--agent", default=DEFAULT_AGENT_NAME, help=f"OpenClaw agent name (default: {DEFAULT_AGENT_NAME})")
    ap.add_argument("--model", default=DEFAULT_AGENT_MODEL, help=f"Model id used if agent is auto-created (default: {DEFAULT_AGENT_MODEL})")
    ap.add_argument("--max-concurrency", type=int, default=DEFAULT_MAX_CONCURRENCY)
    ap.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_S)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--send-summary", action="store_true", help="Send Telegram summary at end")
    ap.add_argument("--send-summary-only", action="store_true", help="Send Telegram summary for last run and exit")
    args = ap.parse_args()

    QUEUE_PATH = Path(args.queue).expanduser()
    RESULTS_PATH = Path(args.results).expanduser()

    # Safety: prevent overlapping runs.
    lock_fd = _acquire_lock()
    if lock_fd is None:
        print("Another overnight_builder run is already active (lock held).", file=sys.stderr)
        return 2

    try:
        if args.send_summary_only:
            existing = _load_json(RESULTS_PATH) or {}
            runs = existing.get("runs") if isinstance(existing.get("runs"), list) else []
            if not runs:
                print("No previous runs found; nothing to summarize.")
                return 0
            # summarize last contiguous run batch (best-effort: last 20)
            last = runs[-20:]
            # render a simple, stable summary
            lines = ["🌅 Morning overnight build summary", f"Last results entries: {len(last)}", ""]
            for r in last:
                task = r.get("task") or {}
                tid = task.get("id", "(no-id)")
                st = r.get("status", "?")
                emoji = "✅" if st == "success" else "❌"
                dur = r.get("duration_seconds")
                dur_s = f"{int(dur)}s" if isinstance(dur, (int, float)) else "?s"
                lines.append(f"{emoji} {tid} ({dur_s})")
            _send_telegram("\n".join(lines))
            print("Sent summary.")
            return 0

        if not args.dry_run:
            if not codex_available():
                print("Codex is not available (state/codex_status.json). Aborting.")
                return 3

        # Ensure codex agent exists (even for dry run, for consistent behavior).
        ensure_codex_agent(agent_name=args.agent, model=args.model, workspace=Path.home() / ".openclaw" / "workspace")

        queue = _load_json(QUEUE_PATH) or {"items": []}
        items = queue.get("items")
        if not isinstance(items, list):
            items = []

        # Filter invalid items
        normalized: List[Dict[str, Any]] = []
        for it in items:
            if not isinstance(it, dict):
                continue
            if not it.get("id") or not it.get("spec") or it.get("priority") is None:
                continue
            normalized.append(it)

        if not normalized:
            print("Queue is empty. Nothing to do.")
            return 0

        ordered = _sort_items(normalized)

        sem = asyncio.Semaphore(max(1, int(args.max_concurrency)))
        repo_root = CLAWD

        results: List[TaskResult] = []

        async def worker(it: Dict[str, Any]) -> None:
            async with sem:
                res = await run_one_item(
                    item=it,
                    agent_name=args.agent,
                    timeout_s=int(args.timeout_seconds),
                    repo_root=repo_root,
                    dry_run=bool(args.dry_run),
                )
                results.append(res)

        # Launch tasks (bounded by semaphore)
        await asyncio.gather(*[worker(it) for it in ordered])

        # Persist results
        _append_results(results)

        # Remove processed items from queue (so we don't rerun them).
        processed_ids = {r.task.get("id") for r in results}
        remaining = [it for it in items if isinstance(it, dict) and it.get("id") not in processed_ids]
        _save_json(QUEUE_PATH, {"items": remaining})

        summary = _format_summary(results)
        print(summary)

        if args.send_summary:
            _send_telegram(summary)
            print("Sent Telegram summary.")

        return 0

    finally:
        _release_lock(lock_fd)


def main() -> None:
    try:
        rc = asyncio.run(main_async())
    except KeyboardInterrupt:
        rc = 130
    except Exception as exc:
        print(f"overnight_builder failed: {exc}", file=sys.stderr)
        rc = 1
    raise SystemExit(rc)


if __name__ == "__main__":
    main()
