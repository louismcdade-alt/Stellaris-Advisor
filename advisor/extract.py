"""
Turn a Stellaris .sav file into a clean structured snapshot.

We only parse the sections we need (country list, plus the top-level date and
player pointer), so even a 20+ MB gamestate processes in about a second.
"""

import zipfile
import re
import os

from .clausewitz import parse, extract_block


# Resource keys we care about, in display order.
RESOURCE_KEYS = [
    'energy', 'minerals', 'food', 'consumer_goods', 'alloys',
    'influence', 'unity', 'physics_research', 'society_research',
    'engineering_research', 'rare_crystals', 'volatile_motes',
    'exotic_gases', 'sr_dark_matter', 'sr_living_metal', 'sr_zro',
    'nanites', 'minor_artifacts',
]


def _read_gamestate(sav_path):
    with zipfile.ZipFile(sav_path) as z:
        return z.read('gamestate').decode('utf-8', 'replace')


_KEY_PREFIX = re.compile(
    r'^(EMPIRE_DESIGN_|PRESCRIPTED_(adjective|species_name|species_plural)_|SPEC_|'
    r'NAME_|SPECIES_)', re.IGNORECASE)


def _tidy_key(key):
    """Turn a localization key like 'SPEC_Prossnakan' into 'Prossnakan'."""
    if not isinstance(key, str):
        return ''
    s = _KEY_PREFIX.sub('', key)
    s = s.replace('_', ' ').strip()
    # Keep already-readable words as-is; title-case ALLCAPS or snake fragments.
    if s.isupper() or '_' in key:
        s = s.title()
    return s


def _resolve_token(value):
    """Resolve a name-variable value (which is itself a name block) to text."""
    if isinstance(value, str):
        return _tidy_key(value)
    if isinstance(value, dict):
        if 'literal' in value and isinstance(value['literal'], str):
            return value['literal']
        # A value can carry its own nested variables.
        if 'variables' in value:
            return _resolve_name(value)
        if 'key' in value:
            return _tidy_key(value['key'])
    return ''


def _resolve_name(name):
    """Best-effort readable empire name from a Stellaris name block.

    Handles plain strings, {key:"..."} designs, and the common AI form where a
    template key like "%ADJECTIVE%" is filled from a `variables` list. Returns
    '' if nothing usable is found (caller assigns a fallback label).
    """
    if isinstance(name, str):
        return name.strip()
    if not isinstance(name, dict):
        return ''

    template = name.get('key', '')
    variables = name.get('variables')

    # Build {var_name: resolved_text} from the variables list.
    var_map = {}
    if isinstance(variables, dict):
        variables = [variables]
    if isinstance(variables, list):
        for v in variables:
            if isinstance(v, dict) and 'key' in v:
                var_map[str(v['key']).lower()] = _resolve_token(v.get('value', ''))

    if var_map:
        # Substitute %PLACEHOLDER% tokens (case-insensitive) in the template.
        def sub(m):
            return var_map.get(m.group(1).lower(), '')

        if isinstance(template, str) and '%' in template:
            out = re.sub(r'%([A-Za-z0-9_]+)%', sub, template).strip()
            out = re.sub(r'\s+', ' ', out)
            if out:
                return out
        # No usable template: join adjective-then-rest in a sensible order.
        ordered = []
        if 'adjective' in var_map:
            ordered.append(var_map['adjective'])
        for k in sorted(k for k in var_map if k != 'adjective'):
            ordered.append(var_map[k])
        joined = ' '.join(t for t in ordered if t).strip()
        if joined:
            return joined

    # No variables — just tidy the template/design key.
    return _tidy_key(template)


def _num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _count(v):
    """Length of a save list field, tolerating scalars/None/dicts."""
    if isinstance(v, list):
        return len(v)
    if isinstance(v, dict):
        return len(v)
    return 0


def _aslist(v):
    if isinstance(v, list):
        return v
    if v is None:
        return []
    return [v]


def _balance(country):
    """Net resource flow last month: {resource: float}. Positive = surplus.

    The save stores balance as {category: {resource: amount}}, so we sum every
    category to get the net per-resource flow the player actually sees.
    """
    budget = country.get('budget', {})
    if not isinstance(budget, dict):
        return {}
    month = budget.get('last_month') or budget.get('current_month') or {}
    bal = month.get('balance', {}) if isinstance(month, dict) else {}
    totals = {}
    if isinstance(bal, dict):
        for category in bal.values():
            if isinstance(category, dict):
                for res, amt in category.items():
                    totals[res] = totals.get(res, 0.0) + _num(amt)
    return {k: round(v, 2) for k, v in totals.items()}


def _resources(country):
    mods = country.get('modules', {})
    econ = mods.get('standard_economy_module', {}) if isinstance(mods, dict) else {}
    res = econ.get('resources', {}) if isinstance(econ, dict) else {}
    return {k: _num(v) for k, v in res.items()} if isinstance(res, dict) else {}


