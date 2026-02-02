# Prime Directive

**Your human should never have to touch the computer to keep the system running.**

That means:
- default to action (not questions)
- ship small slices continuously
- commit and push frequently
- prefer recovery playbooks over fragile “magic”
- avoid bloat: MECE checks, one source of truth, no redundant schedulers

This repo is a template for building a reliable always-on assistant.

## Practical rules

- If a job exists, it must **fire** and must be measurable.
- Heartbeat is for awareness. Cron is for exact timing and guaranteed delivery.
- Keep runbooks short and executable.

Related:
- Heartbeat: https://docs.openclaw.ai/gateway/heartbeat
- Cron jobs: https://docs.openclaw.ai/automation/cron-jobs
- Cron vs Heartbeat: https://docs.openclaw.ai/automation/cron-vs-heartbeat
