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

## 5. [DONE 2026-06-18] validate.py: detect conflicting trait `opposites` within a build
- **Where:** `advisor/validate.py` (`_load_traits`, `validate_build`).
- **Do:** capture each trait's `opposites = { … }`; flag a build that lists two
  mutually-exclusive traits (e.g. `Rapid Breeders` + `Slow Breeders`).
- **Done when:** a build with an opposing pair is reported as not-verified with a
  clear message; current builds stay at 0 issues.

## 6. [DONE 2026-06-18] validate.py: trait-point budget check
- **Where:** `advisor/validate.py`; read each trait's `cost` from the trait files
  (you already brace-extract the block).
- **Do:** sum positive/negative `cost` for a build's starting traits and warn if
  the net exceeds the default starting trait points (treat 2 as the cap unless you
  read it from defines) or uses more than the default pick limit.
- **Done when:** a build whose traits sum over budget shows a warning in
  `audit_builds.py`; in-budget builds don't.

## 7. [DONE 2026-06-18] fleet.py: report recommended vs current total naval capacity
- **Where:** `advisor/fleet.py` (`recommend`) and `dashboard.html` (`renderFleet`).
- **Do:** sum `slot_cost × recommended` and `slot_cost × current` and return both
  (e.g. `recommended_naval_capacity`, `current_naval_capacity`); show them in the
  fleet header next to "Naval capacity in use".
- **Done when:** the Fleet tab header shows current vs recommended capacity totals
  derived from the live `gamedata` slot costs.

## 8. [DONE 2026-06-18] fleet.py: surface Colossus & Juggernaut as special line items
- **Where:** `advisor/fleet.py` (`recommend`) — these are excluded from the tier
  table today (class `shipclass_military_special` / `shipclass_starbase`).
- **Do:** if the player owns one (present in composition), add a non-tier "special"
  row ("Colossus ×1", "Juggernaut ×1") and a note; don't fold them into the
  battleship/titan budget math.
- **Done when:** a save with a colossus shows it as its own line, and the tier
  recommendations are unchanged.

## 9. [DONE 2026-06-18] Persist the last-selected campaign across launches
- **Where:** `advisor/watcher.py` (`AdvisorState.set_campaign`) + `server.py`
  (`/api/select`); store in a small `last_campaign.txt` next to `owned_dlc.txt`.
- **Do:** on `set_campaign`, write the choice; on `AdvisorState.__init__`, default
  `campaign` to the stored value if none passed on the CLI.
- **Done when:** selecting a campaign, quitting, and relaunching reopens on that
  campaign; the dropdown reflects it.

## 10. [BLOCKED — see NEEDS_REVIEW.md] analyze.py: planet unemployment hint
- **Where:** `advisor/extract.py` (add a light owned-planet jobs scan, mirroring
  the on-demand pattern of `_fleet_composition`) + new `analyze_planets(snap)`.
- **Do:** count pops without jobs across owned planets and emit a `warning` when
  unemployment is non-trivial ("N unemployed pops — build more jobs/districts").
  Keep the scan on-demand/cached if it's heavy, like the fleet scan.
- **Done when:** a save with unemployed pops produces an unemployment advice card;
  a fully-employed empire produces none, and live-advice latency stays ~1.5s.