# Mobile warship hull classes we track, in tech progression order.
WARSHIP_CLASSES = ['corvette', 'frigate', 'destroyer', 'cruiser',
                   'battleship', 'titan', 'juggernaut', 'colossus']


def _owned_fleet_ids(country):
    fm = country.get('fleets_manager', {})
    out = set()
    if isinstance(fm, dict):
        for f in _aslist(fm.get('owned_fleets')):
            if isinstance(f, dict) and f.get('fleet') is not None:
                try:
                    out.add(int(f['fleet']))
                except (TypeError, ValueError):
                    pass
    return out


def _fleet_composition(gs, owned_ids):
    """Count the player's ships by hull size (ship_size), for owned ships.

    Walks ship_design (id -> ship_size) then the ships section (ship -> fleet +
    design). To stay fast on huge late-game saves we never slice big entries: we
    search within position windows, rejecting non-owned ships after reading just
    the entry header. Bioship growth stages (e.g. stinger_stage_2) are normalised
    to their base hull. Classification into warships/tiers happens in fleet.py.
    """
    counts = {}
    if not owned_ids:
        return counts

    # design id -> ship_size
    sd, _ = extract_block(gs, 'ship_design')
    design_size = {}
    if sd:
        size_re = re.compile(r'ship_size="([a-z0-9_]+)"')
        for m in re.finditer(r'\n\t(\d+)=\n\t\{', sd):
            sm = size_re.search(sd, m.end(), m.end() + 800)
            if sm:
                try:
                    design_size[int(m.group(1))] = sm.group(1)
                except ValueError:
                    pass

    sb, _ = extract_block(gs, 'ships')
    if not sb:
        return counts
    starts = [m.start() for m in re.finditer(r'\n\t(\d+)=\n\t\{', sb)]
    starts.append(len(sb))
    fleet_re = re.compile(r'fleet=(\d+)')
    design_re = re.compile(r'design=(\d+)')
    for i in range(len(starts) - 1):
        s, e = starts[i], starts[i + 1]
        fm = fleet_re.search(sb, s, min(s + 150, e))
        if not fm or int(fm.group(1)) not in owned_ids:
            continue
        k = sb.find('ship_design_implementation', s, e)
        if k < 0:
            continue
        dm = design_re.search(sb, k, min(k + 80, e))
        if not dm:
            continue
        size = design_size.get(int(dm.group(1)))
        if size:
            size = re.sub(r'_stage_\d+$', '', size)   # normalise bioship stages
            counts[size] = counts.get(size, 0) + 1
    return counts


def compute_fleet(sav_path, owned_ids):
    """On-demand ship composition for a save (reads the gamestate fresh).

    Returns {'composition': {ship_size: count}} for the player's ships. Filtering
    to actual warships and tier classification is done in fleet.py using the
    live game data.
    """
    gs = _read_gamestate(sav_path)
    return {'composition': _fleet_composition(gs, owned_ids)}


def _researched_techs(country):
    """Set of researched technology ids from tech_status."""
    ts = country.get('tech_status', {})
    if not isinstance(ts, dict):
        return []
    techs = ts.get('technology')
    techs = techs if isinstance(techs, list) else ([techs] if techs else [])
    return [t for t in techs if isinstance(t, str)]


def _tech_queue(country):
    """Currently-researching tech per field, if present."""
    out = {}
    for field in ('physics', 'society', 'engineering'):
        q = country.get(f'tech_status', {})
        # The active research is in tech_status under '<field>_queue' in some
        # versions; fall back gracefully.
    ts = country.get('tech_status', {})
    if isinstance(ts, dict):
        for field in ('physics', 'society', 'engineering'):
            queue = ts.get(f'{field}_queue')
            if isinstance(queue, dict):
                out[field] = queue.get('technology') or queue.get('tech')
            elif isinstance(queue, list) and queue:
                first = queue[0]
                if isinstance(first, dict):
                    out[field] = first.get('technology') or first.get('tech')
    return out


def _relations(country):
    """List of (target_country_id, dict-of-flags) describing diplomatic stance."""
    rm = country.get('relations_manager', {})
    if not isinstance(rm, dict):
        return []
    rel = rm.get('relation', [])
    if isinstance(rel, dict):
        rel = [rel]
    out = []
    for r in rel:
        if not isinstance(r, dict):
            continue
        out.append({
            'country': r.get('country'),
            'truce': r.get('truce'),
            'hostile': r.get('hostile'),
            'is_rival': bool(r.get('is_rival')),
            'communications': bool(r.get('communications')),
            'alliance': bool(r.get('alliance')),
            'borders': bool(r.get('borders')),
        })
    return out


