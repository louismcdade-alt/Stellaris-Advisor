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

## 2026-06-18 (cycle 4)
- **Did:** Implemented BACKLOG item #4 — added "Empire Power — Economy" and
  "Empire Power — Technology" tables to the Live Advisor right column,
  beside the existing military power table, ranking the player vs. default
  empires on `economy_power`/`tech_power` (already in the `/api/advice`
  payload). Refactored the previously inline military-power render block in
  `templates/dashboard.html` into a shared `renderPowerTable(d, field,
  tableId, label)` so all three tables reuse the same ranked-bar markup and
  per-field change-signature diffing (now an object `sigPower` keyed by
  field instead of one flat string) — matches the existing "only re-render
  when data changes" pattern used elsewhere in the file.
- **Verified:** No Python changed, so `python -m pytest -v` stayed at 22
  passed/0 failed (regression check only). Per CLAUDE.md's UI-change rule,
  started the real app (`python run.py --no-browser --port 8771`) against
  the player's actual current save, confirmed `/api/advice` returns real
  `economy_power`/`tech_power` per empire (incl. correctly excluding fallen
  empires/pirates/primitives/etc. via the existing `type==="default"`
  filter), confirmed the served dashboard HTML contains all three table
  element IDs (`powertable`, `econpowertable`, `techpowertable`), and
  confirmed the page's inline `<script>` block parses with no syntax errors
  before and after the change. Did not have a screenshot/vision tool
  available in this session to confirm pixel-level rendering — the
  end-to-end data path and DOM wiring are verified, but a human should give
  it a quick look the next time the app is opened normally.
- **Next:** BACKLOG item #5 (validate.py: detect conflicting trait
  `opposites` within a build) is the next highest-value unblocked task.

