# Twitter Thread (6 Tweets)

1. I built a 24/7 AI assistant that runs my life. Here’s the open-source setup guide.

I spent months breaking my own setup so you don’t have to:
https://github.com/zach-highley/openclaw-starter-kit

2. Layer 1 is boring on purpose:
- `launchd/systemd` with `KeepAlive=true`
- one 5 AM `openclaw doctor --fix` cron

No watchdog circus. No monitor watching another monitor.

3. Layer 2 is security hardening from a 355-config audit:
- token auth only
- loopback bind
- Telegram allowlist
- mDNS off
- secrets in `.env`

Simple rules, fewer incidents.

4. Layer 3 is where it gets fun:
- model fallback chains
- memory tuning + context pruning
- cron vs heartbeat strategy
- Telegram chunking fix (`length`, not `newline`)

This is what kept my setup stable.

5. Layer 4 is my real stack (sanitized):
Claude + Codex + OpenRouter fallback, QMD memory, Brave search, Telegram channel, production lessons from stuff that failed in real life.

6. If you run OpenClaw, star the repo so more builders find it:
https://github.com/zach-highley/openclaw-starter-kit
