"""
Validate Empire Builder builds against the installed game files.

Checks, per build, that every element is actually usable:
  * civics exist, suit the build's authority (regular / gestalt hive|machine /
    corporate), and don't conflict with the build's ethics (e.g. a civic gated
    on Authoritarian ethics picked for an Egalitarian build),
  * the origin exists,
  * each species trait exists AND is selectable at empire creation for a normal
    biological species (not ascension/cyborg/robotic/shroud, and not locked to a
    specific phenotype via species_class), no two selected traits are
    mutually-exclusive `opposites` (e.g. Rapid Breeders + Slow Breeders), and
    their net `cost` doesn't exceed the default starting trait-point budget.

Catalogs are read once from the install (cached). If the install can't be found
we report 'unknown' rather than failing builds. This is the same logic the
standalone audit_builds.py uses, exposed so the app can show a live "verified"
badge in the builder.

Note: current-patch civic files gate ethics via `ethics = { OR = { value =
ethic_x } }` (require any of) and `ethics = { NOT/NOR = { value = ethic_x } }`
(exclude), not the older `has_ethic = ethic_x` syntax — we parse the format
actually present in the install.
"""

import os
import re
import glob

from .dlc import find_install

_cache = None


def _catalogs():
    global _cache
    if _cache is not None:
        return _cache
    install = find_install()
    data = {'install': install, 'civic_names': {}, 'civic_cat': {}, 'civic_ethics': {},
            'origin_names': {}, 'trait_names': {}, 'trait_info': {}}
    if install:
        _load_loc(install, data)
        _load_civic_categories(install, data)
        _load_traits(install, data)
    _cache = data
    return _cache


def _load_loc(install, data):
    pat = re.compile(r'^\s*(civic_[a-z0-9_]+|origin_[a-z0-9_]+|trait_[a-z0-9_]+)'
                     r':\d*\s*"(.*?)"', re.M)
    for path in glob.glob(os.path.join(install, 'localisation', 'english', '*.yml')):
        try:
            text = open(path, encoding='utf-8-sig', errors='replace').read()
        except OSError:
            continue
        for m in pat.finditer(text):
            key, name = m.group(1), m.group(2)
            bucket = ('civic_names' if key.startswith('civic_') else
                      'origin_names' if key.startswith('origin_') else 'trait_names')
            data[bucket].setdefault(_norm(name), set()).add(key)


def _load_civic_categories(install, data):
    base = os.path.join(install, 'common', 'governments', 'civics')
    files = {'00_civics.txt': 'regular', '02_gestalt_civics.txt': 'gestalt',
             '03_corporate_civics.txt': 'corporate'}
    for fn, cat in files.items():
        path = os.path.join(base, fn)
        if not os.path.isfile(path):
            continue
        text = open(path, encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'^(civic_[a-z0-9_]+)\s*=\s*\{', text, re.M):
            cid, c = m.group(1), cat
            if cat == 'gestalt':
                c = ('gestalt-hive' if 'hive' in cid else
                     'gestalt-machine' if 'machine' in cid else 'gestalt-any')
            data['civic_cat'][cid] = c
            required, excluded = _ethic_requirements(_block(text, m.start()))
            if required or excluded:
                data['civic_ethics'][cid] = (required, excluded)


def _ethic_requirements(block):
    """Scan a civic's full block text for `ethics = { ... }` sub-blocks and
    split each into (required_any, excluded) ethic id sets — exclusions are
    whatever sits inside a nested NOT/NOR, everything else (typically an OR,
    or a bare `value = ethic_x`) is a requirement."""
    required, excluded = set(), set()
    for m in re.finditer(r'ethics\s*=\s*\{', block):
        sub = _block(block, m.start())
        inner = sub[sub.index('{') + 1:sub.rindex('}')]
        stripped = inner
        for nm in re.finditer(r'(?:NOT|NOR)\s*=\s*\{', inner):
            excl_block = _block(inner, nm.start())
            excluded.update(re.findall(r'value\s*=\s*(ethic_[a-z_]+)', excl_block))
            stripped = stripped.replace(excl_block, '')
        required.update(re.findall(r'value\s*=\s*(ethic_[a-z_]+)', stripped))
    excluded.discard('ethic_gestalt_consciousness')  # redundant w/ authority filtering
    required.discard('ethic_gestalt_consciousness')
    return required, excluded