## 2026-06-18 (cycle 5)
- **Did:** Implemented BACKLOG item #5 — `validate_build` now flags builds
  that pick two mutually-exclusive traits. Added `_trait_opposites(block)`
  to `advisor/validate.py` (parses a trait's `opposites = { "trait_x" ... }`
  block, handling both single-line and multi-line forms), stored the result
  per trait id in `_load_traits`'s existing `trait_info` dict, and added
  `_traits_conflict(id_a, id_b, trait_info)` (checks both directions since
  `opposites` isn't always declared symmetrically in the game files). Wired
  into `validate_build`'s trait loop: each successfully-validated trait's
  representative startable id is collected, then every pair is checked.
  4 new tests in `tests/test_validate.py` (parsing single-line and
  multi-line `opposites`, absent-case, and `_traits_conflict` both
  directions plus the no-conflict case).
- **Verified:** `python -m pytest -v` — 26 passed, 0 failed. Running
  `audit_builds.py` against the real install caught a genuine pre-existing
  bug: the shipped "Iron Conquerors" build picked both "Strong" and "Very
  Strong" (real mutually-exclusive trait tiers in the game files) — exactly
  the bug class this check exists to catch. Fixed `advisor/builds.py` to
  drop "Strong" (redundant with "Very Strong") so the build is actually
  pickable in-game; `audit_builds.py` is back to 0 issues across all 12
  builds. Also found and fixed a `KeyError` crash in the new code (a trait
  id present in `civic_names`/`trait_names` localisation but not loaded
  into `trait_info`, e.g. a ruler trait outside the species/ascension trait
  files, used `cat['trait_info'][i]` instead of `.get(i, {})`). Manually
  confirmed the check has teeth with a synthetic Rapid Breeders + Slow
  Breeders build (correctly flagged).
- **Next:** BACKLOG item #6 (validate.py: trait-point budget check) is the
  next highest-value unblocked task.

## 2026-06-18 (cycle 6)
- **Did:** Implemented BACKLOG item #6 — `validate_build` now flags builds
  whose selected traits' net `cost` exceeds the starting trait-point budget.
  Added `_trait_cost(block)` (parses a trait's top-level `cost = N`,
  excluding `slave_cost`/etc via a negative lookbehind), stored it per trait
  in `_load_traits`'s `trait_info`, and added `_TRAIT_POINT_BUDGET = 2`
  (confirmed live: `@species_trait_points = 2` in
  `common/species_archetypes/00_species_archetypes.txt` — not guessed, and
  not exceeded by any of the 12 builds' civics/origins, since the only two
  things in the install that add trait points, `Natural Design` civic and
  `Overtuned` origin, aren't used by any of them). 3 new tests in
  `tests/test_validate.py` (positive/negative cost parsing, `slave_cost`
  exclusion, absent-cost default).
- **Verified:** `python -m pytest -v` — 29 passed, 0 failed. Manually
  confirmed a synthetic in-budget build (single -1 drawback trait) is not
  flagged.
- **Notable finding, NOT auto-fixed:** running `audit_builds.py` against the
  real install shows **8 of the 12 shipped builds exceed this real budget**
  (e.g. Iron Conquerors: Very Strong(3) + Industrious(2) + Slow Learners(-1)
  = 4 net, over the budget of 2). Unlike cycle 5's Strong/Very Strong fix
  (a strictly redundant duplicate, no judgment call), rebalancing these 8
  requires picking which trait to cut or which drawback to add per build —
  a design/flavor decision, not a mechanical one — so per the autorun hard
  rules this was logged to `NEEDS_REVIEW.md` (full breakdown, per-build net
  costs, and a suggested fix-per-build approach) instead of being changed
  unilaterally. The check itself is correct and shipped; the build content
  needs a follow-up pass.
- **Next:** BACKLOG item #7 (fleet.py: report recommended vs current total
  naval capacity) is the next highest-value unblocked task. Also: see
  `NEEDS_REVIEW.md` for the 8 over-budget builds, which should probably be
  addressed before or alongside whichever cycle picks that up.

## 2026-06-18 (trait-point budget rebalance, requested follow-up to cycle 6)
- **Did:** Rebalanced all 8 over-budget builds flagged in `NEEDS_REVIEW.md`,
  per-build, by computing exact trait costs and the real `opposites` graph
  live from the install (not guessed) and picking a fix that fits each
  build's existing flavor:
  - **Technocratic Pioneers:** swapped Sedentary (-1) -> Repugnant (-2).
  - **Iron Conquerors:** added Repugnant (-2) — a conqueror doesn't need to
    be liked.
  - **Free Republic Traders:** dropped Ingenious (+2) as redundant with
    Thrifty's energy synergy, rather than bolting on an unrelated drawback.
  - **Agrarian Idyll (Tall):** added Deviants (-1) — a non-issue for a tall,
    largely single-species empire.
  - **Synthetic Ascendancy:** added Quarrelsome (-1) — irrelevant when
    racing for Synthetic ascension instead of managing happiness.
  - **Wilderness Living World:** added Nonadaptive (-2) — free, since the
    Wilderness origin keeps you on one living world anyway (no normal
    colonization to be hurt by a habitability penalty).
  - **Evolutionary Predators:** added Repugnant (-2) — Xenophobe predators
    were never trying to make friends.
  - **Clone-Vat Swarm:** added Repugnant (-2) — a clone-vat empire isn't
    winning hearts and minds either way.
  Every addition was checked against the live `opposites` data for that
  build's existing picks (no conflicts) and against the real 5-trait pick
  limit (`@species_max_traits = 5`) — no build exceeds it. `why` text was
  updated wherever a trait was added/removed/renamed so the description
  still matches the actual picks.
- **Verified:** `python audit_builds.py` — 0 issues across all 12 builds
  (civics/ethics, origin, trait-existence, trait-opposites, AND the new
  trait-point-budget check all pass). `python -m pytest -v` — 29 passed, 0
  failed (no test changes needed; this was a content-only fix in
  `advisor/builds.py`). Manually re-confirmed every build's trait count is
  <= 5.
- **Next:** `NEEDS_REVIEW.md` marked resolved. BACKLOG item #7 (fleet.py
  naval capacity totals) remains the next highest-value unblocked task.

