# Hacker News (Show HN)

## Title
Show HN: OpenClaw Starter Kit - 24/7 AI assistant setup guide (open source)

## Body
I built and open-sourced a starter kit for running OpenClaw as a 24/7 personal agent.

Repo: https://github.com/zach-highley/openclaw-starter-kit

Engineering choices behind it:
- one-process reliability (`launchd/systemd` + `KeepAlive=true`)
- daily self-heal (`openclaw doctor --fix` at 5 AM)
- hardened defaults from auditing 355 config options
- practical model fallback and memory settings for long-running sessions
- Telegram delivery fix for paragraph-splitting (`chunkMode: length`)

The goal is operational stability over novelty. I included failures and incident lessons, not just ideal configs.

If useful, I’d love feedback on where this fails in real deployments.
