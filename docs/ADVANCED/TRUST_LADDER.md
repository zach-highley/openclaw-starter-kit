# Trust Ladder (Advanced)

A Trust Ladder is a simple policy system that defines what the assistant can do **without asking**, and what requires confirmation.

The point is safety *and* speed.

---

## Level 1 — Cautious
**Behavior:** Ask before almost everything.

**Use when:** new setup, untrusted environment, or after an incident.

Allowed without asking:
- Read-only checks (status, logs, diffs)
- Drafting plans, docs, and messages (not sending)

Requires confirmation:
- Any file edits
- Any outbound message
- Any automation/scheduling

---

## Level 2 — Safe
**Behavior:** Execute safe ops; ask before medium-risk actions.

Allowed without asking:
- Safe file edits in the workspace (docs, templates)
- Non-destructive scripts

Requires confirmation:
- Installing packages
- Editing OpenClaw config
- Sending messages to real recipients

---

## Level 3 — Trusted (default for many)
**Behavior:** Execute most actions and report after.

Allowed without asking:
- Routine maintenance
- Fixing obvious bugs
- Committing to private repos

Requires confirmation:
- Public repo pushes
- Deletions that could lose data
- Financial transactions
- External contacts

---

## Level 4 — Autonomous
**Behavior:** Run self-directed workstreams. Only ask on irreversible risks.

Allowed without asking:
- Starting new work based on the task queue
- Running overnight builds
- Sending progress updates

Still requires confirmation:
- Public posts
- Sending emails to external parties
- Payments / purchases
- Destructive deletes outside clearly safe temp/log cleanup

---

## Level 5 — Night Shift
**Behavior:** Same as Level 4, but the assistant proactively creates and executes new tasks while the user sleeps.

Guardrails:
- No spending.
- No external outreach.
- No irreversible data loss.
- Morning summary is mandatory.

---

## Implementation tip
Document your current level in `AGENTS.md` or `SECURITY.md`, and make it explicit how to change levels.
