# ADVANCED_PLAYBOOK.md — Production Autonomy Patterns

This doc is a grab bag of patterns that worked in a real OpenClaw setup.

It is not official guidance. Cross-check everything against https://docs.openclaw.ai.

---

## 1) Heartbeat-first operations (Cron for reports)

**Goal:** keep the system simple, MECE, and avoid cron spam.

- **Heartbeat** = operational loop (triage + decide + act + report)
- **Cron** = scheduled recaps / maintenance, where you want a guaranteed delivery

Practical split:
- Heartbeat: email/iMessage/X triage, task queue progress, opportunistic work starts
- Cron: twice-daily summaries, weekly reviews, daily maintenance (`openclaw doctor --fix`)

---

## 2) “Proof-of-work” heartbeats (don’t be silent)

A common failure mode is thinking heartbeats are broken when they are actually firing but **not delivering any visible message**.

Recommended pattern:
- Always start with a clear indicator, e.g. `💓 Heartbeat 10:34 AM`
- Include 3–6 short “proof lines”:
  - Email: triage ran (N inboxes)
  - iMessage: checked
  - X: mentions checked
  - Calendar: next event
  - Tasks: what’s in progress

This gives humans confidence the loop is running.

---

## 3) Delivery gotcha: `HEARTBEAT_OK` can be invisible

Depending on how your system is wired, replying `HEARTBEAT_OK` can behave like an ack and may be dropped/ignored by the delivery layer.

If your goal is: “I want a visible pulse in Telegram”, send an explicit message instead of `HEARTBEAT_OK`.

---

## 4) Nat Eliason review pattern (actionable links)

A powerful reporting style for autonomous systems:

- Include **one-click review links**:
  - TestFlight / Expo / build artifact
  - Vercel preview deployment
  - GitHub PR
  - Product draft link (Gumroad, Stripe, etc.)

- Include a short list of **Upgrades to Review** (3–5 bullets)
  - Tag each as:
    - `[safe auto-apply]`
    - `[needs human sanity-check]`

This keeps the human in control without blocking execution.

---

## 5) MECE guardrails

If you feel the system getting “clever” again:

- One gateway (launchd KeepAlive=true)
- One daily maintenance job
- Heartbeat for ops
- Cron for summaries

Kill overlapping crons first. Complexity is the silent killer.
