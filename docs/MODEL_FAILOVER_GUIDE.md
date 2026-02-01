# Model Failover & Auth Rotation Guide

How to set up reliable model failover in OpenClaw so your bot doesn't die when one account hits rate limits.

## Two Levels of Failover

OpenClaw handles failures in two stages:

### 1. Auth Profile Rotation (Same Provider)
If you have multiple accounts for the same provider (e.g., two Claude MAX subscriptions), OpenClaw rotates between them automatically when one hits rate limits.

**This is the most useful failover for subscription users.** If account A gets rate-limited, OpenClaw switches to account B within the same message — the user never notices.

### 2. Model Fallback (Different Provider)
If ALL profiles for a provider fail, OpenClaw moves to the next model in `agents.defaults.model.fallbacks`.

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

### How to add a second account
1. Run `openclaw setup` or `openclaw configure` for the second account
2. Profiles auto-appear in `~/.openclaw/agents/<id>/agent/auth-profiles.json`
3. Set `auth.order` in your config to control rotation priority

## Setup: Model Fallback Chain

```json5
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-5",
        "fallbacks": [
          "anthropic/claude-sonnet-4",
          "openai/gpt-4o"
        ]
      }
    }
  }
}
```

Fallback triggers when ALL profiles for the primary provider fail. Not on every error — only on auth failures, rate limits, and timeouts that exhausted profile rotation.

## Recommended Patterns

### Pattern 1: Single subscription with emergency fallback chain
```json5
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-5",
        "fallbacks": [
          "anthropic/claude-sonnet-4",     // same provider, cheaper model
          "nvidia-nim/moonshotai/kimi-k2.5", // free tier emergency
          "ollama/qwen2.5:14b"             // local, always available
        ]
      }
    }
  }
}
```
Failover only triggers when the provider returns rate limit errors and ALL profiles are in cooldown. Your primary model stays active until it physically can't respond. This means the "shittier" models in the chain only activate in genuine emergencies.

### Pattern 2: Multi-provider fallback chain
```json5
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-5",
        "fallbacks": [
          "openai/gpt-4o",
          "google/gemini-2.5-pro"
        ]
      }
    }
  }
}
```

### Pattern 3: Coding-specific failover (subagents)
Use model routing scripts to check availability before spawning:
```bash
# Check if Codex is available before spawning a coding subagent
python3 scripts/model_routing_check.py --task coding --json
```
If primary coding model is unavailable, fall back to next best (Claude Code), or build directly in main session. Never fall back to models you don't trust for code.

## Cooldown Behavior

When a profile fails:
| Attempt | Cooldown |
|---------|----------|
| 1st | 1 minute |
| 2nd | 5 minutes |
| 3rd | 25 minutes |
| 4th+ | 1 hour (cap) |

Billing failures (insufficient credits) get longer cooldowns: 5 hours, doubling, capping at 24 hours.

## Monitoring Failover

Build a usage monitor that tracks:
- Which profile is currently active
- Rate limit hits per profile
- Weekly usage percentage per provider
- Time until rate limit reset

This prevents surprises. If you can see you're at 90% of weekly usage on Tuesday, you know to throttle — not panic when it runs out Wednesday.

## Key Insight: Subscription Users

If you have multiple accounts on the same provider, **auth profile rotation gives you more runway before failover kicks in.** Rate limits are per-account, so two accounts = 2x throughput before degradation. But even with a single account, OpenClaw's cooldown + exponential backoff means your primary model gets every possible chance before falling to a backup.

The failover chain is your safety net, not your daily driver. Keep your best model as primary and let OpenClaw's built-in retry logic handle transient rate limits. The fallbacks are for when things are genuinely exhausted.

## Reference
- [Model Failover docs](https://docs.openclaw.ai/concepts/model-failover)
- [Auth & OAuth](https://docs.openclaw.ai/concepts/oauth)
- [Gateway Configuration](https://docs.openclaw.ai/gateway/configuration)
