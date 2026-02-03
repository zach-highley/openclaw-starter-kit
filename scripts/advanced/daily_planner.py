#!/usr/bin/env python3
"""Daily Planner (morning) — lightweight terminal ritual.

Goals
-----
- Give the user a quick situational snapshot: calendar, current work, and project backlog.
- Prompt for a couple focus areas + a "today plan" note.

No external deps. Uses optional CLIs if present.

Usage
-----
  python3 scripts/daily_planner.py
  python3 scripts/daily_planner.py --date 2026-02-03

Outputs
-------
- Prints a formatted briefing to stdout.
- Writes an optional note to: memory/YYYY-MM-DD.md (appended).

"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STATE_CURRENT_WORK = os.path.join(WORKSPACE, 'state', 'current_work.json')
PROJECTS_MD = os.path.join(WORKSPACE, 'PROJECTS.md')
MEMORY_DIR = os.path.join(WORKSPACE, 'memory')


def _read_text(path: str) -> Optional[str]:
  try:
    with open(path, 'r', encoding='utf-8') as f:
      return f.read()
  except FileNotFoundError:
    return None


def _read_json(path: str) -> Optional[dict[str, Any]]:
  try:
    with open(path, 'r', encoding='utf-8') as f:
      data = json.load(f)
      return data if isinstance(data, dict) else None
  except FileNotFoundError:
    return None
  except Exception:
    return None


def _hr(title: str) -> str:
  return f"\n{'=' * 6} {title} {'=' * 6}"


def _run_cmd(cmd: list[str], timeout: int = 8) -> tuple[int, str, str]:
  try:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout.strip(), p.stderr.strip()
  except FileNotFoundError:
    return 127, '', f"not found: {cmd[0]}"
  except subprocess.TimeoutExpired:
    return 124, '', 'timeout'
  except Exception as e:
    return 1, '', str(e)


def show_usage_pace() -> None:
  """Show if we're above or below pace for Claude and Codex usage."""
  print(_hr('Token Pace'))
  try:
    claude_result = subprocess.run(
      ['codexbar', 'usage', '--provider', 'claude', '--format', 'json'],
      capture_output=True, text=True, timeout=30
    )
    codex_result = subprocess.run(
      ['codexbar', 'usage', '--provider', 'codex', '--format', 'json'],
      capture_output=True, text=True, timeout=30
    )
    
    claude_pct = 0
    codex_pct = 0
    
    if claude_result.returncode == 0:
      claude_data = json.loads(claude_result.stdout)
      claude_pct = claude_data.get('usage', {}).get('secondary', {}).get('usedPercent', 0)
    
    if codex_result.returncode == 0:
      codex_data = json.loads(codex_result.stdout)
      codex_pct = codex_data.get('usage', {}).get('secondary', {}).get('usedPercent', 0)
    
    # Calculate expected pace (week resets Sunday)
    now = datetime.now()
    # Days since Sunday (Sunday = 0)
    days_since_sunday = (now.weekday() + 1) % 7
    hours_today = now.hour + now.minute / 60
    days_into_week = days_since_sunday + hours_today / 24
    expected_pct = (days_into_week / 7) * 100
    
    print(f"Target by now: {expected_pct:.0f}%")
    
    claude_diff = claude_pct - expected_pct
    claude_emoji = "📈" if claude_diff >= 0 else "📉"
    claude_status = "ABOVE" if claude_diff >= 0 else "BELOW"
    print(f"{claude_emoji} Claude: {claude_pct:.0f}% ({claude_status} pace by {abs(claude_diff):.0f}%)")
    
    codex_diff = codex_pct - expected_pct
    codex_emoji = "📈" if codex_diff >= 0 else "📉"
    codex_status = "ABOVE" if codex_diff >= 0 else "BELOW"
    print(f"{codex_emoji} Codex: {codex_pct:.0f}% ({codex_status} pace by {abs(codex_diff):.0f}%)")
    
    if claude_diff < -10 or codex_diff < -10:
      print("⚡ BURN FASTER!")
    elif claude_diff > 10 and codex_diff > 10:
      print("✅ On track!")
  except Exception as e:
    print(f"(pace calculation failed: {e})")


def show_calendar_for_day(d: date) -> None:
  print(_hr('Calendar'))

  gog = shutil.which('gog')
  if not gog:
    print('(gog CLI not found — skipping calendar)')
    return

  # We don’t assume gog’s exact subcommands; try a couple common patterns.
  attempts: list[list[str]] = [
    [gog, 'calendar', 'today'],
    [gog, 'calendar', '--today'],
    [gog, 'calendar'],
  ]

  out: Optional[str] = None
  for cmd in attempts:
    code, stdout, _stderr = _run_cmd(cmd, timeout=10)
    if code == 0 and stdout.strip():
      out = stdout
      break

  if not out:
    print('(gog calendar command not available or returned no output)')
    return

  # If gog printed multiple days, we still show it; keep it simple.
  print(out)