- **2026-06-18 update:** investigated against a real save (cycle 10) — the
  data model is more involved than this item assumed. Planets and colonies
  are now separate save objects (`planet=` is celestial-only; the inhabited-
  colony data — `pop_groups`, `pop_jobs`, `employable_pops`, etc. — lives in
  a separate `colony=` block referenced by the planet's `colony=<id>`). No
  field directly gives "N unemployed pops", and the obvious candidate
  (`employable_pops`) couldn't be confirmed (no localisation key, and it
  exactly equalled `num_sapient_pops` on the one colony checked, which
  doesn't disambiguate its meaning). Full findings and a suggested research
  approach are in `NEEDS_REVIEW.md` — read that before attempting this again.

## 11. [DONE 2026-06-18] analyze.py: stop suggesting alliances to empires already in a federation
- **Where:** `advisor/analyze.py` (`analyze_diplomacy`); `snap['player']['in_federation']`
  is already extracted (`extract.py:401`) but never read anywhere in `analyze.py`.
- **Do:** if `in_federation` is true, treat the empire as having allies (skip the
  "No allies yet — consider a defensive pact" suggestion; optionally add a `good`
  card noting federation membership instead) — federation members may have no
  bilateral `alliance` relation flag, which is the only thing the current check
  looks at, so it can give actively wrong advice today.
- **Done when:** a snapshot with `in_federation: True` and no rival/ally relations
  no longer produces the "No allies yet" card; the existing rivals/allies cards
  are unaffected.

## 12. [DONE 2026-06-18] validate.py: check origin ethic/authority requirements (mirrors civic check)
- **Where:** `advisor/validate.py` (`_load_loc`/new `_load_origin_categories` or
  extend `_catalogs`); reuse the existing `_ethic_requirements`/`_ethic_ok` helpers
  from the civic check (item #2).
- **Do:** origins gate on ethics the same way civics do (`ethics = { OR/NOT/NOR =
  {...} }` inside `possible`/`potential`) — confirmed live: 20 of the 61 origins in
  `common/governments/civics/00_origins.txt` have an `ethics =` block (e.g.
  `origin_necrophage`, `origin_syncretic_evolution`, `origin_common_ground`).
  `validate_build` currently only checks the origin *exists*, not whether the
  build's ethics actually qualify for it. Parse and check the same way civics are.
- **Done when:** `audit_builds.py` flags a deliberately-wrong origin/ethics pairing,
  and re-run against all 12 shipped builds — fix any that turn out to actually be
  mismatched (same pattern as the trait-budget check in item #6, which did turn up
  real bugs) before calling it done.

## 13. extract.py + analyze.py: surface active-war status
- **Where:** `advisor/extract.py` (new parsing of the gamestate's top-level `war=`
  / `wars=` blocks — not parsed at all today, only `last_date_at_war` and per-relation
  `truce` are) + `advisor/analyze.py` (`analyze_military` or `analyze_diplomacy`).
- **Do:** inspect a real save's gamestate to confirm the war-block shape first (this
  is the exploratory part), then detect whether the player is currently a war
  participant and against whom, and surface a `warning`/`info` card with the
  opponent and (if present) war exhaustion — today the advisor only has historical
  "you were at war as of `last_date_at_war`" framing, not "you are at war right now".
- **Done when:** a save where the player is mid-war produces a card naming the
  opponent; a save at peace produces none, and live-advice latency stays ~1.5s.

## 14. dashboard: Empire Builder free-text search
- **Where:** `templates/dashboard.html` (`buildGoalButtons`/`loadBuilds`, the
  `#builder-head` row).
- **Do:** add a text input next to the goal-filter chips that filters the already-
  loaded `d.builds` client-side by substring match against name/civics/traits/origin
  (no new API call needed — `loadBuilds()` already has the full list in memory).
- **Done when:** typing e.g. "hive" narrows the builder grid to matching builds
  instantly, clearing the box restores the full (goal-filtered) list.

## 15. README.md: document the test suite and current module layout
- **Where:** `README.md` ("Project layout" section, currently lists only 4 of the
  ~13 modules in `advisor/`) and a missing mention of `pytest`/`audit_builds.py`.
- **Do:** update the file tree to match `advisor/`'s actual contents (`builds.py`,
  `validate.py`, `profile.py`, `knowledge.py`, `gamedata.py`, `dlc.py`), and add a
  short "Development" section: `python -m pip install -r requirements-dev.txt`,
  `python -m pytest`, `python audit_builds.py`.
- **Done when:** the file tree in the README matches `ls advisor/`, and a fresh
  clone's setup instructions are sufficient to run the test suite without reading
  CLAUDE.md first.
