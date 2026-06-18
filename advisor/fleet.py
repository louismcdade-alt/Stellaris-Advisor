"""
Fleet Manager — recommend how many of each warship to field.

Naval-capacity costs (fleet_slot_size), hull prerequisites and which ships are
warships are read live from the installed game files (advisor.gamedata), so the
numbers track the current patch instead of hard-coded values. We support both
the standard hull family and BioGenesis bioships.

Doctrine: spam the cheapest hull early, shift to a main line of the heaviest hull
you have, keep a cheap screen to soak strike craft / missiles, and add a capped
number of titans for their fleet-wide auras.

`current_naval_capacity`/`recommended_naval_capacity` sum slot_cost x count over
this hull family's rows only (not the empire's total naval cap, which may include
other families/starbases) -- they tell you what re-allocating to the recommended
composition would cost versus what's already spent on it.
"""

from . import gamedata

# Each family's hull at each naval-cap "slot" tier. Names are the ship_size ids.
STD_TIERS = {1: 'corvette', 2: 'destroyer', 3: 'cruiser', 4: 'battleship', 8: 'titan'}
BIO_TIERS = {1: 'mauler', 2: 'weaver', 3: 'harbinger', 4: 'stinger', 8: 'bio_titan'}
BIO_HULLS = set(BIO_TIERS.values())

# Fallback costs/prereqs if the game files can't be read.
FALLBACK_SLOT = {'corvette': 1, 'destroyer': 2, 'cruiser': 3, 'battleship': 4, 'titan': 8,
                 'mauler': 1, 'weaver': 2, 'harbinger': 3, 'stinger': 4, 'bio_titan': 8}
FALLBACK_TECH = {'destroyer': 'tech_destroyers', 'cruiser': 'tech_cruisers',
                 'battleship': 'tech_battleships', 'titan': 'tech_titans',
                 'weaver': 'tech_weavers', 'harbinger': 'tech_harbingers',
                 'stinger': 'tech_stingers', 'bio_titan': 'tech_titans'}

ROLE = {1: 'escort', 2: 'picket', 3: 'line', 4: 'capital', 8: 'flagship'}

# Composition as share of naval-capacity budget, keyed by the heaviest "main"
# slot (1..4). Titans (slot 8) are added separately and capped.
TEMPLATE_BY_MAIN = {
    1: {1: 1.0},
    2: {1: 0.5, 2: 0.5},
    3: {1: 0.2, 2: 0.2, 3: 0.6},
    4: {1: 0.15, 2: 0.15, 4: 0.6},
}

PRETTY = {'bio_titan': 'Bio-Titan'}


def _pretty(name):
    return PRETTY.get(name, name.replace('_', ' ').title())


def _info(name):
    """Look up a hull in the game data, allowing for bioship growth stages
    (their ship_size ids are e.g. 'stinger_stage_1', not 'stinger')."""
    sizes = gamedata.ship_sizes()
    return sizes.get(name) or sizes.get(name + '_stage_1')


def _slot_cost(name):
    info = _info(name)
    if info and info.get('slot'):
        return info['slot']
    return FALLBACK_SLOT.get(name, 1)


def _prereq(name):
    info = _info(name)
    if info is not None:
        return info.get('prereq')
    return FALLBACK_TECH.get(name)


def recommend(player):
    techs = set(player.get('researched_techs', []))
    comp = (player.get('fleet') or {}).get('composition', {})

    # Which family is this empire flying?
    bio = any(comp.get(h) for h in BIO_HULLS) or ('tech_maulers' in techs)
    tiers = BIO_TIERS if bio else STD_TIERS

    # Naval cap currently spent on this family's warships (what we re-allocate).
    used_on_warships = sum(comp.get(h, 0) * _slot_cost(h) for h in tiers.values())
    budget = used_on_warships if used_on_warships >= 8 else 16

    # Which slots are unlocked (slot 1 always; others need their prereq tech).
    unlocked = {1}
    for slot, name in tiers.items():
        if slot == 1:
            continue
        pre = _prereq(name)
        if pre is None or pre in techs:
            unlocked.add(slot)

    main = max([s for s in unlocked if s <= 4] or [1])
    template = dict(TEMPLATE_BY_MAIN[main])
    if 8 in unlocked:                       # add a small, capped titan contingent
        template[main] = max(0.0, template.get(main, 0.0) - 0.10)
        template[8] = 0.10

    recommended = {}
    for slot, pct in template.items():
        name = tiers[slot]
        cost = _slot_cost(name)
        n = round(budget * pct / cost) if cost else 0
        if slot == 8:
            n = max(1, n)
        recommended[name] = max(0, n)

    # Build the comparison rows over every relevant hull of this family.
    rows = []
    for slot in sorted(tiers):
        name = tiers[slot]
        cur = comp.get(name, 0)
        rec = recommended.get(name, 0)
        if cur == 0 and rec == 0:
            continue
        rows.append({'class': _pretty(name), 'role': ROLE[slot],
                     'current': cur, 'recommended': rec, 'delta': rec - cur})

    warships = sum(comp.get(h, 0) for h in tiers.values())
    current_naval_capacity = sum(comp.get(h, 0) * _slot_cost(h) for h in tiers.values())
    recommended_naval_capacity = sum(n * _slot_cost(name) for name, n in recommended.items())
    top_name = tiers[main]
    fam = 'bioship' if bio else 'standard'
    doctrine = _doctrine(main, fam, top_name)

    notes = []
    if warships == 0:
        notes.append('You have no warships of this type yet — start building the cheapest '
                     'hull and an anchorage starbase to grow naval capacity.')
    notes.append(doctrine)
    if 8 in unlocked:
        notes.append('Titans are powerful but capacity-capped — keep only a handful and use '
                     'their auras to buff the rest of the fleet.')
    # Capital ships outside the main line.
    if not bio:
        if 'tech_juggernaut' in techs and not comp.get('juggernaut'):
            notes.append('You can build a Juggernaut (mobile shipyard/flagship) — one is a '
                         'big late-game force multiplier.')
        if comp.get('colossus'):
            notes.append('You have a Colossus — use it to crack key enemy worlds.')
    notes.append('Raise naval capacity with anchorages (+ Crew Quarters), the Supremacy '
                 'tradition tree and fleet-size doctrine techs.')

    return {
        'doctrine': doctrine,
        'tier': _pretty(top_name),
        'family': fam,
        'data_source': 'game files' if gamedata.is_loaded() else 'built-in defaults',
        'used_naval_capacity': round(player.get('used_naval_capacity', 0) or 0),
        'current_naval_capacity': round(current_naval_capacity),
        'recommended_naval_capacity': round(recommended_naval_capacity),
        'warships': warships,
        'rows': rows,
        'notes': [n for n in notes if n],
    }


def _doctrine(main, fam, top_name):
    pretty = _pretty(top_name)
    if main <= 1:
        return (f'Swarm era — win with sheer numbers of cheap {pretty}s. Pile them on and '
                f'out-number the enemy.')
    if main == 2:
        return (f'Add {pretty}s to your swarm for point-defense and picket duty against '
                f'missiles and strike craft.')
    if main == 3:
        return (f'{pretty}s become your main line; keep the cheaper hulls as a screen and '
                f'for point-defense.')
    return (f'{pretty}s are your damage. Screen them with a mix of the two cheapest hulls to '
            f'soak strike craft and missiles, and add a few titans for their fleet auras.')