## 2026-06-18 (theme pass, requested by user — not a BACKLOG item)
- **Did:** Made the dashboard "feel more Stellaris" per explicit user
  request, picking 3 directions they chose from a multi-select: (1)
  authentic Stellaris UI chrome — angular corner-cut panels (clip-path) on
  every `section`/`.build` card and the tabs, a gold corner-bracket accent
  on the header, and a gold "selected" treatment on the profile badge and
  active-tab underline; (2) more motion/feedback — a slow diagonal scan-
  sweep highlight across each panel, row-hover glow on every table, and a
  `.scan-flash` pulse on the advice/ascension panels whenever new advice
  data actually changes (a `pulseFlash()` helper that force-reflows so the
  animation restarts on every distinct update, not just the first); (3)
  empire-flavored color theming — the whole accent palette (`--accent`,
  `--accent2`, `--accent-rgb`, used throughout via `rgba(var(--accent-rgb),
  x)`) now shifts based on the player's real authority/dominant ethic (read
  from `d.player.identity.authority`/`.ethics`, already in the existing API
  payload — no backend change needed): red for Hive Mind, cyan-chrome for
  Machine Intelligence, green/gold for Megacorp, and a per-ethic color
  (orange militarist, teal xenophile, purple spiritualist, gold
  authoritarian, etc.) with fanatic ethics taking priority, mirroring
  `profile.py`'s own "fanatic first" ordering.
- **Verified:** inline `<script>` parses cleanly (Node syntax check) before
  and after. `python -m pytest -v` — 29 passed (no Python touched).
  Started the real app (`python run.py --no-browser --port 8772`) and
  confirmed via curl that `/api/advice` exposes real
  `player.identity.authority`/`.ethics` (this save: `auth_democratic` +
  `ethic_fanatic_egalitarian` -> correctly resolves to the Egalitarian
  theme), and that the served HTML contains the new theme/animation code.
  Opened the running app in the user's browser for them to eyeball directly
  — no screenshot tool available this session to confirm pixel rendering
  myself.
- **Next:** user to glance at the live app; BACKLOG item #7 (fleet.py naval
  capacity totals) up next regardless per "continue for one more cycle".

## 2026-06-18 (cycle 7)
- **Did:** Implemented BACKLOG item #7 — `fleet.recommend()` now returns
  `current_naval_capacity`/`recommended_naval_capacity`, summing
  `slot_cost x count` over the relevant hull family's rows only (not the
  empire's total naval cap from other families/starbases, which
  `used_naval_capacity` already covers). Reuses the existing `_slot_cost()`
  live-gamedata lookup, so the totals track the current patch like
  everything else in this module. Wired into `templates/dashboard.html`'s
  `renderFleet()` — the fleet header now shows "This family: N used / M
  recommended" next to the existing "Naval capacity in use". 2 new tests in
  `tests/test_fleet.py`.
- **Verified:** `python -m pytest -v` — 31 passed, 0 failed. Caught my own
  mistake during manual testing: hit the real `/api/fleet` endpoint against
  a server process that had been started *before* this edit, got `None` for
  both new fields (stale loaded module, not a bug) — restarted the server
  and re-checked: `current_naval_capacity: 32`, `recommended_naval_capacity:
  30` against a real Cruiser-tier fleet of 26 warships. Confirmed the
  served dashboard HTML contains the new header text. JS syntax check
  clean.
- **Next:** BACKLOG item #8 (fleet.py: surface Colossus & Juggernaut as
  special line items) is the next highest-value unblocked task.

## 2026-06-18 (cycle 8)
- **Did:** Implemented BACKLOG item #8 — `fleet.recommend()` now returns a
  `specials` list (`[{'class', 'count', 'naval_capacity'}, ...]`) for any
  owned Colossus/Juggernaut, kept entirely separate from `rows`/the tier
  budget math (they were never part of `STD_TIERS`/`BIO_TIERS` to begin
  with, so this required no change to the recommendation math itself — just
  surfacing data that already existed in `comp`). Added `colossus`/
  `juggernaut` to `FALLBACK_SLOT` (confirmed live: both cost 32 naval
  capacity, `class: shipclass_military_special`/`shipclass_starbase`) so
  the new behavior is deterministic in tests regardless of whether a real
  install is present — previously these two hulls had no fallback entry at
  all. Dashboard's `renderFleet()` shows a small second table ("Special
  hull") below the main tier table when `specials` is non-empty.
- **Verified:** `python -m pytest -v` — 33 passed, 0 failed (3 new tests:
  Colossus surfaces as a special row not a tier row, owning one doesn't
  change the corvette tier's own recommended count, and an empty/no-capital-
  hull fleet reports `specials: []`). JS syntax check clean. Started the
  real app and confirmed `/api/fleet` returns `specials` (empty for this
  save, which owns neither hull — correct, not an error) and the served
  HTML contains the new render path.