def _identity(country, species_db):
    """Raw identity fields: ethics, authority, civics, origin, founder traits.

    Interpretation (gestalt? genocidal? trade-focused?) happens in profile.py;
    here we just collect the facts from the save.
    """
    gov = country.get('government', {})
    gov = gov if isinstance(gov, dict) else {}
    ethos = country.get('ethos', {})
    ethics = _aslist(ethos.get('ethic')) if isinstance(ethos, dict) else []

    # Founder species traits.
    traits, sp_class, sp_name = [], None, None
    fid = country.get('founder_species_ref')
    if fid is not None:
        sp = species_db.get(str(fid)) or species_db.get(fid)
        if isinstance(sp, dict):
            sp_class = sp.get('class')
            sp_name = _resolve_name(sp.get('name'))
            tr = sp.get('traits', {})
            if isinstance(tr, dict):
                traits = _aslist(tr.get('trait'))

    return {
        'ethics': ethics,
        'authority': gov.get('authority'),
        'government_type': gov.get('type'),
        'origin': gov.get('origin'),
        'civics': _aslist(gov.get('civics')),
        'species_class': sp_class,
        'species_name': sp_name,
        'species_traits': traits,
        'tradition_trees': [t for t in _aslist(country.get('tradition_categories'))
                            if isinstance(t, str)],
    }


def build_snapshot(sav_path):
    """Parse a save and return a dict of everything the advisor needs."""
    gs = _read_gamestate(sav_path)

    # Top-level date.
    m = re.search(r'\ndate="([0-9.]+)"', gs)
    date = m.group(1) if m else '????'

    # Player's country id.
    player_block, _ = extract_block(gs, 'player')
    pid = '0'
    if player_block:
        pm = re.search(r'country=(\d+)', player_block)
        if pm:
            pid = pm.group(1)

    # Parse the country dictionary only.
    cb, _ = extract_block(gs, 'country')
    countries_raw = parse(cb[1:-1]) if cb else {}

    # Species database (small) — used to read the founder species' traits.
    sdb_block, _ = extract_block(gs, 'species_db')
    species_db = parse(sdb_block[1:-1]) if sdb_block else {}

    empires = {}
    for cid, c in countries_raw.items():
        if not isinstance(c, dict) or 'military_power' not in c:
            continue
        ctype = c.get('type') or c.get('country_type')
        empires[cid] = {
            'id': cid,
            'name': _resolve_name(c.get('name')) or f'Empire {cid}',
            'type': ctype,
            'military_power': _num(c.get('military_power')),
            'economy_power': _num(c.get('economy_power')),
            'tech_power': _num(c.get('tech_power')),
            'victory_rank': c.get('victory_rank'),
            'victory_score': _num(c.get('victory_score')),
            'colonies': _count(c.get('owned_planets')),
            'empire_size': _num(c.get('empire_size')),
        }

    player_raw = countries_raw.get(pid, {})
    player = {
        'id': pid,
        'name': _resolve_name(player_raw.get('name')),
        'resources': _resources(player_raw),
        'balance': _balance(player_raw),
        'military_power': _num(player_raw.get('military_power')),
        'economy_power': _num(player_raw.get('economy_power')),
        'tech_power': _num(player_raw.get('tech_power')),
        'victory_rank': player_raw.get('victory_rank'),
        'tech_queue': _tech_queue(player_raw),
        'researched_techs': _researched_techs(player_raw),
        'relations': _relations(player_raw),
        'colonies': _count(player_raw.get('owned_planets')),
        'empire_size': _num(player_raw.get('empire_size')),
        'used_naval_capacity': _num(player_raw.get('used_naval_capacity')),
        'owned_fleet_ids': sorted(_owned_fleet_ids(player_raw)),
        'leaders': _count(player_raw.get('owned_leaders')),
        'starbase_capacity': _num(player_raw.get('starbase_capacity')),
        'ascension_perks': [a for a in _aslist(player_raw.get('ascension_perks'))
                            if isinstance(a, str)],
        'traditions': _count(player_raw.get('traditions')),
        'tradition_categories': _count(player_raw.get('tradition_categories')),
        'tradition_trees': [t for t in _aslist(player_raw.get('tradition_categories'))
                            if isinstance(t, str)],
        'edicts': [e.get('edict') for e in _aslist(player_raw.get('edicts'))
                   if isinstance(e, dict) and e.get('edict')],
        'in_federation': bool(player_raw.get('federation')),
        'war_allies': _aslist(player_raw.get('war_allies')),
        'last_date_at_war': player_raw.get('last_date_at_war'),
        'government': (player_raw.get('government') or {}).get('type')
                      if isinstance(player_raw.get('government'), dict) else None,
        'ethics': _aslist((player_raw.get('ethos') or {}).get('ethic'))
                  if isinstance(player_raw.get('ethos'), dict) else [],
        'identity': _identity(player_raw, species_db),
    }

    return {
        'date': date,
        'save_file': os.path.basename(sav_path),
        'player': player,
        'empires': empires,
    }
