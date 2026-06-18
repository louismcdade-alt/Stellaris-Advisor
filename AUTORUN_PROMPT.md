# Stellaris Advisor — Autonomous Work Session

You are working unattended on the Stellaris Advisor (part of the Stellaris Live AI
project). No human is watching this cycle, so be conservative: make steady, verifiable
progress and never guess on anything that needs a human decision.

## Each cycle, do exactly this:
1. Read CLAUDE.md, README, and BACKLOG.md to load current state and conventions.
2. Pick the single highest-value unblocked task from BACKLOG.md. Prefer tasks that are
   small, testable, and move the Advisor toward working end-to-end over speculative work.
3. Implement it in the smallest reasonable change.
4. Verify: run the build and the test suite. If there are no tests for what you changed,
   add one.
5. If green, commit with a clear message: `auto: <what changed and why>`.
   Do NOT push and do NOT touch the main branch — work on the `auto-work` branch only.
6. Append a dated entry to PROGRESS.md: what you did, what you verified, what's next.
7. Move/check off the task in BACKLOG.md.

## Hard rules (stop and write to NEEDS_REVIEW.md instead of acting):
- Anything ambiguous, architectural, or irreversible (schema changes, deleting data,
  changing public APIs, new dependencies with licensing questions).
- Anything touching secrets, API keys, or credentials — never read, print, or commit them.
- If the build/tests were already failing when you started, fix that FIRST or log it and stop.
- If you can't make a clean, verified change, revert your work this cycle and log why.

## Style:
- One coherent task per cycle. No half-finished features left uncommitted.
- Leave the repo in a green, committed state at the end of every cycle.
- Keep PROGRESS.md honest — note failures and dead ends, not just wins.
