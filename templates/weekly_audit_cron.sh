#!/usr/bin/env bash
set -euo pipefail

# Weekly audit template (cron/launchd target)
# Run from your OpenClaw workspace root.

cd "${OPENCLAW_WORKSPACE:-$(cd "$(dirname "$0")/.." && pwd)}"

echo "[weekly-audit] $(date -Iseconds) starting in $(pwd)"

# 1) Basic secret scan (customize for your environment)
rg -n "(api[_-]?key|token|secret|password|BEGIN [A-Z ]+PRIVATE KEY)" . || true

# 2) Orphan script scan
for f in scripts/*; do
  b=$(basename "$f")
  if ! rg -n "\b$b\b" . >/dev/null; then
    echo "[weekly-audit] UNREFERENCED: $b"
  fi
done

# 3) Parse check (python)
python3 - <<'PY'
import ast
from pathlib import Path
bad=[]
for p in Path('scripts').glob('*.py'):
    try:
        ast.parse(p.read_text())
    except Exception as e:
        bad.append((str(p), str(e)))
if bad:
    raise SystemExit("\n".join([f"{p}: {e}" for p,e in bad]))
print("[weekly-audit] python scripts parse OK")
PY

echo "[weekly-audit] done"
