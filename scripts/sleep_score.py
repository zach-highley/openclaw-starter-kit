#!/usr/bin/env python3
"""sleep_score.py — compute a simple sleep score from Eight Sleep intervals.

This script is an example of a *non-LLM* automation you can run on a schedule.
It calls `eightctl` locally, computes a score for the latest interval, and keeps a
small on-disk history so it can compute a rolling 30-day average without making
extra historical API calls.

Requirements:
- eightctl installed and authenticated (see eightctl docs)

Output:
- Prints JSON to stdout.
- Writes history to: state/sleep_history.json (under your workspace).

Usage:
  python3 scripts/sleep_score.py

Workspace:
  Defaults to parent directory of this script's folder.
  Override with OPENCLAW_WORKSPACE=/path/to/workspace.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def workspace_root() -> Path:
    raw = os.environ.get("OPENCLAW_WORKSPACE")
    if raw:
        return Path(raw).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


WORKSPACE = workspace_root()
HISTORY_PATH = WORKSPACE / "state" / "sleep_history.json"


def run_cmd(cmd: str, timeout_s: int = 25) -> Tuple[bool, str]:
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        return proc.returncode == 0, (proc.stdout or "").strip()
    except Exception:
        return False, ""


def parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def extract_intervals(payload: Any) -> List[Dict[str, Any]]:
    intervals: List[Dict[str, Any]] = []
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        return intervals
    for item in payload:
        if not isinstance(item, dict):
            continue
        if isinstance(item.get("intervals"), list):
            intervals.extend([i for i in item["intervals"] if isinstance(i, dict)])
        if isinstance(item.get("interval"), dict) and isinstance(item["interval"].get("intervals"), list):
            intervals.extend([i for i in item["interval"]["intervals"] if isinstance(i, dict)])
    return intervals


def pick_latest_interval(intervals: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not intervals:
        return None

    def sort_key(interval: Dict[str, Any]) -> datetime:
        end = parse_dt(interval.get("sleepEnd")) or parse_dt(interval.get("end"))
        start = parse_dt(interval.get("sleepStart")) or parse_dt(interval.get("start"))
        return end or start or datetime.min

    return max(intervals, key=sort_key)


def compute_score(interval: Dict[str, Any]) -> Dict[str, Any]:
    stage = interval.get("stageSummary") if isinstance(interval.get("stageSummary"), dict) else {}
    deep_pct = stage.get("deepPercentOfSleep")
    rem_pct = stage.get("remPercentOfSleep")
    duration_sec = interval.get("duration")

    if not isinstance(duration_sec, (int, float)):
        start = parse_dt(interval.get("sleepStart"))
        end = parse_dt(interval.get("sleepEnd"))
        if start and end:
            duration_sec = max(0, (end - start).total_seconds())
        else:
            duration_sec = None

    sleep_duration = stage.get("sleepDuration")
    if not isinstance(sleep_duration, (int, float)):
        sleep_duration = interval.get("sleepDuration") if isinstance(interval.get("sleepDuration"), (int, float)) else None

    duration_hours = duration_sec / 3600 if isinstance(duration_sec, (int, float)) else None

    # A simple, explainable heuristic. Tune for your preferences.
    if isinstance(duration_hours, (int, float)):
        if duration_hours <= 5:
            duration_score = 0.0
        elif duration_hours >= 8:
            duration_score = 40.0
        else:
            duration_score = ((duration_hours - 5) / 3.0) * 40.0
    else:
        duration_score = 0.0

    deep_score = min(25.0, (deep_pct / 0.20) * 25.0) if isinstance(deep_pct, (int, float)) else 0.0
    rem_score = min(25.0, (rem_pct / 0.25) * 25.0) if isinstance(rem_pct, (int, float)) else 0.0

    if isinstance(duration_sec, (int, float)) and duration_sec > 0 and isinstance(sleep_duration, (int, float)):
        efficiency_score = min(10.0, (sleep_duration / duration_sec) * 10.0)
    else:
        efficiency_score = 0.0

    total_score = int(round(duration_score + deep_score + rem_score + efficiency_score))

    return {
        "score": total_score,
        "duration_hours": round(duration_hours, 2) if isinstance(duration_hours, (int, float)) else None,
        "deep_pct": int(round(deep_pct * 100)) if isinstance(deep_pct, (int, float)) else None,
        "rem_pct": int(round(rem_pct * 100)) if isinstance(rem_pct, (int, float)) else None,
    }


@dataclass
class HistoryEntry:
    day: date
    score: int


def _parse_history_entry(obj: Any) -> Optional[HistoryEntry]:
    if not isinstance(obj, dict):
        return None
    ds = obj.get("date")
    sc = obj.get("score")
    if not isinstance(ds, str) or not ds:
        return None
    try:
        d = date.fromisoformat(ds)
    except Exception:
        return None
    if not isinstance(sc, (int, float)):
        return None
    return HistoryEntry(day=d, score=int(round(sc)))


def load_history(path: Path) -> List[HistoryEntry]:
    try:
        if not path.exists():
            return []
        raw = json.loads(path.read_text())
        if isinstance(raw, dict) and isinstance(raw.get("history"), list):
            raw = raw["history"]
        if not isinstance(raw, list):
            return []
        out: List[HistoryEntry] = []
        for item in raw:
            ent = _parse_history_entry(item)
            if ent:
                out.append(ent)
        by_day: Dict[date, int] = {}
        for ent in out:
            by_day[ent.day] = ent.score
        normalized = [HistoryEntry(day=d, score=s) for d, s in by_day.items()]
        normalized.sort(key=lambda e: e.day)
        return normalized
    except Exception:
        return []


def save_history(path: Path, entries: List[HistoryEntry]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [{"date": e.day.isoformat(), "score": e.score} for e in entries]
        path.write_text(json.dumps(payload, indent=2) + "\n")
    except Exception:
        pass


def upsert(entries: List[HistoryEntry], day: date, score: int, keep_last_n: int = 90) -> List[HistoryEntry]:
    try:
        by_day: Dict[date, int] = {e.day: e.score for e in entries}
        by_day[day] = int(score)
        out = [HistoryEntry(day=d, score=s) for d, s in by_day.items()]
        out.sort(key=lambda e: e.day)
        if keep_last_n > 0 and len(out) > keep_last_n:
            out = out[-keep_last_n:]
        return out
    except Exception:
        return entries


def rolling_avg(entries: List[HistoryEntry], end_day: date, window_days: int = 30) -> Optional[int]:
    try:
        if window_days <= 0:
            return None
        start_day = end_day - timedelta(days=window_days - 1)
        scores = [e.score for e in entries if start_day <= e.day <= end_day and isinstance(e.score, int)]
        if not scores:
            return None
        return int(round(sum(scores) / len(scores)))
    except Exception:
        return None


def interval_day(interval: Dict[str, Any]) -> date:
    dt = parse_dt(interval.get("sleepEnd")) or parse_dt(interval.get("end")) or parse_dt(interval.get("sleepStart")) or parse_dt(interval.get("start"))
    if isinstance(dt, datetime):
        try:
            return dt.date()
        except Exception:
            pass
    return datetime.now().date()


def main() -> int:
    empty = {"score": None, "duration_hours": None, "deep_pct": None, "rem_pct": None, "avg_score_30d": None}

    ok, raw = run_cmd("eightctl metrics intervals --quiet --output json")
    if not ok or not raw:
        print(json.dumps(empty))
        return 0

    try:
        parsed = json.loads(raw)
    except Exception:
        print(json.dumps(empty))
        return 0

    intervals = extract_intervals(parsed)
    latest = pick_latest_interval(intervals)
    if not latest:
        print(json.dumps(empty))
        return 0

    score = compute_score(latest)
    day = interval_day(latest)

    history = load_history(HISTORY_PATH)
    history = upsert(history, day, int(score["score"]))
    save_history(HISTORY_PATH, history)

    score["avg_score_30d"] = rolling_avg(history, day, window_days=30)

    print(json.dumps(score))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
