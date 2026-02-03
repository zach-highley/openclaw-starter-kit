# Telegram setup (Bot API) — starter-kit notes

This repo assumes you’re using Telegram as the primary “ops channel” for alerts
and scheduled deliveries.

Official reference: https://docs.openclaw.ai/channels/telegram

## 1) Create a bot token

- Chat with **@BotFather** in Telegram.
- Run `/newbot`.
- Copy the token.

## 2) Configure the token (config or env)

Either:

- Env: `TELEGRAM_BOT_TOKEN=...`

Or (recommended for explicitness):

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "123:abc",
      dmPolicy: "pairing",
      // For groups, start with mention-gated behavior:
      groups: { "*": { requireMention: true } },
    },
  },
}
```

Notes (from the docs):
- If both env and config are set, **config wins**.
- DMs default to **pairing** (you approve a code the first time).

## 3) Start (or restart) the Gateway

Use the Gateway service (recommended):

```bash
openclaw gateway install   # one-time
openclaw gateway restart
```

If config validation fails, the Gateway refuses to start. Run:

```bash
openclaw doctor
# and if needed
openclaw doctor --yes
```

## 4) Telegram chat IDs (IMPORTANT)

When you send Telegram messages via the CLI (`openclaw message …`) or via cron
delivery (`--to …`), the target must be a Telegram chat id.

Typical formats:
- **DMs**: a positive integer (your user id)
- **Groups / supergroups**: a **negative** integer like `-1001234567890`

### How to get the chat id

From the official docs (preferred):
- Forward a group message to `@userinfobot` / `@getidsbot` to see the chat id.
  (Privacy note: those are third-party bots.)

No-third-party option:
- Add your bot to the chat, send a message, then inspect logs:

```bash
openclaw logs --follow
# Look for inbound Telegram update; it includes chat.id.
```

## 5) Sending Telegram messages (CLI)

The message CLI requires **--target**.

```bash
openclaw message send --channel telegram \
  --target "-1001234567890" \
  --message "Hello from OpenClaw"
```

Telegram forum topics (supergroup forums):

```bash
openclaw message send --channel telegram \
  --target "-1001234567890" \
  --thread-id "123" \
  --message "Hello topic"
```

## 6) Cron delivery to Telegram

Cron isolated jobs can deliver automatically with `--deliver` + `--to`.
For topics, prefer the explicit `:topic:` encoding:

```bash
openclaw cron add \
  --name "Nightly summary" \
  --cron "0 22 * * *" \
  --tz "America/New_York" \
  --session isolated \
  --message "Summarize today." \
  --deliver --channel telegram \
  --to "-1001234567890:topic:123"
```

Reference: https://docs.openclaw.ai/automation/cron-jobs

## 7) Typing indicators (recommended defaults)

Typing indicators are configured globally via `agents.defaults.typingMode` and
`agents.defaults.typingIntervalSeconds`.

Reference: https://docs.openclaw.ai/concepts/typing-indicators

Suggested Telegram-friendly defaults:

```json5
{
  agents: {
    defaults: {
      typingMode: "message",          // avoid typing for NO_REPLY / silent runs
      typingIntervalSeconds: 6,        // default cadence
    },
  },
}
```

If you want “maximum liveness” (more typing indicators), set `typingMode:
"instant"`.

## 8) One Gateway per host (recommended)

Avoid starting extra gateway processes (for example `nohup openclaw gateway &`).
Use the service lifecycle commands instead:

```bash
openclaw gateway status
openclaw gateway restart
```

Reference: https://docs.openclaw.ai/gateway/multiple-gateways
