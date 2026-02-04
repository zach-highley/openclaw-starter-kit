# PROJECT_REGISTRY.md — What Your Assistant Tracks

A simple but critical pattern: write down the *set of projects your assistant is allowed to operate on*.

## Why
Without a project registry, agents drift:
- they guess where code lives
- they operate on the wrong repo
- they can’t generate one-click review links

## Minimal schema
For each project, capture:
- repo/path
- what “success” looks like
- how bugs arrive (Sentry/Expo/webhook)
- what links the human needs (preview/PR/build)

## Example projects
- your assistant workspace/config repo
- your primary app repo
- your personal dashboard repo
- your product/docs repo

## Nat Eliason pattern (next-level)
If you have an Expo app:
- wire Expo dev server notifications
- when the human finds a bug, the agent gets the alert and starts fixing immediately

Pair with:
- PRD + checklist
- Codex CLI full-auto loops
- one-click review links
