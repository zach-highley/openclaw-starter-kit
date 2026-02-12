# PRD + Checklist (Ralph Loop)

## Goal (JTBD)
- 

## Scope
### In
- 

### Out (explicitly not doing)
- 

## Acceptance Criteria (Checklist)
- [ ] 
- [ ] 
- [ ] 

## Files / Areas
- 

## Constraints
- No secrets / credentials changes
- No destructive operations without human sanity-check
- Keep changes minimal and MECE

## Backpressure (must run each iteration)
- [ ] `git status --porcelain` is clean except intended changes
- [ ] `git diff` reviewed
- [ ] `npm test` / `pnpm test` / `swift test` (project-specific)
- [ ] `npm run lint` (if applicable)

## Completion Sentinel
- Add `STATUS: COMPLETE` to `IMPLEMENTATION_PLAN.md` when all checklist items are done.
