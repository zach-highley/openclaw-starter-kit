# Security Hardening — Battle-Tested Defaults

This repo is public. Your workspace should assume attackers can read **everything** in git.

## 1) Never hardcode secrets

Bad:
- bot tokens in scripts
- API keys in `.py` / `.sh`
- “temporary” secrets committed to git

Good:
- load secrets from OpenClaw config, environment variables, or an encrypted store
- treat logs as sensitive (they often contain URLs, IDs, partial payloads)

## 2) Keep secrets out of git (and git history)

### .gitignore must cover
At minimum:
- `__pycache__/`
- `.venv/`
- `.env`
- `secrets/`
- `logs/`
- `*.log`

If you ever commit a secret:
- assume it is compromised
- rotate it immediately
- don’t just “delete the file” — git history still contains it

## 3) Weekly security scan

Make security scanning a habit (automated is best):
- run a weekly audit
- scan for common secret patterns
- review recent diffs

See:
- `docs/WEEKLY_AUDIT_GUIDE.md`

## 4) Least privilege

- run the gateway with the minimum OS permissions it needs
- only enable tools you actually use
- sandbox non-main agents when possible (see OpenClaw docs)

## 5) “Public repo” sanity check

Before pushing, run a targeted search for personal data and tokens.
This project’s rebrand sprint uses a strict grep (see `SPRINT_REBRAND_SPEC.md`).

Also do a broad sweep:
```bash
rg -n "(api[_-]?key|token|secret|password|BEGIN [A-Z ]+PRIVATE KEY)" .
```
