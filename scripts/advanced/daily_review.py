#!/usr/bin/env python3
"""Daily Review (evening) — lightweight wrap-up.

What it does
------------
1) Summarizes what was accomplished today (best-effort):
   - DONE items from state/current_work.json
   - Optionally: user-entered accomplishments
2) Appends a daily summary block to memory/YYYY-MM-DD.md
3) Updates/creates a small overnight queue file: state/overnight_queue.json
4) Sends the summary to Telegram via the `openclaw` CLI (if available)

No external deps.

Usage
-----
  python3 scripts/daily_review.py
  python3 scripts/daily_review.py --date 2026-02-03
  python3 scripts/daily_review.py --no-telegram
  python3 scripts/daily_review.py --dry-run

"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import date, datetime
from typing import Any, Optional

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STATE_CURRENT_WORK = os.path.join(WORKSPACE, 'state', 'current_work.json')
STATE_OVERNIGHT_QUEUE = os.path.join(WORKSPACE, 'state', 'overnight_queue.json')
MEMORY_DIR = os.path.join(WORKSPACE, 'memory')

DEFAULT_TELEGRAM_TARGET = os.environ.get('TELEGRAM_TARGET')


def _read_json(path: str) -> Optional[dict[str, Any]]:
  try:
    with open(path, 'r', encoding='utf-8') as f:
      data = json.load(f)
      return data if isinstance(data, dict) else None
  except FileNotFoundError:
    return None
  except Exception:
    return None


def _write_json(path: str, data: Any) -> None:
  os.makedirs(os.path.dirname(path), exist_ok=True)
  with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, sort_keys=False)
    f.write('\n')


def memory_path_for_day(d: date) -> str:
  os.makedirs(MEMORY_DIR, exist_ok=True)
  return os.path.join(MEMORY_DIR, f"{d.isoformat()}.md")


def append_to_memory(d: date, text: str) -> None:
  path = memory_path_for_day(d)
  exists = os.path.exists(path)

  stamp = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')
  block: list[str] = []
  if not exists:
    block.append(f"# {d.isoformat()}\n")
  block.append(f"\n## Daily review ({stamp})\n")
  block.append(text.rstrip() + "\n")

  with open(path, 'a', encoding='utf-8') as f:
    f.write('\n'.join(block))


def get_done_items_from_current_work() -> list[str]:
  data = _read_json(STATE_CURRENT_WORK)
  if not data:
    return []
  tasks = data.get('tasks')
  if not isinstance(tasks, list):
    return []

  done_lines: list[str] = []
  for t in tasks:
    if not isinstance(t, dict):
      continue
    status = str(t.get('status') or '').strip().upper()
    if status != 'DONE':
      continue
    tid = t.get('id')
    name = str(t.get('name') or '').strip()
    note = str(t.get('note') or '').strip()

    head = []
    if tid is not None:
      head.append(f"#{tid}")
    if name:
      head.append(name)
    line = ' '.join(head) if head else '(done)'
    if note:
      line += f" — {note}"
    done_lines.append(line)

  return done_lines


def prompt_list(prompt: str) -> list[str]:
  if not sys.stdin.isatty():
    return []
  print(prompt)
  print('(blank line to finish)')
  items: list[str] = []
  while True:
    s = input('> ').strip()
    if not s:
      break
    items.append(s)
  return items


def load_overnight_queue() -> dict[str, Any]:
  data = _read_json(STATE_OVERNIGHT_QUEUE)
  if data and isinstance(data, dict):
    return data
  # Default structure
  return {
    'updated': None,
    'items': [],
  }


def update_overnight_queue(items: list[str]) -> dict[str, Any]:
  q = load_overnight_queue()
  cur_items = q.get('items')
  if not isinstance(cur_items, list):
    cur_items = []

  # Append new items as simple dicts.
  for it in items:
    cur_items.append({
      'text': it,
      'added': datetime.now().astimezone().isoformat(),
      'status': 'QUEUED',
    })

  q['items'] = cur_items
  q['updated'] = datetime.now().astimezone().isoformat()
  _write_json(STATE_OVERNIGHT_QUEUE, q)
  return q


def get_usage_pace() -> str:
  """Calculate if we're above or below pace for Claude and Codex usage."""
  try:
    result = subprocess.run(
      ['python3', os.path.join(WORKSPACE, 'scripts', 'check_usage.py'), '--json'],
      capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
      return ''
    
    # Get codexbar usage for Claude
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
    
    pace_lines = []
    pace_lines.append(f"📊 Token Pace (target: {expected_pct:.0f}% by now):")
    
    claude_diff = claude_pct - expected_pct
    claude_emoji = "📈" if claude_diff >= 0 else "📉"
    claude_status = "ABOVE" if claude_diff >= 0 else "BELOW"
    pace_lines.append(f"  {claude_emoji} Claude: {claude_pct:.0f}% ({claude_status} pace by {abs(claude_diff):.0f}%)")
    
    codex_diff = codex_pct - expected_pct
    codex_emoji = "📈" if codex_diff >= 0 else "📉"
    codex_status = "ABOVE" if codex_diff >= 0 else "BELOW"
    pace_lines.append(f"  {codex_emoji} Codex: {codex_pct:.0f}% ({codex_status} pace by {abs(codex_diff):.0f}%)")
    
    if claude_diff < -10 or codex_diff < -10:
      pace_lines.append("  ⚡ BURN FASTER!")
    elif claude_diff > 10 and codex_diff > 10:
      pace_lines.append("  ✅ On track!")
    
    return '\n'.join(pace_lines)
  except Exception as e:
    return f"(pace calculation failed: {e})"


def build_summary(d: date, done: list[str], extra_done: list[str], overnight: list[str], blockers: list[str]) -> str:
  lines: list[str] = []
  lines.append(f"Daily review — {d.isoformat()}")

  if done or extra_done:
    lines.append('')
    lines.append('Accomplished:')
    for x in done:
      lines.append(f"- {x}")
    for x in extra_done:
      lines.append(f"- {x}")
  else:
    lines.append('')
    lines.append('Accomplished:')
    lines.append('- (none captured)')

  if blockers:
    lines.append('')
    lines.append('Blockers / notes:')
    for b in blockers:
      lines.append(f"- {b}")

  if overnight:
    lines.append('')
    lines.append('Overnight queue:')
    for it in overnight:
      lines.append(f"- {it}")

  # Add usage pace
  pace = get_usage_pace()
  if pace:
    lines.append('')
    lines.append(pace)

  return '\n'.join(lines).strip()


def send_telegram(text: str, target: str, dry_run: bool) -> bool:
  openclaw = shutil.which('openclaw')
  if not openclaw:
    print('daily_review: openclaw CLI not found; skipping Telegram send', file=sys.stderr)
    return False

  cmd = [
    openclaw,
    'message',
    'send',
    '--channel',
    'telegram',
    '--target',
    target,
    '--message',
    text,
  ]
  if dry_run:
    cmd.append('--dry-run')

  try:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if p.returncode != 0:
      stderr = (p.stderr or '').strip()
      print(f"daily_review: telegram send failed (code={p.returncode}): {stderr}", file=sys.stderr)
      return False
    return True
  except Exception as e:
    print(f'daily_review: telegram send error: {e}', file=sys.stderr)
    return False


def main() -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument('--date', help='ISO date (YYYY-MM-DD). Defaults to today.')
  ap.add_argument('--no-telegram', action='store_true', help='Do not send Telegram summary.')
  ap.add_argument('--dry-run', action='store_true', help='Do not write files; do not send (unless you want openclaw --dry-run).')
  ap.add_argument('--target', help='Telegram chat id/@username. Defaults to TELEGRAM_TARGET env or hardcoded default.')
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

  done = get_done_items_from_current_work()

  extra_done: list[str] = []
  overnight_items: list[str] = []
  blockers: list[str] = []

  if not args.no_prompt and sys.stdin.isatty():
    extra_done = prompt_list('Anything else you accomplished today?')
    blockers = prompt_list('Any blockers / notes for tomorrow?')
    overnight_items = prompt_list('Overnight build / queue items to add?')

  summary = build_summary(d, done=done, extra_done=extra_done, overnight=overnight_items, blockers=blockers)

  # Write memory + overnight queue unless dry-run
  if args.dry_run:
    print(summary)
  else:
    append_to_memory(d, summary)
    if overnight_items:
      update_overnight_queue(overnight_items)

  # Telegram send
  if not args.no_telegram:
    target = (args.target or DEFAULT_TELEGRAM_TARGET).strip()
    if target:
      # If --dry-run, we still call openclaw with --dry-run so you can preview payload.
      send_telegram(summary, target=target, dry_run=args.dry_run)

  return 0


if __name__ == '__main__':
  raise SystemExit(main())
