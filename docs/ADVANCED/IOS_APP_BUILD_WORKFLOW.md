# iOS App Building Workflow (OpenClaw + Codex)

This guide describes a **repeatable** workflow for building and maintaining iOS apps with OpenClaw, using:
- a **planner model** for architecture + task breakdown
- a **coding model** (Codex) for implementation
- optional CI monitoring (Xcode Cloud)

It is intentionally **repo-agnostic** and **secret-free**.

---

## 1) The Operating Model

### Roles
- **Planner (Opus or equivalent):**
  - converts goals → specs
  - chooses the smallest next shippable slice
  - writes acceptance criteria
- **Coder (Codex):**
  - implements code changes
  - runs build/test commands
  - writes incremental commits
- **Orchestrator (you):**
  - ensures the task lands cleanly in git
  - updates docs + changelog
  - keeps the system MECE (no duplicate scripts/pipelines)

### The 8-step “hybrid” loop
1. Define scope (one slice)
2. Write a short spec (10–30 min human-equivalent)
3. Create a branch
4. Codex implements
5. Run `xcodebuild` / tests
6. Open PR
7. Review + merge
8. Update docs/runbooks

---

## 2) Project Registry Pattern (Multi-App)

If you run multiple apps, keep a single registry so your automation can route work correctly.

Example: `state/app_registry.json`

```json
{
  "apps": {
    "my_app": {
      "name": "My App",
      "platform": "ios",
      "repo": "/path/to/your/repo",
      "mainBranch": "main",
      "build": {
        "type": "xcodebuild",
        "command": "xcodebuild -project MyApp.xcodeproj -scheme MyApp -destination 'generic/platform=iOS' -configuration Release -quiet build"
      },
      "ci": {
        "type": "xcode-cloud",
        "notes": "Optional. Use Xcode Cloud if you want CI-driven build monitoring."
      },
      "monitoring": {
        "type": "sentry",
        "org": "YOUR_SENTRY_ORG",
        "project": "YOUR_SENTRY_PROJECT"
      }
    }
  }
}
```

Notes:
- Do **not** store DSNs/tokens in git. Use env vars or your OpenClaw credential store.
- The goal is routing + repeatability, not perfect metadata.

---

## 3) What to Ask Codex to Do (prompt patterns)

Good tasks for Codex:
- implement a feature from a concrete spec
- fix a build error from `xcodebuild` output
- refactor with a clearly defined “done” condition

Bad tasks for Codex (give to planner first):
- vague “make it better”
- product strategy
- UI/UX design without mocks

---

## 4) CI / Build Monitoring (Optional)

If you use Xcode Cloud:
- treat build failures as **work items**
- capture:
  - failing step
  - error logs
  - last known good commit
- have Codex propose and implement the smallest fix

---

## 5) Safety + Public Repo Hygiene

- Never commit private app repos, signing keys, `.p8` files, provisioning profiles, or `.env` files.
- Treat any accidental secret commit as compromised: rotate immediately.
- Prefer documenting *patterns* (registry shape, commands, workflow), not internal URLs.
