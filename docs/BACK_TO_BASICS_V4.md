# Back to Basics v4.0

A stabilization-first release for autonomous OpenClaw setups.

## Why v4.0

When systems get noisy, the fix is rarely more automation. The fix is usually:

1. simplify triggers,
2. reduce overlapping loops,
3. restore one clear operational baseline,
4. rebuild deliberately.

This release codifies that recovery pattern.

## Core Operating Pattern

- **Boot hooks inert by default during incident recovery**
- **Heartbeat + Cron must be intentionally scoped, not sprawling**
- **One source of truth for commitments (`TODO.md`)**
- **Memory hygiene daily (`memory/YYYY-MM-DD.md` + `MEMORY.md`)**
- **Config changes via `gateway config.patch` only**

## The Rescue Pair Pattern (Primary + Backup Bot)

For high-uptime personal setups:

- Keep a **primary bot** for normal operation.
- Keep a **backup/rescue bot** with a lean profile.
- Give each bot a clear role and avoid overlap.
- Use SSH/Tailscale for cross-checks and recovery when one side drifts.

This prevents single-point personality/config drift and enables quick stabilization.

## Docs Pass Applied (OpenClaw Concepts)

A full pass was run over all current `/concepts/*` pages in official docs and integrated as guardrails in templates.

### Key integrations from concepts docs

- **Agent/session architecture matters**: direct chats vs grouped session boundaries are explicit.
- **Context and compaction are first-class**: avoid giant prompt files and stale context bloat.
- **Queue/retry/streaming are operational controls**: tune these before writing custom glue.
- **Memory is a workflow, not a feature toggle**: daily logs + curated long-term memory.
- **Timezone and formatting discipline**: avoid delivery regressions on chat surfaces.

## Practical v4.0 Rules

- Keep messaging dense and readable for Telegram (single rich message by default, two max when needed).
- Treat model-regression claims as a hypothesis. Verify prompt quality, context pressure, and tier first.
- Use terminal-first coding loops for substantial work; avoid fragile multi-layer orchestration.
- After every feature: run a small refactor pass, edge-case tests, and docs update.

## Migration Checklist

- [ ] Add `TODO.md` if missing
- [ ] Add/refresh `SYSTEM-ARCHITECTURE.md`
- [ ] Refresh `HEARTBEAT.md` with a minimal health checklist
- [ ] Ensure `hooks` are intentionally set (not accidental defaults)
- [ ] Audit cron list for MECE and remove overlap
- [ ] Verify `agents.defaults` contains heartbeat/context/compaction settings

## Versioning Note

This is a **process architecture release**. It changes how you run OpenClaw day-to-day more than any single code path.