- **Next:** BACKLOG item #9 (persist last-selected campaign) is the next
  highest-value unblocked task.

## 2026-06-18 (cycle 9)
- **Did:** Implemented BACKLOG item #9 — `advisor/watcher.py` now persists
  the dashboard's campaign selection to `last_campaign.txt` (project root,
  next to `owned_dlc.txt`, already pre-listed in `.gitignore` with a comment
  anticipating exactly this). New `_read_last_campaign()`/
  `_write_last_campaign()`; `AdvisorState.__init__` now defaults
  `self.campaign` to the persisted value when none is passed on the CLI
  (`campaign or _read_last_campaign() or None` — an explicit `--campaign`
  flag still wins), and `set_campaign()` writes the choice (including
  writing `''` when switching back to "Auto", which correctly clears the
  persisted value on the next launch). This is app-managed runtime state,
  not user data — same category as `advisor.log`, not `owned_dlc.txt`.
- **Verified:** `python -m pytest -v` — 39 passed (6 new tests in
  `tests/test_watcher.py`, using `monkeypatch` to redirect the persisted-
  state path to a `tmp_path` so tests never touch the real project-root
  file). End-to-end against the real app: selected a real campaign via
  `/api/select`, confirmed `last_campaign.txt` was written with the right
  folder name, restarted the server (simulating a relaunch) and confirmed
  `/api/campaigns` reported it as `selected` again — exactly the backlog's
  "done when". Reset selection back to auto and deleted the test-generated
  file afterward to leave the dev environment as found.
- **Next:** BACKLOG item #10 (analyze.py: planet unemployment hint) is the
  next highest-value unblocked task.

## 2026-06-18 (cycle 10 — punted, not shipped)
- **Did:** Attempted BACKLOG item #10. Investigated a real save's gamestate
  to find owned-planet job/unemployment data, and found the actual current-
  patch data model is significantly more involved than the item assumed:
  planets and colonies are now separate save objects (the Pop Groups
  rework split them), the inhabited-colony fields (`pop_groups`,
  `pop_jobs`, `employable_pops`, `num_sapient_pops`, ...) live in a
  separate `colony=` block, and no field directly gives an unemployment
  count. The likeliest candidate field (`employable_pops`) couldn't be
  confirmed — no localisation key exists for it, and on the one colony
  checked it exactly equalled `num_sapient_pops`, which doesn't disambiguate
  "currently employed" from "eligible to work".
- **Why not shipped anyway:** guessing the field's meaning risks giving
  actively wrong advice ("N pops unemployed" when that's not true), which
  contradicts CLAUDE.md's core promise that advice is accurate because it's
  read live from the game. Per the autorun process's hard rule, this is
  logged to `NEEDS_REVIEW.md` (full findings + a suggested research path:
  compare a colony with *visible* in-game unemployment against a fully-
  employed one to isolate which field actually moves) instead of shipped.
  BACKLOG item #10 marked `[BLOCKED — see NEEDS_REVIEW.md]`, not `[DONE]`.
- **Verified:** no code changed; `python -m pytest -v` untouched at 39
  passed (sanity-checked, not because this cycle touched anything testable).
- **Next:** BACKLOG item #11 (analyze.py: respect `in_federation` in
  diplomacy advice) is the next highest-value unblocked task.

## 2026-06-18 (cycle 11)
- **Did:** Implemented BACKLOG item #11 — `analyze_diplomacy` now reads the
  already-extracted `player['in_federation']` flag. Federation members no
  longer get the "No allies yet — consider a defensive pact" suggestion
  (federation membership may not set a bilateral `alliance` relation flag,
  which was the only thing the old check looked at), and now get a `good`
  "Federation member" card in the same slot the "N ally/allies" card uses
  when there's no separate bilateral alliance to list.
