# Progress log — Stellaris Advisor autonomous work

## 2026-06-18
- **Did:** Added the project's first pytest suite (BACKLOG item #1). New
  `requirements-dev.txt` (pytest only, dev-only — `advisor/` stays stdlib-only).
  New `tests/test_clausewitz.py` (parse round-trips: scalars, booleans,
  duplicate keys -> list, nested blocks, bare arrays; `extract_block` brace
  matching incl. nested braces and a not-found case), `tests/test_analyze.py`
  (`analyze_economy` critical-runway alert + stable->"good"; `analyze_military`
  outgunned->warning + strongest->good, via synthetic snapshot dicts),
  `tests/test_fleet.py` (`fleet.recommend` with no warships, budget scaling
  from an existing composition, and tier unlock via researched tech).
- **Verified:** `python -m pytest -v` — 15 passed, 0 failed. No production
  code touched, so no risk to `app.py`/`run.py` behavior.
- **Note:** `gamedata.ship_sizes()` returns `{}` when no Stellaris install is
  found, so `fleet.recommend()` cleanly exercises its built-in `FALLBACK_SLOT`/
  `FALLBACK_TECH` constants under pytest with no mocking needed — confirmed
  this while reading `advisor/gamedata.py` before writing the fleet tests.
- **Next:** BACKLOG item #2 (validate.py: check civic <-> ethics/authority
  requirements) is the next highest-value unblocked task.
