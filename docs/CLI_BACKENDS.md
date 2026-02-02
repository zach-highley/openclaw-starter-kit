# CLI Backends (Last-Resort Fallback)

OpenClaw can use **local AI CLIs** as a **text-only safety net** when hosted providers are down, rate-limited, or misbehaving.

Key properties (by design):
- **Tools are disabled** (no file/system/browser tool calls)
- **Text in → text out**
- Sessions still work (follow-ups stay coherent)

This makes CLI backends a great "it always answers" mode, but not a substitute for your normal tool-enabled agent.

## When to use

Use CLI backends as a **final fallback**:
- You prefer an answer (even if limited) over a hard failure
- You want to survive temporary provider outages without touching config

## Configuration (example)

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "claude-cli": {
          // If your gateway runs under launchd/systemd, PATH may be minimal.
          // Prefer absolute paths.
          command: "/opt/homebrew/bin/claude",
        },
      },

      model: {
        primary: "anthropic/claude-opus-4-5",
        fallbacks: [
          "openai-codex/gpt-5.2",
          "ollama/qwen2.5:14b",
          "claude-cli/opus-4.5", // last resort
        ],
      },

      models: {
        "anthropic/claude-opus-4-5": { alias: "Opus" },
        "claude-cli/opus-4.5": { alias: "Claude CLI (Fallback)" },
      },
    },
  },
}
```

## Gotchas

- If you use `agents.defaults.models` as an allowlist, you must include `claude-cli/...` models.
- If you need tools, CLI backend is the wrong mode. Use it only when reliability matters more than capability.

Official docs:
- https://docs.openclaw.ai/gateway/cli-backends
