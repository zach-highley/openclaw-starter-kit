# Gmail legacy → MECE label migration (runbook)

Script: `scripts/email_label_migrate_mece.py`

## What this script does (and does NOT do)

✅ Adds MECE labels (creates missing target labels if needed)

✅ Migrates **threads** from legacy labels to MECE labels

✅ Removes the legacy label **from threads** (after successfully adding the new label)

✅ Supports legacy labels with **>500 threads** (Gmail search pagination)

✅ Resumable with checkpointing (safe to stop/restart)

❌ Does **not** delete any Gmail labels (label definitions)

❌ Does **not** delete messages/threads


## Why pagination is tricky (and how we handle it)

Gmail pagination (`nextPageToken`) is not safe if you modify labels while paging the same query, because the result set changes.

This script uses a **two-phase approach per legacy label**:

1. **Inventory phase (read-only)**: page through all matching threads and write thread IDs to a local inventory file.
2. **Apply phase (write)**: walk the inventory file and apply label changes.

This avoids skipping threads and makes retries idempotent.


## Files written

All files live under `~/openclaw-workspace/state/email_router/`:

- Audit log (JSONL):
  - `label-migrate-YYYY-MM-DD.jsonl`

- Per-label checkpoint files:
  - `label_migrate_checkpoints/<account>/<legacy>.json`

- Per-label inventory files (thread ids):
  - `label_migrate_inventory/<account>/<legacy>.txt`


## Recommended workflow

### 0) Snapshot metrics (before)

```bash
python3 scripts/email_legacy_label_audit.py \
  --accounts [EMAIL] \
  --json-out state/email_router/legacy-label-audit-before.json
```

Identify large legacy labels (e.g. `threadsTotal > 500`) from the audit output.

### 1) Dry run, scoped to a large label

```bash
python3 scripts/email_label_migrate_mece.py \
  --dry-run \
  --accounts [EMAIL] \
  --only-legacy-labels "Misc,Receipts" \
  --oldest
```

This will build inventories and write a detailed audit log, but will not modify Gmail.

### 2) Apply (resumable)

```bash
python3 scripts/email_label_migrate_mece.py \
  --apply \
  --accounts [EMAIL] \
  --only-legacy-labels "Misc,Receipts" \
  --oldest
```

### 3) Stop/restart safely

Just re-run the same command. By default, it resumes from the checkpoint.

To force a fresh run (discard local inventory/checkpoint for that label pass):

```bash
python3 scripts/email_label_migrate_mece.py --apply --no-resume ...
```

### 4) Snapshot metrics (after)

```bash
python3 scripts/email_legacy_label_audit.py \
  --accounts [EMAIL] \
  --json-out state/email_router/legacy-label-audit-after.json
```


## Safety knobs

- `--max-per-label N`
  - Limits work per legacy label (useful while testing). `0` (default) = unlimited.

- `--page-size N`
  - Defaults to `500` (max recommended by Gmail). Lower if you hit rate limits.

- `--only-legacy-labels "A,B,C"`
  - Strongly recommended for first runs on large accounts.


## Expected verification

For each processed legacy label, the script performs a small check after applying:

- `gog gmail search label:"<legacy>" --max 1`

If it returns 0 threads, that label is drained at that moment.

If it returns >0 threads, run a second pass (`--passes 2`) or just re-run later (new mail can re-add labels depending on filters).
