# System Maintenance — Weekly Auto-Tasks (optional)

This starter kit includes **two small, opt-in scripts** for routine maintenance.

They are intentionally conservative:
- **Default is dry-run** (no changes) unless you pass `--apply`.
- **No sudo.**
- **Workspace-scoped cleanup** only (no deleting `/tmp`, no touching your Downloads folder).

If you want deeper machine maintenance (OS updates, disk pruning, Xcode DerivedData, etc.), keep it separate from OpenClaw automation and follow your OS/vendor guidance.

---

## Auto-Update (`scripts/auto_update.py`)

Updates Homebrew packages weekly.

```bash
# Dry-run (prints what it would do)
python3 scripts/auto_update.py

# Apply (actually runs brew update/upgrade)
python3 scripts/auto_update.py --apply

# JSON summary (useful for posting in a weekly heartbeat)
python3 scripts/auto_update.py --apply --json
```

What it does (when `--apply`):
- `brew update`
- `brew upgrade`

If Homebrew is not installed, it prints “brew not found” and exits successfully.

---

## Auto-Cleanup (`scripts/auto_cleanup.py`)

Weekly cleanup with safe defaults.

```bash
# Dry-run
python3 scripts/auto_cleanup.py

# Apply (runs brew cleanup + deletes old *.log files under the current directory)
python3 scripts/auto_cleanup.py --apply

# Only delete logs older than 30 days
python3 scripts/auto_cleanup.py --apply --older-than-days 30

# Skip brew cleanup
python3 scripts/auto_cleanup.py --apply --no-brew
```

What it does (when `--apply`):
- Runs `brew cleanup` (if Homebrew exists; can be disabled with `--no-brew`)
- Deletes `*.log` files **under the current working directory** older than `--older-than-days` (default: 14)

What it does **not** do:
- Delete system temp folders
- Delete anything outside your repo/workspace
- Touch Xcode DerivedData

---

## Adding to Your Heartbeat

```markdown
## Weekly Tasks (Sunday mornings)
- Run `python3 scripts/auto_update.py --apply --json` and post the summary.
- Run `python3 scripts/auto_cleanup.py --apply --json` and post the summary.
```

---

## Model Router (`scripts/model_router.py`)

Programmatic model selection based on task type and current usage.

```bash
# Get recommended model for a coding task
python3 scripts/model_router.py --task-type coding

# Just check current usage levels
python3 scripts/model_router.py --check-only
```

Returns the optimal model based on:
- Task type (coding, research, summarization, quick)
- Current usage against rate limits
- Logarithmic degradation curve (uses cheaper models as usage increases)