- **Verified:** `python -m pytest -v` — 41 passed (2 new tests: federation
  member without bilateral alliance relations gets the federation card and
  not the "no allies" suggestion; a non-federation empire's existing "no
  allies" suggestion is unchanged). Cross-checked against the real save:
  this player is in a federation *and* has explicit ally relations, so the
  existing "2 ally/allies" card still fires correctly — confirms no
  regression to the case the bug fix doesn't touch.
- **Next:** BACKLOG item #12 (validate.py: origin ethic/authority
  requirements) is the next highest-value unblocked task.

## 2026-06-18 (cycle 12)
- **Did:** Implemented BACKLOG item #12 — `validate_build` now checks an
  origin's own ethic/authority requirements, mirroring the civic check from
  item #2. Confirmed live: 20 of 61 origins gate ethics and 11 gate
  authority via the identical `OR`/`NOT`/`NOR` shape civics use. Refactored
  `_ethic_requirements` into a generic `_gate_requirements(block, section,
  prefix)` (kept `_ethic_requirements`'s external behavior/signature
  unchanged — gestalt-discard quirk included — so existing tests needed no
  changes) and added `_authority_requirements` as a thin wrapper over it.
  New `_load_origin_gates` scans `00_origins.txt` into `origin_ethics`/
  `origin_authority` catalog dicts. New `_BUILD_AUTH_IDS`/
  `_build_authority_id` map builds.py's authority labels ("Hive Mind",
  "Democratic", ...) to `auth_xxx` ids (a different label set than
  `profile.py`'s noun-form `_AUTH_LABEL`, since `builds.py` uses adjectives).
  `validate_build` checks both gates after the origin-exists check, only
  when the build's authority label is recognized (skips silently rather
  than false-flagging on an unrecognized label).
