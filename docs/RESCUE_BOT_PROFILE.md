# Rescue bot profile (optional, recommended for autonomy)

No uptime guarantees. Things break. Config mistakes happen. Bots go silent.

A **rescue bot** is a second, fully-isolated Gateway instance on the same host.
When the primary bot is down (or its config is schema-invalid and it won't start),
you can still message the rescue bot to debug and recover.

This follows the official OpenClaw pattern for multiple Gateways:
https://docs.openclaw.ai/gateway/multiple-gateways

## When you need this
- You applied a config change and the Gateway refuses to start (strict schema validation).
- Your primary Gateway is down and you cannot reach the local dashboard.
- You need a safe “out-of-band” path to restart/relink without touching the broken instance.

## Rules (non-negotiable)
Multiple Gateways only work if they are **fully isolated**:
- separate **profile** (recommended)
- separate **config path**
- separate **state dir**
- separate **workspace**
- separate **base port** (and derived ports)

If you share any of these, you will create race conditions and port conflicts.

## Setup (recommended: profiles)

### 1) Onboard rescue profile

```bash
openclaw --profile rescue onboard
```

### 2) Pick a safe port
Leave at least **20 ports** between instances so derived ports never collide.

- main: 18789 (default)
- rescue: 19001 (safe default)

### 3) Start rescue gateway

```bash
openclaw --profile rescue gateway --port 19001
```

### 4) Install as a service (recommended)

```bash
openclaw --profile rescue gateway install
```

## Daily use

- Check both:
```bash
openclaw --profile main status
openclaw --profile rescue status
```

- If main is broken, use rescue to:
  - inspect logs
  - run `openclaw doctor`
  - apply a fixed config (via `config.patch` / UI)
  - restart the main service

## What NOT to do
- Do not point both instances at the same Chrome/CDP ports.
- Do not share `OPENCLAW_STATE_DIR`.
- Do not share `OPENCLAW_CONFIG_PATH`.
- Do not share `agents.defaults.workspace`.

## Safety note
A rescue bot increases complexity slightly, but it gives you a reliable control plane
when the primary instance is dead. For autonomous assistants, this is usually worth it.
