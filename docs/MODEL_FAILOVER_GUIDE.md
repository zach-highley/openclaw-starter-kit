# Model Failover & Auth Rotation Guide

How to set up reliable model failover in OpenClaw so your bot never dies when one account hits rate limits.

## Two Levels of Failover

OpenClaw handles failures in two stages:

### 1. Auth Profile Rotation (Same Provider)
If you have multiple accounts for the same provider (example: two Claude MAX subscriptions), OpenClaw rotates between them when one hits rate limits.

This is the highest-quality failover because the user often never notices.

### 2. Model Fallback (Different Provider)
If **all** auth profiles for a provider fail (cooldown, rate limit, billing, auth), OpenClaw moves to the next model in `agents.defaults.model.fallbacks`.

## Setup: Auth Profile Rotation

### Multiple accounts on same provider
```json5
{
  "auth": {
    "profiles": {
      "anthropic:account-a": { "provider": "anthropic" },
      "anthropic:account-b": { "provider": "anthropic" }
    },
    "order": {
      "anthropic": ["anthropic:account-a", "anthropic:account-b"]
    }
  }
}
```

OpenClaw uses round-robin with session stickiness:
- Pins one profile per session (keeps provider caches warm)
- Rotates to next profile on rate limits/auth failures
- Cooldowns use exponential backoff: 1min → 5min → 25min → 1hr cap

## Setup: Model Fallback Chain (Cross-Provider)

This starter-kit default is designed to avoid the "locked into Anthropic cooldown" failure mode.

```json5
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-5",
        "fallbacks": [
          "openai-codex/gpt-5.2",
          "google-gemini-cli/gemini-3-pro-preview",
          "nvidia-nim/moonshotai/kimi-k2.5",
          "ollama/qwen2.5:14b"
        ]
      }
    }
  }
}
```

Fallback triggers when **all profiles for the primary provider** fail. It should not trigger on occasional transient errors.

## Recommended Patterns

### Pattern 1: Best quality with safety net (most users)
- Primary: Opus
- Rotate multiple Anthropic profiles if you have them
- Fallback cross-provider only when truly necessary

### Pattern 2: Coding subagents can have their own chain

```json5
{
  "agents": {
    "defaults": {
      "subagents": {
        "model": {
          "primary": "openai-codex/gpt-5.2",
          "fallbacks": [
            "google-gemini-cli/gemini-3-pro-preview",
            "nvidia-nim/moonshotai/kimi-k2.5",
            "ollama/qwen2.5:14b"
          ]
        }
      }
    }
  }
}
```

## Cooldown Behavior

When a profile fails:

| Attempt | Cooldown |
|---------|----------|
| 1st | 1 minute |
| 2nd | 5 minutes |
| 3rd | 25 minutes |
| 4th+ | 1 hour (cap) |

Billing failures (insufficient credits) typically get longer cooldowns.

## Monitoring Failover

Your usage monitor should track:
- which provider/profile is active
- rate limit hits per provider
- weekly usage percentage per provider
- time until next reset

The goal is to degrade gracefully, not to surprise you.

## Reference
- https://docs.openclaw.ai/concepts/model-failover
- https://docs.openclaw.ai/concepts/oauth
- https://docs.openclaw.ai/gateway/configuration
