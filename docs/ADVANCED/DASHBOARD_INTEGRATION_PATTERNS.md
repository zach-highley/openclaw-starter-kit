# Dashboard Integration Patterns (Advanced)

Goal: connect OpenClaw’s on-disk state (`state/`, `memory/`) to a personal dashboard without leaking secrets or coupling everything together.

---

## Principles

1. **Keep it MECE**
   - OpenClaw owns *state + automation*.
   - The dashboard owns *visualization + UI*.
   - Integration scripts only translate and push.

2. **Push small, structured payloads**
   - Prefer a single JSON payload with:
     - timestamps
     - current focus / next tasks
     - key counters

3. **No secrets in git**
   - API URLs and tokens must be env vars.

---

## Recommended data sources

- `state/current_work.json` (or your equivalent)
- `state/work_metrics.json`
- daily memory: `memory/YYYY-MM-DD.md` (optional; consider summarizing)

---

## Transport options

- HTTP POST to your dashboard API (most common)
- Write a JSON file to a shared folder and let the dashboard read it
- Message-based (Telegram/Discord) for “human-first” status, dashboard is secondary

---

## Minimal implementation

Use the template script:
- `scripts/advanced/dashboard_push_template.py`

Configure:
- `DASHBOARD_API_URL`
- `DASHBOARD_API_TOKEN`

---

## Anti-patterns

- Hardcoding tokens or private URLs in scripts.
- Parsing huge logs on every run.
- Multiple scripts pushing overlapping dashboard payloads.

---

## Suggested cadence

- Hourly: push quick status
- Morning + evening: push richer summaries
- After overnight builds: push a results summary
