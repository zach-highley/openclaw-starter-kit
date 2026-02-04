# Delivery Gotchas (How to Make Automations Actually Send)

The most common failure mode in “agent automation” is boring:

> The job ran, but nothing was delivered.

This doc explains how to avoid that.

## systemEvent vs agentTurn

### systemEvent (main session)
- Injects a message into the session.
- **Does not automatically send a message to your chat**.
- Useful for nudging the agent (“check X”), especially when paired with heartbeat.

### agentTurn (isolated session)
- Runs the agent like a normal turn.
- Can **send messages** when `deliver:true` *and/or* when the agent calls the message tool.
- Best for guaranteed recaps and scheduled reporting.

## Best practice: for scheduled reports, use agentTurn + deliver:true

If you want something to show up in Telegram every time:
- use an isolated cron job
- set `deliver:true`
- and instruct the job to send via the message tool

## Best practice: for awareness, use heartbeat

If you want “tell me only if something needs attention”:
- use heartbeat
- keep HEARTBEAT.md short

**Important:** In some setups, replying `HEARTBEAT_OK` can behave like an ack and may be dropped (meaning you see nothing).

If you want a visible pulse in Telegram, prefer a short "proof-of-work" message instead (e.g., `💓 Heartbeat 10:34 AM` + 3–6 status lines).
## Debugging checklist

1) `openclaw cron list` (is the job enabled? nextRunAt?)
2) `openclaw cron runs <job-id>` (did it run? duration? errors?)
3) `openclaw status --deep` (is the channel healthy?)
4) `openclaw logs --follow` (look for tool errors)

## Telegram-specific delivery gotchas

### 1) Message CLI requires `--target`

This is an easy mistake in scripts.

```bash
openclaw message send --channel telegram --target "-1001234567890" --message "hi"
```

### 2) Prefer numeric chat IDs

For reliability, prefer numeric chat ids:
- DMs: positive integer
- Groups/supergroups: negative integer like `-1001234567890`

How to find it: see `docs/TELEGRAM_SETUP.md` (or the official Telegram channel docs).

### 3) Topics need a thread id

Telegram forums use topics (message_thread_id). For proactive sends:

```bash
openclaw message send --channel telegram \
  --target "-1001234567890" \
  --thread-id "123" \
  --message "hello topic"
```

Cron delivery can encode topics in `--to`:
- `-1001234567890:topic:123`

## Avoiding redundancy

- Don’t have both a heartbeat and a cron job do the same check.
- If you must, define:
  - heartbeat = awareness
  - cron = action/report
