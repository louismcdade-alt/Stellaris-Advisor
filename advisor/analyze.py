"""
Heuristic advice engine.

Takes a snapshot (from extract.build_snapshot) and returns a list of advice
items. Each item:

    {'priority': 'critical'|'warning'|'info'|'good',
     'category': 'economy'|'military'|'diplomacy'|'research',
     'title': short headline,
     'detail': one or two sentences of explanation}

These are rules of thumb, not a solver. They aim to catch the things a player
most often forgets between autosaves: a resource about to bottom out, a
neighbour that has outgrown your fleet, an empty research slot, an unmet ally.
"""

from .profile import EmpireProfile
from .knowledge import origin_civic_cards, ascension_cards

PRIORITY_ORDER = {'critical': 0, 'warning': 1, 'info': 2, 'good': 3}


def _profile(snap):
    """Build (once) and cache the empire profile on the snapshot."""
    prof = snap.get('_profile')
    if prof is None:
        prof = EmpireProfile(snap['player'].get('identity'))
        snap['_profile'] = prof
    return prof

# Stockpiles below this many months of runway (at current drain) are flagged.
RUNWAY_WARN_MONTHS = 12
RUNWAY_CRIT_MONTHS = 4

# Strategic resources that gate ship components / buildings.
STRATEGIC = ['volatile_motes', 'exotic_gases', 'rare_crystals',
             'sr_dark_matter', 'sr_living_metal', 'sr_zro', 'nanites']


def _fmt(n):
    return f'{n:+.0f}' if abs(n) >= 1 else f'{n:+.1f}'


def _date_to_days(d):
    """Stellaris date 'YYYY.MM.DD' -> rough day count for comparisons."""
    try:
        y, m, day = (int(x) for x in str(d).split('.'))
        return y * 360 + m * 30 + day
    except (ValueError, AttributeError):
        return None


def _years_since(then, now):
    a, b = _date_to_days(then), _date_to_days(now)
    if a is None or b is None:
        return None
    return (b - a) / 360.0


def _rank(value, others):
    """1-based rank of `value` within [value, *others] sorted high-to-low."""
    ranked = sorted([value] + list(others), reverse=True)
    return ranked.index(value) + 1, len(ranked)


def _defaults(snap):
    p = snap['player']
    return [e for e in snap['empires'].values()
            if e['type'] == 'default' and e['id'] != p['id']]