- **Verified:** `python -m pytest -v` — 44 passed (3 new tests: bare-value
  required parsing, NOT-excluded parsing, label->id mapping). `python
  audit_builds.py` — 0 issues across all 12 builds (unlike cycle 6's
  trait-budget check, this one didn't surface any pre-existing bugs — the
  shipped builds' origin/ethic/authority pairings were already correct).
  Manually confirmed the check has teeth both ways: a synthetic
  Necrophage+Fanatic-Xenophile build is flagged ("conflicts with
  ethic(s): ethic_fanatic_xenophile"), a synthetic Progenitor-Hive+
  Democratic build is flagged ("needs authority: auth_hive_mind"), and a
  correctly-paired Progenitor-Hive+Hive-Mind build raises no origin-gate
  issue (only the expected, pre-existing civic mismatch from using the
  wrong civics in the synthetic test build).
- **Next:** this closes out the requested batch of 5 cycles (8, 9, 10
  [punted — see NEEDS_REVIEW.md], 11, 12). BACKLOG item #13 (extract.py:
  surface active-war status) is the next highest-value unblocked task,
  flagged as exploratory in its own entry.

## 2026-06-19 — React/Vite frontend migration: Live Advisor, Fleet Manager, Empire Builder screens
- **Did:** Ported the remaining three dashboard screens from the old
  `templates/dashboard.html` to the new React + Vite + Framer Motion frontend
  (`frontend/`), each wired to the existing `/api/advice`, `/api/fleet`,
  `/api/builds` endpoints with no backend changes: `LiveAdvisor.jsx`
  (advice cards, ascension split-out, resource table with count-up numbers,
  3 ranked power-comparison tables), `FleetManager.jsx` (doctrine/stat header,
  hull-class table with animated `scaleX` bars, specials table, notes —
  fetches only while its tab is active since the ship scan is expensive),
  `EmpireBuilder.jsx` (goal-filter pills, build card grid with staggered
  entrance and verified/issue badges). New shared pieces: `Panel.jsx` (the
  reusable corner-cut Stellaris chrome + scan-flash-on-update, used by all
  three screens), `DataTable.css` (shared table look), `theme.js` (ported
  the empire-ethic/authority accent-color theming that the old dashboard had).
  All animation draws from the existing `motion.js` token system; bars use
  `scaleX`/`opacity` only, never `width`, per the motion system's GPU-only rule.
- **Also:** while building the Fleet Manager screen, the user asked for it to
  show how many fleets the recommended composition needs (accounting for
  naval capacity). Investigating against a real save found `used_naval_capacity`
  (230) doesn't reconcile with the hull-family naval capacity `fleet.py`
  already computes (34) — likely strike craft, unconfirmed. A capacity-scaled
  `fleets_needed` was implemented, found to produce bad advice on the real
  save (~4x too many recommended hulls), and reverted before commit — `fleet.py`
  is byte-for-byte unchanged. Shipped a safe alternative instead: presentation-only
  chunking of the recommended totals into ~20-ship batches (`FleetManager.jsx`'s
  `chunkIntoFleets`), which makes no capacity claim. Full writeup in
  `NEEDS_REVIEW.md` ("Fleet Manager: `used_naval_capacity` doesn't reconcile...").
- **Verified:** `npx eslint src` clean, `npm run build` succeeds after every
  change, all three screens manually checked against the live test server
  (`python run.py --port 8775`) with a real save loaded — advice cards, fleet
  table, and build cards all render real data correctly; `python -m pytest -v`
  — 44 passed (Python side untouched by this work, confirms the fleet.py
  revert left no trace).
- **Next:** BACKLOG item #11 (update CLAUDE.md for the React/Vite frontend)
  is the last item before this migration is fully wrapped up — tech
  stack/conventions/commands/project-structure sections all need rewriting
  now that all three screens are live and `templates/dashboard.html` is
  unreferenced.

## 2026-06-20 — CLAUDE.md update, legacy dashboard removal, BACKLOG item #13 (active-war status)
- **Did:** Finished the React/Vite migration wrap-up: updated CLAUDE.md for the
  new frontend (tech stack, commands, data-flow diagram, project structure,
  conventions, do-not-touch list; also fixed a stale "no tests exist" claim —
  there are 47 now), added `frontend/node_modules/` to `.gitignore`, deleted
  the now-unreferenced `templates/dashboard.html` (684 lines, superseded by
  `frontend/`), and committed the whole migration (`6ee1e8a`).
  Then picked up BACKLOG item #13: surface active-war status. Added
  `advisor.extract._active_wars()`, which brace-extracts the gamestate's
  top-level `war=` section (not parsed anywhere before this), finds any war
  where the player's country appears in `attackers`/`defenders` (directly or
  via alliance/subject/overlord call-ins), and resolves the *opposing* side's
  `call_type=primary` belligerent to a readable name via the already-parsed
  `countries_raw` dict. Wired into `player['wars']` in `build_snapshot`.
  `analyze_military` now emits a `warning` card per active war ("At war with
  X" — attacking/defending, start date, war exhaustion %) instead of the old
  `last_date_at_war`-only heuristic; that heuristic is kept as a fallback
  (retitled "Recently at war", downgraded to `info`) for when no war block
  matches but the player was at war within the last year.
- **Performance:** `war=` sits very late in a large save's gamestate (~82%
  through the 29 MB file on the test save), so a cold `extract_block` scan
  from offset 0 cost ~0.35s on its own. Reused the end-offset already
  returned by the (already-mandatory) `country=` block extraction as the
  search start for `war=` — `country=` is confirmed to end well before
  `war=` begins on every save checked — cutting that cost to ~0.16s. Falls
  back to a full scan from 0 if nothing is found past that offset, so an
  unexpected save layout degrades to the slower-but-correct path instead of
  silently reporting "no wars". Note: `build_snapshot`'s total time on this
  particular (large, late-game, turn ~2275) save was already ~2.1s before
  this change, over the ~1.5s figure documented in CLAUDE.md — a pre-existing
  condition on this specific save, not introduced here; this change adds
  ~0.15-0.2s on top of that baseline.
- **Verified:** ran `_active_wars`/`build_snapshot` against the newest save
  in all 11 of the user's campaigns — correctly found 0, 1, and 2
  simultaneous active wars across different saves, both attacker and
  defender sides, with correct opponent names and exhaustion values (cross-
  checked one save's raw `war=` block by hand). Added three new
  `test_analyze.py` cases (active-war card, historical fallback, neither).
  `python -m pytest -v` — 47 passed.
- **Note:** BACKLOG item #14 referenced the now-deleted `templates/dashboard.html`;
  updated it to point at `frontend/src/components/EmpireBuilder.jsx`/`GoalFilter.jsx`
  instead (no functional change, just kept the backlog accurate).
- **Next:** BACKLOG item #15 (README.md module-layout/test-suite docs) is the
  next unblocked item.
