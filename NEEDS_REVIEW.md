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
