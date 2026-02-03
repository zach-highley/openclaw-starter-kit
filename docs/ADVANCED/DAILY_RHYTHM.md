# DAILY_RHYTHM.md — Daily Planning + Review (Template)

This is a tiny, dependency-free daily ritual for your OpenClaw workspace.

Tip: many people create a convenience symlink like `~/openclaw-workspace` → `~/.openclaw/workspace`.

## Why this exists

- **Low friction.** One command in the morning, one at night.
- **Single source of truth.** Uses the same files the agent uses (`state/current_work.json`, `PROJECTS.md`, `memory/`).
- **Works offline-ish.** No extra Python deps; optional CLIs only.

---

## Morning: Daily Planner

Run:

```bash
python3 ~/openclaw-workspace/scripts/daily_planner.py
```

What it does:

1. **Calendar (optional):**
   - If `gog` CLI is installed, it tries to print “today’s calendar”.
   - If `gog` isn’t present (or its calendar subcommand differs), it skips.

2. **Current work (incomplete):**
   - Reads `state/current_work.json` and prints any task whose `status != "DONE"`.

3. **Backlog / priorities:**
   - Pulls from `PROJECTS.md`:
     - The **Active** section
     - The **Overnight build queue** list

4. **Focus prompt:**
   - Prompts for 1–3 focus areas.
   - Appends them to `memory/YYYY-MM-DD.md` under a “Morning plan” section.

Non-interactive mode (CI / piping):

```bash
python3 ~/openclaw-workspace/scripts/daily_planner.py --no-prompt
```

---

## Evening: Daily Review

Run:

```bash
python3 ~/openclaw-workspace/scripts/daily_review.py
```

What it does:

1. **Accomplished (best-effort):**
   - Pulls all `status == "DONE"` items from `state/current_work.json`.
   - Prompts you for any additional accomplishments.

2. **Writes a summary:**
   - Appends a “Daily review” block to `memory/YYYY-MM-DD.md`.

3. **Overnight queue:**
   - Prompts for overnight build items.
   - Appends them to `state/overnight_queue.json` (created if missing).

4. **Telegram summary:**
   - Sends the summary via the `openclaw` CLI:

     ```bash
     openclaw message send --channel telegram --target <chat_id> --message "..."
     ```

   - Target resolution:
     - `TELEGRAM_TARGET` env var (required)
     - (no default; keep it explicit to avoid misdelivery)

Disable Telegram send:

```bash
python3 ~/openclaw-workspace/scripts/daily_review.py --no-telegram
```

Dry run (prints summary, does not modify files; uses `openclaw --dry-run` if available):

```bash
python3 ~/openclaw-workspace/scripts/daily_review.py --dry-run
```

---

## Files touched

- `state/current_work.json` (read)
- `PROJECTS.md` (read)
- `memory/YYYY-MM-DD.md` (append)
- `state/overnight_queue.json` (write/append)

---

## Notes / expectations

- This is intentionally **simple**.
- If `gog` calendar output isn’t what you want, update the command attempts in `scripts/daily_planner.py`.
- If you want the overnight queue to drive an actual nightly automation later, `state/overnight_queue.json` is designed to be machine-readable.
