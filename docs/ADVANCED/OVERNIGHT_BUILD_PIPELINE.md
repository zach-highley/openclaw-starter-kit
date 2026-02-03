# Overnight Build Pipeline (Queue → Codex sub-agents → Results → Morning Telegram)

**Goal:** while the user sleeps, Codex should be chewing through a prioritized queue of build tasks, producing real code/doc changes in the main workspace, and logging outcomes for review the next morning.

This pipeline is implemented by:

- `state/overnight_queue.json` — the task queue (prioritized)
- `scripts/overnight_builder.py` — the runner/orchestrator
- `state/overnight_build_results.json` — durable results log (append-only history)

> This pipeline is intentionally **small, deterministic, and inspectable**. It does not “decide what to do”; it simply executes the queue.

---

## 1) Queue file: `state/overnight_queue.json`

### Minimal schema

```json
{
  "items": [
    {"id": "OB-001", "priority": 1, "type": "script", "spec": "Build X that does Y"},
    {"id": "OB-002", "priority": 2, "type": "feature", "spec": "Add Z to MyApp"}
  ]
}
```

### Fields

- `id` (string, required): Stable identifier for the work item.
- `priority` (number, required): Lower = earlier. Items are processed in ascending priority, then by input order.
- `type` (string, optional): Free-form categorization (e.g. `script`, `feature`, `docs`, `bugfix`).
- `spec` (string, required): The natural-language build specification.

### Optional fields (supported)

- `repo` (string): If set, indicates where the work should be performed.
  - Examples: `workspace` (your OpenClaw workspace), `repos/MyApp`.
- `notes` (string): Extra context.

### What happens to processed items?

`overnight_builder.py` **removes** completed items from the queue when it runs successfully (regardless of success/fail). The durable record is `state/overnight_build_results.json`.

If you want to re-run an item, re-add it (or bump its priority).

---

## 2) Codex availability gate: `state/codex_status.json`

Before spawning any Codex work, the pipeline checks `state/codex_status.json`.

Expected shape (loose):

```json
{
  "available": true,
  "exhausted": false,
  "note": "optional"
}
```

Rules:

- If `available` is `false` **or** `exhausted` is `true` → the pipeline will **not** run tasks.
- If the file is missing or malformed → treated as **not available** (fail closed).

This prevents burning cycles when Codex is rate-limited.

---

## 3) Execution model

### Concurrency

- Max **3 concurrent** tasks (configurable via `--max-concurrency`, default 3).

### Timeout

- Hard timeout **10 minutes per task** (600s, configurable via `--timeout-seconds`, default 600).
- If a task times out, it is recorded as `fail` with `error: timeout`.

### Where does Codex run?

The orchestrator uses OpenClaw’s CLI to run isolated agent turns:

- `openclaw agent --agent codex ...`

To make this work, `overnight_builder.py` will ensure there is a configured OpenClaw agent named `codex`:

- model: `openai-codex/gpt-5.2`
- workspace: `~/.openclaw/workspace` (same as `~/openclaw-workspace/`)

If the agent does not exist, the script will create it automatically.

---

## 4) Results log: `state/overnight_build_results.json`

The results file is written as a single JSON object:

```json
{
  "runs": [
    {
      "run_id": "2026-02-03T03:12:45Z",
      "task": {"id": "OB-001", "priority": 1, "type": "script", "spec": "..."},
      "status": "success",
      "started_at": "...",
      "finished_at": "...",
      "duration_seconds": 123.4,
      "files_changed": ["scripts/foo.py"],
      "commits_made": ["abcd1234 add foo"],
      "agent": "codex",
      "session_id": "overnight:OB-001",
      "model_report": {"success": true, "summary": "..."},
      "raw_reply": "(full agent text)"
    }
  ],
  "last_run_at": "..."
}
```

Notes:

- The script computes `files_changed` and `commits_made` by comparing git state before vs after each task.
- `model_report` is best-effort parsing of JSON embedded in the agent’s reply.

---

## 5) Telegram summary (morning report)

At the end of a run (or when invoked with `--send-summary`), the script sends a short Telegram summary using:

- `scripts/simple_telegram_notify.py`

This keeps Telegram delivery logic centralized.

---

## 6) How to run

### Run overnight builds now

```bash
python3 ~/openclaw-workspace/scripts/overnight_builder.py
```

### Dry run (no execution)

```bash
python3 ~/openclaw-workspace/scripts/overnight_builder.py --dry-run
```

### Send the latest summary again (no queue processing)

```bash
python3 ~/openclaw-workspace/scripts/overnight_builder.py --send-summary-only
```

---

## 7) Scheduling (recommended)

This repo already uses launchd for recurring jobs. The recommended pattern is:

- A nightly launchd job to run `overnight_builder.py` around bedtime.
- A morning launchd job to run `overnight_builder.py --send-summary-only`.

This separation guarantees that if the nightly run is interrupted (sleep / crash / restart), the morning report can still fire.

---

## 8) Operational safety & failure modes

- **Lock file**: `state/overnight_builder.lock` prevents concurrent overlapping runs.
- **Fail-closed Codex gate**: avoids accidental non-Codex runs.
- **Timeouts**: prevents a single task from stalling the entire night.
- **Auditability**: results are persisted to JSON and are tied to git commits.

---

## 9) Adding new items

Add an item with a unique id and a clear spec:

```json
{
  "id": "OB-003",
  "priority": 3,
  "type": "docs",
  "spec": "Write docs for the new dashboard API endpoints and include curl examples",
  "repo": "workspace"
}
```

Pro tip: Keep specs **small** (10–30 minutes human equivalent). Overnight is for lots of small wins.
