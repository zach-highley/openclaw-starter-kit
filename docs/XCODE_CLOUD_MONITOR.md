# Xcode Cloud Build Monitor

## What It Does

Automatically monitors your Gmail for Xcode Cloud build failure emails, extracts the actual compiler errors, and can auto-spawn a coding agent to fix them.

## How It Works

1. Searches Gmail (via `gog` CLI) for Apple build failure emails
2. Parses the HTML email body to extract file paths and error messages
3. Compares against known errors (avoids re-fixing the same thing)
4. Generates a fix task that can be handed to Codex/Claude Code
5. Tracks consecutive failures, fix attempts, and success history

## Setup

Requires:
- `gog` CLI configured with Gmail access
- Gmail account(s) that receive Xcode Cloud notifications

## Integration

Add to your HEARTBEAT.md:

```markdown
## Xcode Cloud Build Monitor (every heartbeat)
Run `python3 scripts/xcode_cloud_monitor.py` and check:
- If `has_failures` is true AND `is_repeat` is false: auto-fix with Codex
- If `is_repeat` is true: escalate to user (avoid infinite fix loops)
- Max 2 auto-fix attempts per unique error set
```

## Multi-Account Support

If you receive build emails on multiple accounts, configure both:

```python
GMAIL_ACCOUNTS = [
    "personal@gmail.com",
    "work@company.com",
]
```

The monitor searches all accounts and deduplicates by thread ID.

## Lessons Learned

- Xcode Cloud email subjects vary — use a broad search query, not just `subject:"failed"`
- `gog gmail search` can return `null` threads (not empty array) — always guard with `or []`
- HTML email parsing is fragile — the `XcodeEmailParser` handles Apple's specific format but may need updating if Apple changes their email template
- **Always run a local build** (`xcodebuild`) to verify fixes before pushing — Xcode Cloud builds are slow and you don't want another failure email

See `scripts/build_monitor.py` for the sanitized template.
