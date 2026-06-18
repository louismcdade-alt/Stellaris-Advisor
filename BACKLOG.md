# BACKLOG — Stellaris Advisor

Small, concrete, single-sitting tasks, ordered by value. Each names the file(s),
function/behavior, and a "done when" check.

## 1. [DONE 2026-06-18] Add a pytest suite (there are currently none)
- **Where:** new `tests/` dir; `requirements-dev.txt` with `pytest`.
- **Do:** unit-test `clausewitz.parse`/`extract_block` (round-trip a small inline
  Clausewitz string incl. duplicate keys, arrays, nested blocks) and the pure
  heuristics in `analyze.py` / `fleet.py` (feed synthetic snapshot dicts, assert
  expected advice titles / recommended counts). No real `.sav` needed.
- **Done when:** `python -m pytest` passes with ≥10 assertions covering the parser
  and at least `analyze_economy`, `analyze_military`, `fleet.recommend`.

## 2. [DONE 2026-06-18] validate.py: check civic ↔ ethics/authority requirements
- **Where:** `advisor/validate.py` (`_load_civic_categories` / `validate_build`).
- **Do:** parse each civic's `potential`/`possible` block for `has_ethic = …`
  requirements and verify against `build['ethics']`. Currently only file-based
  authority category is checked (the known gap noted in chat).
- **Done when:** `audit_builds.py` flags a deliberately-wrong pairing (e.g. an
  Egalitarian build given a civic that requires Authoritarian) and all 12 shipped
  builds still report 0 issues.

## 3. [DONE 2026-06-18] analyze.py: species-trait-aware economy advice
- **Where:** new `analyze_species(snap)` in `advisor/analyze.py`, added to
  `analyze()`; reads `snap['player']['identity']['species_traits']` (already
  extracted).
- **Do:** map a few traits to tips, e.g. `trait_intelligent`→"lean into research
  jobs", `trait_agrarian`→"favour farming districts", `trait_industrious`→
  "mineral-heavy build".
- **Done when:** a snapshot whose species has `trait_intelligent` yields a
  `category:'economy'` (or `'research'`) tip mentioning research, and a species
  with none of the mapped traits yields nothing extra.

## 4. [DONE 2026-06-18] dashboard: economy & tech power comparison tables
- **Where:** `templates/dashboard.html` (`render()`); payload `d.empires` already
  carries `economy_power` and `tech_power`.
- **Do:** add two tables/bars beside the existing military "Empire Power" table,
  ranking the player vs default empires on economy and tech (reuse the `.bar`
  markup and the signature-diff pattern).
- **Done when:** the Live Advisor right column shows three ranked power tables and
  they update only when their data changes.

## 5. validate.py: detect conflicting trait `opposites` within a build
- **Where:** `advisor/validate.py` (`_load_traits`, `validate_build`).
- **Do:** capture each trait's `opposites = { … }`; flag a build that lists two
  mutually-exclusive traits (e.g. `Rapid Breeders` + `Slow Breeders`).
- **Done when:** a build with an opposing pair is reported as not-verified with a
  clear message; current builds stay at 0 issues.

## 6. validate.py: trait-point budget check
- **Where:** `advisor/validate.py`; read each trait's `cost` from the trait files
  (you already brace-extract the block).
- **Do:** sum positive/negative `cost` for a build's starting traits and warn if
  the net exceeds the default starting trait points (treat 2 as the cap unless you
  read it from defines) or uses more than the default pick limit.
- **Done when:** a build whose traits sum over budget shows a warning in
  `audit_builds.py`; in-budget builds don't.

## 7. fleet.py: report recommended vs current total naval capacity
- **Where:** `advisor/fleet.py` (`recommend`) and `dashboard.html` (`renderFleet`).
- **Do:** sum `slot_cost × recommended` and `slot_cost × current` and return both
  (e.g. `recommended_naval_capacity`, `current_naval_capacity`); show them in the
  fleet header next to "Naval capacity in use".
- **Done when:** the Fleet tab header shows current vs recommended capacity totals
  derived from the live `gamedata` slot costs.

## 8. fleet.py: surface Colossus & Juggernaut as special line items
- **Where:** `advisor/fleet.py` (`recommend`) — these are excluded from the tier
  table today (class `shipclass_military_special` / `shipclass_starbase`).
- **Do:** if the player owns one (present in composition), add a non-tier "special"
  row ("Colossus ×1", "Juggernaut ×1") and a note; don't fold them into the
  battleship/titan budget math.
- **Done when:** a save with a colossus shows it as its own line, and the tier
  recommendations are unchanged.

## 9. Persist the last-selected campaign across launches
- **Where:** `advisor/watcher.py` (`AdvisorState.set_campaign`) + `server.py`
  (`/api/select`); store in a small `last_campaign.txt` next to `owned_dlc.txt`.
- **Do:** on `set_campaign`, write the choice; on `AdvisorState.__init__`, default
  `campaign` to the stored value if none passed on the CLI.
- **Done when:** selecting a campaign, quitting, and relaunching reopens on that
  campaign; the dropdown reflects it.

## 10. analyze.py: planet unemployment hint
- **Where:** `advisor/extract.py` (add a light owned-planet jobs scan, mirroring
  the on-demand pattern of `_fleet_composition`) + new `analyze_planets(snap)`.
- **Do:** count pops without jobs across owned planets and emit a `warning` when
  unemployment is non-trivial ("N unemployed pops — build more jobs/districts").
  Keep the scan on-demand/cached if it's heavy, like the fleet scan.
- **Done when:** a save with unemployed pops produces an unemployment advice card;
  a fully-employed empire produces none, and live-advice latency stays ~1.5s.
