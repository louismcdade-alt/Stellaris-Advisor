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

## 2026-06-18 (cycle 2)
- **Did:** Implemented BACKLOG item #2 — `validate_build` now flags civics
  whose ethic gate conflicts with the build's ethics, not just authority.
  Discovered while reading the installed civic files that the current patch
  no longer uses the `has_ethic = ethic_x` syntax the backlog text assumed;
  civics now gate ethics via `ethics = { OR = { value = ethic_x } }` (need
  any of) and `ethics = { NOT/NOR = { value = ethic_x } }` (exclude). Adapted
  the implementation to the format actually present in the install rather
  than the stale syntax, per CLAUDE.md's "read the game, don't hard-code it."
  Added `advisor/validate.py`: `_ethic_requirements` (parses a civic block's
  `ethics=` sub-blocks into required-any/excluded ethic id sets, discarding
  the universal-and-redundant gestalt exclusion), `_build_ethic_ids` (maps a
  build's human-readable ethic labels like "Fanatic Materialist" to ethic ids
  — hard-coded small fixed mapping, same precedent as `profile.py`'s ethic
  label table, since the 8 base ethics are not DLC-dependent), `_ethic_ok`,
  and wired them into `validate_build`'s civic loop (checked only against
  the id variant(s) actually selectable for the build's authority kind).
  New `tests/test_validate.py` (5 tests, pure parsing logic, no install
  needed) covering OR->required, NOR->excluded, gestalt-noise discarding,
  label->id mapping with Fanatic, and the required/excluded gate logic.
- **Verified:** `python -m pytest -v` — 20 passed, 0 failed. `python
  audit_builds.py` against the real installed Stellaris files — still 0
  issues across all 12 shipped builds. Manually confirmed the check actually
  catches a bad pairing: an Egalitarian/Xenophile build given "Imperial Cult"
  (which needs Authoritarian or Spiritualist) is correctly flagged; the same
  civic on an Authoritarian/Militarist build is not.
- **Next:** BACKLOG item #3 (analyze.py: species-trait-aware economy advice)
  is the next highest-value unblocked task.

## 2026-06-18 (cycle 3)
- **Did:** Implemented BACKLOG item #3 — `analyze_species(snap)` in
  `advisor/analyze.py`, wired into `analyze()` right after `analyze_economy`.
  Maps founder-species traits to one-line tips via a small fixed
  `SPECIES_TRAIT_TIPS` table: `trait_intelligent` -> research-jobs tip,
  `trait_agrarian` -> farming districts, `trait_industrious` -> mineral
  build, `trait_thrifty` -> energy jobs, `trait_charismatic` -> envoys/
  diplomacy. Reused `EmpireProfile.traits` (already parsed from
  `identity.species_traits` by `profile.py`) rather than re-reading the raw
  snapshot field. Traits not in the table produce no advice, matching the
  backlog's "done when" bar.
- **Verified:** `python -m pytest -v` — 22 passed (2 new: mapped trait
  produces exactly one research-category tip; unmapped traits yield
  nothing). Manual smoke test of `analyze(snap)` end-to-end with a synthetic
  snapshot containing `trait_intelligent` confirmed the new tip appears
  alongside the existing advice categories with no regressions.
- **Next:** BACKLOG item #4 (dashboard: economy & tech power comparison
  tables) is the next highest-value unblocked task — note it's a
  `templates/dashboard.html` (frontend) change, which per CLAUDE.md should
  be visually verified in a browser before being called done; a future
  cycle should start the app and check the dashboard rather than relying on
  pytest alone.
