# System Maintenance — Weekly Auto-Tasks

Two scripts handle routine system maintenance so you never have to think about it.

## Auto-Update (`scripts/auto_update.py`)

Updates Homebrew packages weekly. Run on Sunday mornings via heartbeat or cron.

```bash
python3 scripts/auto_update.py
```

What it does:
- `brew update && brew upgrade`
- Logs what was updated
- Reports any failures
- Returns JSON with update summary

## Auto-Cleanup (`scripts/auto_cleanup.py`)

Cleans temporary files weekly. Keeps your disk tidy.

```bash
# Standard cleanup
python3 scripts/auto_cleanup.py

# Include Xcode derived data (if you're an iOS dev)
python3 scripts/auto_cleanup.py --include-xcode
```

What it cleans:
- System temp files (`/tmp`, `/var/folders`)
- Homebrew cache (`brew cleanup`)
- Old log files
- Xcode derived data (optional)

What it does NOT clean:
- Downloads folder
- Trash
- Anything in your workspace

## Adding to Your Heartbeat

```markdown
## Weekly Tasks (Sunday mornings)
- Run `python3 scripts/auto_update.py` to update brew packages
- Run `python3 scripts/auto_cleanup.py` to clean temp files
- Report summary to [USER]
```

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
