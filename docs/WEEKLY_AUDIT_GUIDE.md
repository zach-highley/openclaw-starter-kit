# Weekly Audit Guide — Learn From Failures Automatically

A self-healing system needs a feedback loop.
The weekly audit is that loop: it prevents “workspace entropy” (stale scripts, duplicated docs, zombie schedules, leaked secrets) from slowly killing uptime.

## What to audit (MECE checklist)

### 1) Scheduled jobs
- list cron/launchd jobs
- detect duplicates
- detect “LLM calls on a schedule” (expensive) and migrate to scripts

### 2) Scripts
- how many scripts exist?
- which are actually used?
- which are dead or redundant?

### 3) State files
- are there orphaned state files?
- is any state growing without bound?

### 4) Docs
- do docs still match reality?
- are there duplicate guides?

### 5) Security
- search for tokens / secrets
- ensure `.gitignore` covers logs/caches

---

## Useful one-liners

Run from your workspace root.

### Find scripts that are never referenced
```bash
# lists scripts/* that aren't referenced anywhere in the repo
for f in scripts/*; do
  b=$(basename "$f")
  if ! rg -n "\b$b\b" . >/dev/null; then
    echo "UNREFERENCED: $b"
  fi
done
```

### Find references to removed/renamed scripts
```bash
rg -n "scripts/(auto_update|auto_cleanup|build_monitor|system_monitor)" .
```

### Fast secret scan (starter)
```bash
rg -n "token|api_key|apikey|secret|password" .
```

### Python parse sanity
```bash
python3 - <<'PY'
import ast
from pathlib import Path
bad=[]
for p in Path('scripts').glob('*.py'):
  try:
    ast.parse(p.read_text())
  except Exception as e:
    bad.append((str(p), str(e)))
print('OK' if not bad else 'BAD')
for p,e in bad:
  print(p, e)
PY
```

---

## A simple weekly audit cron template

This project includes a template you can adapt:
- `templates/weekly_audit_cron.sh`

Suggestion:
- run it weekly
- send yourself a summary message (via your preferred channel)
- keep it *script-based* (no heartbeats unless you truly need LLM reasoning)

---

## Auto-fix mode (recommended)

The audit should be allowed to do safe, mechanical fixes:
- remove caches
- prune logs
- reformat known files
- report duplicates

But avoid auto-fixing anything that could cause data loss unless you’re confident and have backups.
