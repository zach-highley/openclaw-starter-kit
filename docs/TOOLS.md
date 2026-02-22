# TOOLS.md - Local Environment Notes

## Installed CLI Tools
- `himalaya` — Email CLI (IMAP/SMTP)
- `gog` — Google Workspace CLI (Gmail, Calendar, Drive)
- `remindctl` — Apple Reminders CLI
- `peekaboo` — macOS UI capture/automation
- `openhue` — Philips Hue control (needs bridge pairing)
- `gifgrep` — GIF search/download
- `rg` (ripgrep) — Fast text search
- `jq` — JSON processor
- `codex` — OpenAI Codex CLI (coding agent)
- `tmux` — Terminal multiplexer (installed via brew)
- `gh` — GitHub CLI (authenticated as zach-highley)

## Installed Skills
- `doctor` — Health check skill
- `ralph-loop` — Continuous execution loops
- `youtube-watcher` — YouTube monitoring (with get_transcript.py)
- `yt-api-cli` — YouTube API CLI

## TTS
- Preferred voice: British male (when ElevenLabs/voice integration is set up)

## Git Repos (Local)
- Workspace: `~/.openclaw/workspace/` (local git, no remote)
- Dashboard: cloned to `/tmp/dashboard-check/` (temporary working copy)
- Starter kit: cloned to `/tmp/openclaw-starter-kit/` (temporary working copy)

## Google Accounts (Authenticated)
- zachhgg@gmail.com (u/0 in browser)
- zach@zhighley.com (u/1 in browser)
- zmhighley@gmail.com (needs browser login)
- hello@thehealthymandaily.com (needs browser login)
- support@zhighley.com (needs browser login)

## X/Twitter API (ALWAYS USE THIS, NEVER SCRAPE)
- App: EricRibbitA (@EricRibbitAI) — read + write access
- Keys in .env: X_BEARER_TOKEN, X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
- Fetch tweets: `GET https://api.twitter.com/2/tweets/{id}?tweet.fields=created_at,author_id,text,public_metrics`
- Search: `GET https://api.twitter.com/2/tweets/search/recent?query=...`
- Local helper script (added): `python3 scripts/x_api.py`
  - Tweet by ID: `python3 scripts/x_api.py tweet <tweet_id>`
  - Recent search: `python3 scripts/x_api.py search "<query>" --max-results 10`
- NEVER use web_fetch/browser/nitter for X content. API only.

## Telegram
- Bot: @EricRibbitBot
- Zach's ID: 7246353227
- Ack reaction: 👀
- Exec approval format: `/approve <id> allow-once`

## Paths
- OpenClaw config: `~/.openclaw/openclaw.json`
- OpenClaw env: `~/.openclaw/.env`
- OpenClaw workspace: `~/.openclaw/workspace/`
- OpenClaw logs: `/tmp/openclaw/openclaw.log`
- OpenClaw CLI: `/opt/homebrew/bin/openclaw`
- Enchiridion: `~/Library/Mobile Documents/com~apple~CloudDocs/Work/iPhone Apps/GetSmart/` (DO NOT TOUCH)