# Stellaris' fixed set of base ethics — unlike civics/traits/origins these are
# not DLC-dependent and have been stable for years, so (as profile.py already
# does for the reverse mapping) we hard-code the label<->id pairing instead of
# reading it from localisation, which has no single reliable ethic-name key.
_BASE_ETHIC_IDS = {
    'militarist': 'militarist', 'pacifist': 'pacifist',
    'xenophobe': 'xenophobe', 'xenophile': 'xenophile',
    'materialist': 'materialist', 'spiritualist': 'spiritualist',
    'authoritarian': 'authoritarian', 'egalitarian': 'egalitarian',
    'gestalt consciousness': 'gestalt_consciousness',
}


# Default species starting trait points. Not exposed as a simple literal in
# any data file (species_classes' species_trait_points field is documented
# but unset in the base game; civics/origins only ever *add* to it), so this
# is the well-known base-game default rather than something read live.
_TRAIT_POINT_BUDGET = 2


def _ethic_ok(required, excluded, have):
    if required and not (required & have):
        return False
    if excluded and (excluded & have):
        return False
    return True


def _build_ethic_ids(ethics):
    """Build's human-readable ethic labels (e.g. 'Fanatic Materialist') ->
    the ethic_xxx / ethic_fanatic_xxx ids the game files reference."""
    out = set()
    for label in ethics:
        low = label.lower()
        fanatic = low.startswith('fanatic ')
        base = _BASE_ETHIC_IDS.get(low[len('fanatic '):] if fanatic else low)
        if base:
            out.add(f'ethic_fanatic_{base}' if fanatic else f'ethic_{base}')
    return out


def _load_traits(install, data):
    folder = os.path.join(install, 'common', 'traits')
    nonstart = ('09_', '05_', '10_', '17_', '03_')
    paths = glob.glob(os.path.join(folder, '*species_traits*.txt')) + \
        glob.glob(os.path.join(folder, '*ascension_traits*.txt'))
    for path in paths:
        fn = os.path.basename(path)
        text = open(path, encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'^(trait_[a-z0-9_]+)\s*=\s*\{', text, re.M):
            block = _block(text, m.start())
            am = re.search(r'allowed_archetypes\s*=\s*\{([^}]*)\}', block)
            arch = set(am.group(1).split()) if am else set()
            sc = re.search(r'species_class\s*=\s*\{([^}]*)\}', block)
            locked = bool(sc) or any(p in fn for p in ('15_biogenesis',))
            nonstartable = fn.startswith(nonstart)
            startable = 'BIOLOGICAL' in arch and not nonstartable and not locked
            data['trait_info'][m.group(1)] = {
                'startable': startable, 'phenotype': locked, 'nonstart': nonstartable,
                'opposites': _trait_opposites(block), 'cost': _trait_cost(block)}


def _trait_cost(block):
    """A trait's top-level `cost = N` (positive for upgrades, negative for
    drawbacks) -> float, 0 if absent. Excludes `slave_cost`/other *_cost keys."""
    m = re.search(r'(?<![a-zA-Z_])cost\s*=\s*(-?\d+(?:\.\d+)?)', block)
    return float(m.group(1)) if m else 0.0


def _trait_opposites(block):
    """A trait's `opposites = { "trait_x" "trait_y" }` block -> the set of
    trait ids it can't be picked alongside."""
    m = re.search(r'opposites\s*=\s*\{', block)
    if not m:
        return set()
    sub = _block(block, m.start())
    return set(re.findall(r'"(trait_[a-z0-9_]+)"', sub))


def _traits_conflict(id_a, id_b, trait_info):
    a = trait_info.get(id_a, {})
    b = trait_info.get(id_b, {})
    return id_b in a.get('opposites', set()) or id_a in b.get('opposites', set())


def _block(text, at):
    s = text.index('{', at)
    depth, i, n = 0, s, len(text)
    while i < n:
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[s:i + 1]
        i += 1
    return text[s:]


