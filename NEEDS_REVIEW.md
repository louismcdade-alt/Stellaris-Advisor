# Needs review — flagged by autonomous work, not auto-fixed

## 2026-06-18 (cycle 6) — 8 of 12 Empire Builder builds exceed the real starting trait-point budget

**What:** Implementing BACKLOG item #6 (validate.py trait-point budget check)
against the real installed game data (`@species_trait_points = 2` in
`common/species_archetypes/00_species_archetypes.txt`, confirmed live, not
guessed) shows that **8 of the 12 builds in `advisor/builds.py` pick more net
trait-point cost than an empire can actually select at creation**:

| Build | Authority | Traits | Net cost |
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

**Why this wasn't auto-fixed:** unlike the single-build fix in cycle 5 (Iron
Conquerors also had "Strong" + "Very Strong" together — a strictly redundant
duplicate-tier pick, zero design ambiguity to remove), bringing these 8 builds
into budget means **choosing which trait to cut or which drawback trait to add
for each one**, which changes the build's actual character and would make the
existing `why` text inaccurate unless rewritten too. That's a per-build
judgment call about game balance/flavor, not a mechanical fix — exactly the
kind of ambiguous content decision the autorun process is supposed to flag
rather than make unilaterally.

**Product impact:** once this check ships, the Empire Builder tab will show
"⚠ Not fully usable" on these 8 builds (their actual issue list will say
e.g. `traits cost 4 points, over the starting budget of 2 (...)`). The check
itself is correct (verified against live game data, has automated tests, and
a synthetic in-budget build is confirmed *not* flagged) — it's the build
content that needs rebalancing.

**Suggested next step:** for each build above, either drop one positive trait
or add one more negative/drawback trait, and touch up `why` if the dropped
trait was mentioned by name. Re-run `python audit_builds.py` after each edit
to confirm net cost <= 2.