def analyze_standing(snap):
    """Compare the player across military / economy / tech and surface the
    dimension they're weakest in — the thing most likely to lose them the game."""
    out = []
    p = snap['player']
    rivals = _defaults(snap)
    if not rivals:
        return out

    dims = [
        ('economy', 'economy_power', 'economy', 'Grow production: settle/develop planets, '
         'fill jobs, and build more districts and resource buildings.'),
        ('tech', 'tech_power', 'technology', 'Boost research: build labs, staff researcher '
         'jobs, and keep all three research slots busy.'),
        ('military', 'military_power', 'fleet power', 'Build more ships and upgrade designs '
         'with your latest tech, and raise naval capacity.'),
    ]
    ranks = {}
    for name, key, _, _ in dims:
        r, total = _rank(p.get(key, 0), [e[key] for e in rivals])
        ranks[name] = (r, total)

    # Headline: which dimension is the player worst at, relative to the field.
    worst = max(dims, key=lambda d: ranks[d[0]][0])
    wname, wkey, wlabel, wfix = worst
    wr, total = ranks[wname]
    best = min(dims, key=lambda d: ranks[d[0]][0])
    br = ranks[best[0]][0]

    # Only flag if there's a real imbalance (weak in one area, strong in another).
    if wr >= max(2, total // 2 + 1) and wr - br >= 2:
        pr = 'warning' if wr > (total * 0.6) else 'info'
        out.append({
            'priority': pr, 'category': wname if wname != 'tech' else 'research',
            'title': f'Lagging in {wlabel} (rank {wr}/{total})',
            'detail': f'You rank {br}/{total} in {best[2]} but only {wr}/{total} in {wlabel}. '
                      f'{wfix}'})
    return out


def analyze_expansion(snap):
    """Colony count vs the field — are you expanding fast enough?"""
    out = []
    p = snap['player']
    rivals = _defaults(snap)
    mine = p.get('colonies', 0)
    if not rivals or mine == 0:
        return out
    counts = sorted([e.get('colonies', 0) for e in rivals], reverse=True)
    median = counts[len(counts) // 2]
    leader = counts[0]

    if mine < median - 2:
        out.append({
            'priority': 'warning', 'category': 'expansion',
            'title': f'Behind on expansion ({mine} colonies)',
            'detail': f'Rivals hold a median of {median} (top empire {leader}). More planets '
                      f'means more pops, production and research. Colonise habitable worlds, '
                      f'build colony ships, or take systems by force/claims.'})
    elif mine >= leader and leader > 0:
        out.append({
            'priority': 'good', 'category': 'expansion',
            'title': f'Widest empire in the galaxy ({mine} colonies)',
            'detail': 'Make sure each colony is developed and not dragging your economy with '
                      'upkeep — build admin/bureaucrat capacity to offset sprawl.'})
    return out


def analyze_economy(snap):
    out = []
    p = snap['player']
    prof = _profile(snap)
    res = p['resources']
    bal = dict(p['balance'])

    # Default trade policy routes trade value to energy credits; fold it in so
    # we don't false-alarm on energy when trade more than covers it. Gestalts
    # have no trade, so this is simply the energy balance for them.
    eff_energy = bal.get('energy', 0) + (bal.get('trade', 0) if prof.uses_trade() else 0)

    # Core economy resources to check — but only the ones this empire type uses.
    checks = [
        ('energy', 'Energy credits', eff_energy),
        ('minerals', 'Minerals', bal.get('minerals', 0)),
        ('alloys', 'Alloys', bal.get('alloys', 0)),
    ]
    if prof.uses_food():
        checks.append(('food', 'Food', bal.get('food', 0)))
    if prof.uses_consumer_goods():
        checks.append(('consumer_goods', 'Consumer goods', bal.get('consumer_goods', 0)))

    # Runway checks on the core economy resources.
    for key, label, flow in checks:
        stock = res.get(key, 0)
        if flow < -0.5:
            months = stock / -flow if flow < 0 else 999
            if months <= RUNWAY_CRIT_MONTHS:
                out.append({
                    'priority': 'critical', 'category': 'economy',
                    'title': f'{label} running out (~{months:.0f} mo left)',
                    'detail': f'Net {_fmt(flow)}/mo with {stock:.0f} in reserve. '
                              f'Build more production or cut upkeep before it hits zero '
                              f'and cripples your empire.'})
            elif months <= RUNWAY_WARN_MONTHS:
                out.append({
                    'priority': 'warning', 'category': 'economy',
                    'title': f'{label} trending negative ({_fmt(flow)}/mo)',
                    'detail': f'{stock:.0f} stockpiled, ~{months:.0f} months of runway. '
                              f'Queue more {label.lower()} production soon.'})

    # Influence sitting at cap is wasted.
    infl = res.get('influence', 0)
    if infl >= 990:
        out.append({
            'priority': 'info', 'category': 'economy',
            'title': 'Influence at cap (wasted)',
            'detail': 'You are at/near the 1000 influence cap. Spend it: claim systems, '
                      'enact edicts, or recruit/assign envoys.'})

    # Big alloy surplus with a stockpile cap nearby = build more ships/buildings.
    if res.get('alloys', 0) >= 18000:
        out.append({
            'priority': 'info', 'category': 'economy',
            'title': 'Alloys piling up',
            'detail': f"{res['alloys']:.0f} alloys banked. Convert it into fleet or "
                      f"starbase upgrades rather than letting it sit."})

    # Strategic resource shortfalls (negative flow, low stock).
    for key in STRATEGIC:
        flow = bal.get(key, 0)
        stock = res.get(key, 0)
        if flow < -0.1 and stock < 50:
            out.append({
                'priority': 'warning', 'category': 'economy',
                'title': f'{key.replace("sr_", "").replace("_", " ").title()} shortage',
                'detail': f'Net {_fmt(flow)}/mo, only {stock:.0f} left. Secure a source or '
                          f'reduce buildings/components that consume it.'})

    if not out:
        out.append({
            'priority': 'good', 'category': 'economy',
            'title': 'Economy stable',
            'detail': 'No resource is trending toward zero. Consider investing surpluses '
                      'into growth (districts, buildings, fleet).'})
    return out


# Founder-species traits worth a tip: (category, title, detail). Not every
# trait needs advice — just the ones that should noticeably steer a build.
SPECIES_TRAIT_TIPS = {
    'trait_intelligent': ('research', 'Intelligent species — lean into research jobs',
                          'Your founder species researches faster. Prioritise researcher '
                          'jobs and labs to make the most of it.'),
    'trait_agrarian': ('economy', 'Agrarian species — favour farming districts',
                       'Your founder species produces more food per farmer. Lean into '
                       'agriculture districts and food buildings.'),
    'trait_industrious': ('economy', 'Industrious species — mineral-heavy build',
                          'Your founder species mines more minerals per miner. Lean into '
                          'mining districts and mineral buildings.'),
    'trait_thrifty': ('economy', 'Thrifty species — favour energy jobs',
                      'Your founder species produces more energy per technician. Lean into '
                      'energy districts and generator buildings.'),
    'trait_charismatic': ('diplomacy', 'Charismatic species — lean on envoys',
                          'Your founder species is more persuasive. Use envoys for opinion '
                          'and diplomatic weight.'),
}


def analyze_species(snap):
    """Tips driven by the founder species' traits (e.g. Intelligent -> research)."""
    prof = _profile(snap)
    out = []
    for trait in prof.traits:
        tip = SPECIES_TRAIT_TIPS.get(trait)
        if tip:
            category, title, detail = tip
            out.append({'priority': 'info', 'category': category, 'title': title,
                        'detail': detail})
    return out


def analyze_military(snap):
    out = []
    p = snap['player']
    prof = _profile(snap)
    my_mil = p['military_power']

    rivals = [e for e in snap['empires'].values()
              if e['type'] == 'default' and e['id'] != p['id']]
    rivals.sort(key=lambda e: -e['military_power'])

    if rivals:
        strongest = rivals[0]
        ranked = sorted([my_mil] + [r['military_power'] for r in rivals], reverse=True)
        my_rank = ranked.index(my_mil) + 1
        total = len(ranked)

        if strongest['military_power'] > my_mil * 1.3:
            out.append({
                'priority': 'warning', 'category': 'military',
                'title': f'{strongest["name"]} outguns you',
                'detail': f'Their fleet power {strongest["military_power"]:.0f} vs your '
                          f'{my_mil:.0f}. Avoid provoking them and prioritise fleet/tech, '
                          f'or secure a defensive alliance.'})
        elif my_rank == 1:
            if prof.pacifist:
                tip = ('As a Pacifist you can\'t start offensive wars, so use this strength '
                       'defensively and from a position of safety while you build tall.')
            elif prof.no_diplomacy or prof.militarist:
                tip = 'Press it now — declare on a weaker neighbour before they catch up.'
            else:
                tip = 'A good window to claim territory or pressure a weaker neighbour.'
            out.append({
                'priority': 'good', 'category': 'military',
                'title': 'Strongest military among rivals',
                'detail': f'You lead {total} empires at {my_mil:.0f} fleet power. {tip}'})
        else:
            out.append({
                'priority': 'info', 'category': 'military',
                'title': f'Military rank {my_rank} of {total}',
                'detail': f'Your fleet power {my_mil:.0f}. Strongest rival '
                          f'{strongest["name"]} at {strongest["military_power"]:.0f}.'})

    # Active / recent war.
    war_age = _years_since(p.get('last_date_at_war'), snap.get('date'))
    if war_age is not None and war_age <= 1.0:
        allies = len(p.get('war_allies', []))
        ally_txt = f' You have {allies} war ally/allies — coordinate your fleets.' if allies else ''
        out.append({
            'priority': 'warning', 'category': 'military',
            'title': 'Currently at war',
            'detail': f'You were at war as recently as {p.get("last_date_at_war")}. Keep your '
                      f'main fleet repaired and concentrated, defend choke-point starbases, and '
                      f'watch war exhaustion.{ally_txt}'})

    # Fallen empires: catastrophically strong, leave alone.
    fes = [e for e in snap['empires'].values() if e['type'] == 'fallen_empire']
    if fes:
        strongest_fe = max(fes, key=lambda e: e['military_power'])
        if strongest_fe['military_power'] > my_mil * 3:
            out.append({
                'priority': 'info', 'category': 'military',
                'title': 'Fallen Empire nearby — do not provoke',
                'detail': f'A Fallen Empire fields ~{strongest_fe["military_power"]:.0f} '
                          f'fleet power (many times yours). Respect their borders and '
                          f'demands until you have a late-game fleet.'})
    return out


def analyze_diplomacy(snap):
    out = []
    p = snap['player']
    prof = _profile(snap)
    empires = snap['empires']
    rels = p['relations']

    # Genocidal empires have no diplomacy at all, and Driven Assimilators are
    # hostile to non-gestalts — the identity card already says so; don't suggest
    # pacts they can never sign.
    if prof.no_diplomacy or prof.assimilator:
        return out

    known = [r for r in rels if r.get('communications')]
    rivals = [r for r in rels if r.get('is_rival')]
    allies = [r for r in rels if r.get('alliance')]

    def name_of(cid):
        e = empires.get(str(cid))
        return e['name'] if e else f'Empire {cid}'

    if rivals:
        out.append({
            'priority': 'info', 'category': 'diplomacy',
            'title': f'{len(rivals)} active rival(s)',
            'detail': 'Rivalries give influence but block cooperation: '
                      + ', '.join(name_of(r['country']) for r in rivals) + '.'})

    if not allies and len(known) >= 2 and not prof.inward:
        # Suggest the strongest non-rival contact as an ally candidate.
        # (Inward Perfection empires shun alliances, so skip this for them.)
        candidates = []
        for r in known:
            if r.get('is_rival'):
                continue
            e = empires.get(str(r['country']))
            if e and e['type'] == 'default':
                candidates.append(e)
        candidates.sort(key=lambda e: -e['military_power'])
        if candidates:
            best = candidates[0]
            out.append({
                'priority': 'info', 'category': 'diplomacy',
                'title': 'No allies yet — consider a defensive pact',
                'detail': f'{best["name"]} ({best["military_power"]:.0f} fleet power) is a '
                          f'strong non-rival contact. A defensive pact or federation would '
                          f'deter aggression.'})

    if allies:
        out.append({
            'priority': 'good', 'category': 'diplomacy',
            'title': f'{len(allies)} ally/allies',
            'detail': 'Allied with ' + ', '.join(name_of(r['country']) for r in allies)
                      + '. Coordinate wars and share intel.'})

    if not out:
        out.append({
            'priority': 'info', 'category': 'diplomacy',
            'title': 'Few diplomatic contacts',
            'detail': 'Send science ships and envoys to make contact and open trade/research '
                      'agreements with neighbours.'})
    return out


def analyze_research(snap):
    out = []
    queue = snap['player'].get('tech_queue', {})
    fields = {'physics': 'Physics', 'society': 'Society', 'engineering': 'Engineering'}
    empty = [label for key, label in fields.items() if not queue.get(key)]

    if empty:
        out.append({
            'priority': 'warning', 'category': 'research',
            'title': f'Idle research: {", ".join(empty)}',
            'detail': 'One or more research slots may be empty or finishing — pick the next '
                      'tech so you never waste research output.'})
    else:
        researching = ', '.join(
            f'{fields[k]}: {v.replace("tech_", "").replace("_", " ")}'
            for k, v in queue.items() if v)
        if researching:
            out.append({
                'priority': 'good', 'category': 'research',
                'title': 'All research slots active',
                'detail': researching + '.'})
    return out


def analyze_progression(snap):
    """Empire-building progress: ascension perks and leadership."""
    out = []
    p = snap['player']
    perks = len(p.get('ascension_perks', []))
    unity = p.get('resources', {}).get('unity', 0)

    # Ascension perks are powerful permanent bonuses; idle unity that could buy
    # the next one is a missed opportunity.
    if perks < 8 and unity >= 3000:
        out.append({
            'priority': 'info', 'category': 'progression',
            'title': f'Unity banked — {perks}/8 ascension perks taken',
            'detail': f'{unity:.0f} unity stored. Finish a tradition tree to unlock the next '
                      f'ascension perk rather than letting unity sit unused.'})

    # Edicts cost upkeep but are usually worth running if you can afford them.
    if not p.get('edicts'):
        out.append({
            'priority': 'info', 'category': 'progression',
            'title': 'No edicts active',
            'detail': 'Edicts give strong empire-wide bonuses. If you have spare energy/unity, '
                      'enable one (e.g. research, unity or production edicts).'})
    return out


def analyze_identity(snap):
    """A single tailored card describing how to play to this empire's strengths."""
    prof = _profile(snap)
    card = prof.identity_advice()
    if not card:
        return []
    category, title, detail = card
    return [{'priority': 'info', 'category': category, 'title': title, 'detail': detail}]


def analyze_origin_civics(snap):
    """Tips specific to the empire's origin and signature civics."""
    prof = _profile(snap)
    return [{'priority': 'info', 'category': cat, 'title': title, 'detail': detail}
            for cat, title, detail in origin_civic_cards(prof)]


def analyze_ascension(snap):
    """Read current ascension progress and recommend a path / next perks."""
    prof = _profile(snap)
    perks = snap['player'].get('ascension_perks', [])
    techs = snap['player'].get('researched_techs', [])
    dlc = (snap.get('dlc') or {}).get('names')
    return [{'priority': 'info', 'category': cat, 'title': title, 'detail': detail}
            for cat, title, detail in ascension_cards(prof, perks, techs, dlc)]


def analyze(snap):
    """Return all advice items, sorted by priority then category."""
    items = []
    items += analyze_identity(snap)
    items += analyze_origin_civics(snap)
    items += analyze_ascension(snap)
    items += analyze_economy(snap)
    items += analyze_species(snap)
    items += analyze_standing(snap)
    items += analyze_expansion(snap)
    items += analyze_military(snap)
    items += analyze_diplomacy(snap)
    items += analyze_research(snap)
    items += analyze_progression(snap)
    items.sort(key=lambda x: (PRIORITY_ORDER.get(x['priority'], 9), x['category']))
    return items