def _norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def _authority_kind(authority):
    a = (authority or '').lower()
    if 'hive' in a:
        return 'hive'
    if 'machine' in a:
        return 'machine'
    if 'corp' in a:
        return 'corporate'
    return 'regular'


def _civic_ok(cats, kind):
    for c in cats:
        if kind == 'regular' and c == 'regular':
            return True
        if kind == 'corporate' and c in ('corporate', 'regular'):
            return True
        if kind == 'hive' and c in ('gestalt-hive', 'gestalt-any'):
            return True
        if kind == 'machine' and c in ('gestalt-machine', 'gestalt-any'):
            return True
    return False


def validate_build(build):
    """Return {'verified': bool, 'issues': [str], 'checked': bool}.

    `checked` is False when the game install couldn't be read (so we can't
    verify); in that case the build is treated as verified-unknown.
    """
    cat = _catalogs()
    if not cat['install'] or not cat['civic_names']:
        return {'verified': True, 'issues': [], 'checked': False}

    issues = []
    kind = _authority_kind(build['authority'])
    build_ethic_ids = _build_ethic_ids(build.get('ethics', []))

    for civ in build['civics']:
        name = re.sub(r'\s*[—-].*$', '', civ).strip()
        ids = cat['civic_names'].get(_norm(name))
        if not ids:
            issues.append(f'civic "{civ}" not found in game files')
            continue
        cats = {cat['civic_cat'].get(i, 'unknown') for i in ids}
        if not _civic_ok(cats, kind):
            issues.append(f'civic "{civ}" not available to a {build["authority"]} empire')
            continue

        # Ethic gate: only consider the id variant(s) actually selectable by
        # this authority kind, and accept if any of them is satisfied.
        relevant = [i for i in ids if _civic_ok({cat['civic_cat'].get(i, 'unknown')}, kind)]
        gated = [cat['civic_ethics'][i] for i in relevant if i in cat['civic_ethics']]
        if gated and not any(_ethic_ok(req, exc, build_ethic_ids) for req, exc in gated):
            req, exc = gated[0]
            if req and not (req & build_ethic_ids):
                issues.append(f'civic "{civ}" needs ethic(s): {", ".join(sorted(req))}')
            if exc and (exc & build_ethic_ids):
                conflict = sorted(exc & build_ethic_ids)
                issues.append(f'civic "{civ}" conflicts with ethic(s): {", ".join(conflict)}')

    oname = re.sub(r'\s*\(.*?\)|\s+or\s+.*$', '', build['origin']).strip()
    if not cat['origin_names'].get(_norm(oname)):
        issues.append(f'origin "{build["origin"]}" not found in game files')

    selected = []
    for tr in build['traits']:
        name = re.sub(r'\s*\(.*?\)|\s*—.*$', '', tr).strip()
        ids = cat['trait_names'].get(_norm(name))
        infos = [cat['trait_info'][i] for i in (ids or []) if i in cat['trait_info']]
        if not ids:
            issues.append(f'trait "{tr}" not found in game files')
        elif not any(t['startable'] for t in infos):
            if any(t['nonstart'] for t in infos):
                issues.append(f'trait "{tr}" is unlocked later, not pickable at start')
            elif any(t['phenotype'] for t in infos):
                issues.append(f'trait "{tr}" needs a specific species/phenotype')
            else:
                issues.append(f'trait "{tr}" not selectable for a biological species')
        else:
            rep = next((i for i in ids if cat['trait_info'].get(i, {}).get('startable')),
                       next(iter(ids)))
            selected.append((tr, rep))

    for i, (label_a, id_a) in enumerate(selected):
        for label_b, id_b in selected[i + 1:]:
            if _traits_conflict(id_a, id_b, cat['trait_info']):
                issues.append(f'traits "{label_a}" and "{label_b}" are opposites '
                               f'and cannot both be picked')

    net_cost = sum(cat['trait_info'].get(tid, {}).get('cost', 0.0) for _, tid in selected)
    if net_cost > _TRAIT_POINT_BUDGET:
        issues.append(f'traits cost {net_cost:g} points, over the starting budget of '
                       f'{_TRAIT_POINT_BUDGET:g} ({", ".join(label for label, _ in selected)})')

    return {'verified': not issues, 'issues': issues, 'checked': True}
