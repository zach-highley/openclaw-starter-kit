# 🔨 CI/CD Build Failure Monitor

Automatically detect build failures from email notifications, parse the exact errors, and spawn an AI agent to fix them. No manual intervention needed.

## The Loop

```
You push code → CI/CD builds → build fails → failure email arrives →
AI reads email → parses errors → spawns Codex to fix → commits fix →
pushes → CI/CD rebuilds → (hopefully passes)
```

All automatic. You might not even know it broke.

## How It Works

### 1. Email Detection
The monitor searches Gmail for build failure emails using configurable search queries:
- **Xcode Cloud:** `from:noreply@apple.com subject:"failed" newer_than:1d`
- **GitHub Actions:** `from:notifications@github.com subject:"failed" newer_than:1d`
- **Custom:** Set `BUILD_MONITOR_QUERY` environment variable

### 2. Error Parsing
The script parses HTML email bodies to extract:
- **File paths** where errors occurred
- **Error messages** with line numbers
- **Commit info** that triggered the build

For Xcode Cloud, it reads the `<x-issuePath>` and `<div class="message">` tags.
For other CI systems, extend the `BuildEmailParser` class.

### 3. Fix Task Generation
Errors are formatted into a structured task that any coding AI can understand:
```
Fix the following CI/CD build errors:

1. Core/Services/ContentLoader.swift (line 1045)
   Error: 'async' call in a function that does not support concurrency

2. Core/Services/SpacedRepetitionManager.swift (line 157)
   Error: Left side of mutating operator isn't mutable: 'newToUse' is a 'let' constant
```

### 4. Auto-Fix Spawning
Your AI spawns a coding agent (Codex, Claude Code, etc.) with the fix task. The agent:
1. Reads the error details
2. Finds and fixes the code
3. Commits and pushes
4. The push triggers a new CI build

### 5. Repeat Detection
If the same errors appear after a fix attempt:
- **Attempt 1-2:** Try fixing again with more context
- **Attempt 3+:** Stop auto-fixing, alert the user
- This prevents infinite fix→fail→fix loops

## Setup

### Prerequisites
- `gog` CLI installed and authenticated (`brew install steipete/tap/gogcli`)
- Gmail account that receives CI/CD notifications
- A coding agent (Codex, Claude Code, etc.)

### Configuration
Set environment variables or edit `scripts/build_monitor.py`:

```bash
export BUILD_MONITOR_EMAIL="you@gmail.com"
export BUILD_MONITOR_QUERY='from:noreply@apple.com subject:"failed" newer_than:1d'
```

### Add to Heartbeat
In your `HEARTBEAT.md`:
```markdown
## Build Monitor (every heartbeat)
Run `python3 scripts/build_monitor.py` and check the result:
- If `has_failures` is true AND `should_auto_fix` is true:
  1. Message user about the failure
  2. Spawn coding agent with the `fix_task`
  3. Next heartbeat: check if the new build passed
- If `has_failures` and NOT `should_auto_fix` (repeat failures):
  1. Message user: needs manual review
- If no failures: skip silently
```

## State Tracking

State is stored in `state/build_monitor_state.json`:
```json
{
  "lastChecked": "2026-01-29T14:40:00Z",
  "lastBuildId": "abc123",
  "knownErrors": ["file.swift:error message"],
  "fixAttempts": 0,
  "consecutiveFailures": 2
}
```

## Extending for Other CI Systems

The `BuildEmailParser` class handles Xcode Cloud by default. To add support for GitHub Actions, CircleCI, etc.:

1. Create a new parser class that extends `HTMLParser`
2. Override `handle_starttag`, `handle_endtag`, `handle_data` for that CI's email format
3. Add a detection function that picks the right parser based on the email sender

Most CI systems send HTML emails with structured error information — you just need to find the right tags.

## Real-World Example

We built this after getting 10+ consecutive Xcode Cloud failure emails in one morning. Two errors were repeating across every build:
1. An `async` function called from a non-async context
2. A `let` constant being mutated

The monitor detected the first email, parsed both errors, spawned Codex, which fixed both in 2 minutes, committed, and pushed. The next Xcode Cloud build incorporated the fix. Total human intervention: zero.
