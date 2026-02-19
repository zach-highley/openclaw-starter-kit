# Reddit Post (r/selfhosted or r/artificial)

## Title
I audited 355 OpenClaw configs and wrote an open-source 24/7 setup guide (launchd/systemd + hardened defaults)

## Body
I’ve been running OpenClaw as a daily driver and kept hitting the same failure modes, so I documented the setup that actually held up.

Repo: https://github.com/zach-highley/openclaw-starter-kit

What’s inside:
- 4-layer setup guide from basic uptime to advanced config
- security hardening defaults (token auth, loopback bind, Telegram allowlist, mDNS off)
- launchd/systemd reliability pattern + 5 AM maintenance cron
- notes from a 355-option config audit and real incident cleanup
- model failover + memory tuning examples (sanitized config)

Big lesson: most of my downtime came from overengineering reliability, not from missing another monitor script.

If you try it, I’d love feedback on what broke and what I should tighten.

If you try it, report what breaks and what should be tightened next.
