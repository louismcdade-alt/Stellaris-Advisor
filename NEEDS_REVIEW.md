# Needs review — flagged by autonomous work, not auto-fixed

## 2026-06-18 (cycle 6) — 8 of 12 Empire Builder builds exceed the real starting trait-point budget

**Status: RESOLVED 2026-06-18.** See the "trait-point budget rebalance" entry
in PROGRESS.md — all 12 builds now net <= 2 points and stay within the real
5-trait pick limit (`audit_builds.py` reports 0 issues across all 12). Kept
here for history.

**What:** Implementing BACKLOG item #6 (validate.py trait-point budget check)
against the real installed game data (`@species_trait_points = 2` in
`common/species_archetypes/00_species_archetypes.txt`, confirmed live, not
guessed) showed that **8 of the 12 builds in `advisor/builds.py` picked more
net trait-point cost than an empire can actually select at creation**:

| Build | Authority | Traits (original) | Net cost |
|---|---|---|---|
| Technocratic Pioneers | Oligarchic | Intelligent, Natural Engineers, Rapid Breeders, Deviants (-), Sedentary (-) | 3 |
| Iron Conquerors | Imperial | Very Strong, Industrious, Slow Learners (-) | 4 |
| Free Republic Traders | Democratic | Charismatic, Thrifty, Ingenious, Slow Breeders (-) | 4 |
| Agrarian Idyll (Tall) | Democratic | Agrarian, Conservationist, Traditional, Sedentary (-) | 3 |
| Synthetic Ascendancy | Dictatorial | Intelligent, Natural Physicists, Quick Learners, Fleeting (-) | 3 |
| Wilderness Living World | Hive Mind | Intelligent, Rapid Breeders, Strong, Sedentary (-) | 4 |
| Evolutionary Predators | Dictatorial | Strong, Industrious, Rapid Breeders, Slow Learners (-) | 4 |
| Clone-Vat Swarm | Dictatorial | Rapid Breeders, Communal, Strong | 4 |

Budget is 2 for all of these (none use `Natural Design` civic or `Overtuned`
origin, the only two things in the install that grant extra
`BIOLOGICAL_species_trait_points_add`).

**How it was fixed:** each build was rebalanced individually (swap or add one
drawback trait, or drop a redundant positive trait), checked against the real
`opposites` graph for conflicts and the real 5-trait pick limit, and the
`why` text updated to match. Full per-build changes are in the cycle-6
rebalance entry in `PROGRESS.md` and the corresponding commit.

## 2026-06-18 (cycle 10) — BACKLOG item #10 (planet unemployment hint) needs more save-format research than fits a single sitting

**Status: NOT IMPLEMENTED — punted, not auto-shipped.** BACKLOG item #10 as
originally written assumed a simple "count pops without jobs across owned
planets" scan, similar in shape to `extract.compute_fleet`'s on-demand ship
scan. Investigating a real save's gamestate showed the actual current-patch
data model is significantly more involved:

- Stellaris' Pop Groups rework split what used to be one `planet` object into
  two: a `planet=` top-level block (celestial/orbital data only — class,
  size, coordinates, owner) and a separate `colony=` top-level block (the
  actual colonization data — buildings, districts, `pop_groups`, `pop_jobs`,
  `employable_pops`, `num_sapient_pops`, `free_housing`, `stability`, etc.),
  linked via the planet's `colony=<id>` field. Code anywhere in this repo
  that assumed "planet" already meant "the inhabited colony" needs to look up
  the `colony` object instead.
- The colony block does **not** contain a direct "N pops are unemployed"
  field. The closest candidates are `employable_pops` and `num_sapient_pops`
  — but in the one colony checked (the player's homeworld, "Earth") both
  were exactly 7544, which doesn't disambiguate whether `employable_pops`
  means "currently employed" or "eligible to work" (no localisation key
  exists for either field name, so the meaning can't be confirmed from game
  text — these are internal-only save fields).
- `colony.pop_jobs` lists job-object ids (e.g. `338 339 340 ... 365`), but
  there is **no top-level `job=` block** in this save to resolve those ids
  against — so the "obvious" approach (sum each job's filled capacity, sum
  pop count, subtract) has no clear path without more investigation into
  where job-capacity data actually lives in this patch's gamestate format
  (it may be implicit from `districts`/`buildings_cache` job-slot counts
  cross-referenced against `pop_groups` sizes, which is a meaningfully
  bigger scan than "a light owned-planet jobs scan").

**Why this wasn't guessed and shipped anyway:** CLAUDE.md's core promise is
that advice is accurate because it's read live from the game, not guessed.
An unemployment heuristic built on a misread of `employable_pops` could
confidently tell a player "N pops are unemployed" when that's not actually
true, which is worse than not having the feature. Per the autorun process's
hard rule ("if a clean verified change isn't possible, revert and log why"),
this is logged instead of shipped.

**Suggested next step:** find a save with *known* visible unemployment in the
in-game UI (a colony actively showing the unemployment icon), and compare its
`colony` block fields against a fully-employed colony's to isolate which
field(s) actually move. Alternatively, sum `districts`/`buildings_cache`
job-slot capacities (would need to brace-extract each building/district id's
own block to read its job-grant fields) against `pop_groups` total size on
the same colony — more work, but doesn't rely on guessing an undocumented
field's meaning.
