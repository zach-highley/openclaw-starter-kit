# Bot health checks (OpenClaw) — keep the Gateway boring

This repo is a **starter kit**, not the source of truth.
For canonical behavior and config schema, always defer to:
- https://docs.openclaw.ai/gateway/doctor
- https://docs.openclaw.ai/gateway/health
- https://docs.openclaw.ai/gateway/configuration

The biggest reliability wins come from:
1) **Strict config hygiene** (schema-valid only)
2) **One Gateway per host** (service supervised)
3) **Doctor after updates** (migrations + repairs)

---

## 1) Quick status snapshot

```bash
openclaw status --deep
openclaw health --json
```

If health is failing, don’t guess — run doctor.

```bash
openclaw doctor
```

---

## 2) Updates (safe path)

If you installed via npm/pnpm, you can update via npm OR via OpenClaw’s update
command.

Recommended:

```bash
openclaw update
# (it will usually restart the gateway; add --no-restart if you need)
```

After any update, run doctor to catch config migrations:

```bash
openclaw doctor
```

Headless/automation:

```bash
openclaw doctor --non-interactive
# or opt-in to repairs
openclaw doctor --repair --yes
```

---

## 3) One Gateway per host (recommended)

A common reliability footgun is accidentally starting a second Gateway instance
(which can cause port conflicts and channel/session weirdness).

Use the service lifecycle commands:

```bash
openclaw gateway install   # one-time
openclaw gateway status
openclaw gateway restart
```

Reference: https://docs.openclaw.ai/gateway/multiple-gateways

---

## 4) Telegram sanity checks

- Make sure you know the **numeric chat id** you’re delivering to (DM user id or
  group id like `-100…`).
- The message CLI requires **--target**:

```bash
openclaw message send --channel telegram --target "-1001234567890" --message "ping"
```

More: `docs/TELEGRAM_SETUP.md` and https://docs.openclaw.ai/channels/telegram

---

## 5) Typing indicators (optional tuning)

Reference: https://docs.openclaw.ai/concepts/typing-indicators

Recommended default (Telegram-friendly):

```json5
{
  agents: {
    defaults: {
      typingMode: "message",
      typingIntervalSeconds: 6,
    },
  },
}
```

---

## 6) Memory plugin (don’t break schema)

Memory is **Markdown on disk** + optional memory search. The default memory
plugin (memory-core) is bundled and is usually enabled by default.

Check what plugins are loaded:

```bash
openclaw plugins list
openclaw doctor
```

If you *do* need to force the memory plugin selection, use plugin **slots**:

```json5
{
  plugins: {
    slots: {
      memory: "memory-core", // or "none" to disable memory plugins
    },
  },
}
```

Reference: https://docs.openclaw.ai/plugin

---

