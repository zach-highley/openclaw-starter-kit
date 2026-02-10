# No AI Slop — Design Rules for AI-Built UIs

> If it looks like AI made it, it's wrong. Every UI your agent touches must pass human scrutiny.

## The AI Slop Checklist (if ANY are true, redesign)

- [ ] Rainbow color-coded sections (red for X, green for Y, blue for Z)
- [ ] Radial gradients or glowing borders
- [ ] `uppercase tracking-wide` or `tracking-widest` on more than one element per page
- [ ] More than 2 accent colors (pick ONE brand color + neutrals)
- [ ] "Digital gladiators" or any overwrought copy
- [ ] More than 6 nav items visible at once
- [ ] Every card having a different colored border
- [ ] Symmetric grid layouts that look procedurally generated
- [ ] Overuse of rounded-3xl, rounded-full on everything
- [ ] Emoji as the only visual hierarchy tool

## Design Principles

1. **Study real sites first**: Polymarket, Linear, Vercel, Apple, Stripe. Clean, minimal, data-forward.
2. **One accent color** + grayscale. That's it.
3. **Typography creates hierarchy** — not color. Use font size and weight.
4. **Generous whitespace**. Let things breathe. Negative space is design.
5. **Flat, subtle backgrounds**. No gradients unless intentional and tasteful.
6. **5-6 nav items max** visible. Rest goes in menus or contextual links.
7. **Mobile-first**. If it doesn't work on a phone, it doesn't work.
8. **Data forward**. Big numbers, clean tables, minimal decoration.
9. **Copy should be human**. Short, direct, no marketing fluff.
10. **Research before building**: Check Dribbble, Awwwards, real products. Never design in a vacuum.

## Why This Matters

AI coding agents (Codex, Claude, Copilot) have a default aesthetic: rainbow gradients, tracking-widest headers, glowing borders, 12-item navbars. It's immediately recognisable and it screams "nobody designed this."

Your agent builds UIs? Add these rules to SOUL.md. Review every frontend commit against this checklist. Kill slop on sight.

## Real Example

**Before (AI slop):** 12 nav items, rainbow color-coded sections (red/amber/emerald/sky/violet), radial gradients, uppercase tracking-widest headers, "Digital gladiators" copy, glowing borders on every card.

**After (clean):** 5 nav items (Home, Fights, Leaderboard, Play, Credits), single amber accent + grayscale, typography-driven hierarchy, generous whitespace, mobile hamburger menu, clean data tables.

Same app. Night and day difference.