def show_incomplete_current_work() -> None:
  print(_hr('Current work (incomplete)'))

  data = _read_json(STATE_CURRENT_WORK)
  if not data:
    print(f"(missing or unreadable: {STATE_CURRENT_WORK})")
    return

  tasks = data.get('tasks')
  if not isinstance(tasks, list) or not tasks:
    print('(no tasks found)')
    return

  incomplete = []
  for t in tasks:
    if not isinstance(t, dict):
      continue
    status = str(t.get('status') or '').strip().upper()
    if status and status != 'DONE':
      incomplete.append(t)

  if not incomplete:
    print('✅ All current_work tasks are DONE')
    return

  for t in incomplete:
    tid = t.get('id')
    name = str(t.get('name') or '').strip()
    status = str(t.get('status') or '').strip()
    note = str(t.get('note') or '').strip()
    bits = []
    if tid is not None:
      bits.append(f"#{tid}")
    if status:
      bits.append(status)
    prefix = f"- {' '.join(bits)}: " if bits else '- '
    line = prefix + (name or '(unnamed task)')
    if note:
      line += f" — {note}"
    print(line)


def _extract_projects_active(md: str) -> list[str]:
  # Very simple extraction: keep lines between the Active header and the next header.
  start = md.find('## 🔴 Active')
  if start < 0:
    start = md.find('## Active')
  if start < 0:
    return []
  rest = md[start:]
  end = rest.find('\n## ')
  # end points at the same header; we want the next header after the first line.
  if end > 0:
    # Skip the first header occurrence.
    next_header = rest.find('\n## ', len('## 🔴 Active'))
    if next_header > 0:
      rest = rest[:next_header]

  lines = [l.rstrip() for l in rest.splitlines()]
  # Drop empty preamble lines and keep up to a reasonable size.
  trimmed = [l for l in lines if l.strip()]
  return trimmed[:30]


def _extract_overnight_queue(md: str) -> list[str]:
  start = md.find('**Queue:**')
  if start < 0:
    return []
  rest = md[start:]
  # Stop at "**Log:**" or next header.
  stop_candidates = []
  i = rest.find('**Log:**')
  if i >= 0:
    stop_candidates.append(i)
  j = rest.find('\n## ')
  if j >= 0:
    stop_candidates.append(j)
  stop = min(stop_candidates) if stop_candidates else len(rest)
  chunk = rest[:stop]
  lines = []
  for l in chunk.splitlines():
    l = l.rstrip()
    if l.strip().startswith('- ['):
      lines.append(l)
  return lines[:15]


def show_backlog() -> None:
  print(_hr('Backlog / priorities'))

  md = _read_text(PROJECTS_MD)
  if not md:
    print(f"(missing: {PROJECTS_MD})")
    return

  active = _extract_projects_active(md)
  if active:
    print('Active projects (from PROJECTS.md):')
    for l in active:
      print(l)
  else:
    print('(no Active section found in PROJECTS.md)')

  queue = _extract_overnight_queue(md)
  if queue:
    print('\nOvernight build queue:')
    for l in queue:
      print(l)


def memory_path_for_day(d: date) -> str:
  os.makedirs(MEMORY_DIR, exist_ok=True)
  return os.path.join(MEMORY_DIR, f"{d.isoformat()}.md")


def append_to_memory(d: date, text: str) -> None:
  path = memory_path_for_day(d)
  exists = os.path.exists(path)

  stamp = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')
  block = []
  if not exists:
    block.append(f"# {d.isoformat()}\n")
  block.append(f"\n## Morning plan ({stamp})\n")
  block.append(text.rstrip() + "\n")

  with open(path, 'a', encoding='utf-8') as f:
    f.write('\n'.join(block))


def prompt_for_focus(d: date, non_interactive: bool) -> None:
  print(_hr('Focus'))
  if non_interactive or not sys.stdin.isatty():
    print('(non-interactive mode; skipping prompts)')
    return

  print('What are your top 1–3 focus areas today? (blank line to finish)')
  items: list[str] = []
  while True:
    line = input('> ').strip()
    if not line:
      break
    items.append(line)

  if not items:
    print('(no focus items entered)')
    return

  note = '\n'.join([f"- {i}" for i in items])
  append_to_memory(d, note)
  print(f"Saved to memory/{d.isoformat()}.md")


def main() -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument('--date', help='ISO date (YYYY-MM-DD). Defaults to today.')
  ap.add_argument('--no-prompt', action='store_true', help='Skip interactive prompts.')
  args = ap.parse_args()

  if args.date:
    try:
      d = date.fromisoformat(args.date)
    except Exception:
      print('Invalid --date; expected YYYY-MM-DD', file=sys.stderr)
      return 2
  else:
    d = datetime.now().astimezone().date()

  print(f"Daily Planner — {d.isoformat()}")

  show_usage_pace()
  show_calendar_for_day(d)
  show_incomplete_current_work()
  show_backlog()
  prompt_for_focus(d, non_interactive=args.no_prompt)

  return 0


if __name__ == '__main__':
  raise SystemExit(main())
