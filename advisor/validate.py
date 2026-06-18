"""
Validate Empire Builder builds against the installed game files.

Checks, per build, that every element is actually usable:
  * civics exist and suit the build's authority (regular / gestalt hive|machine /
    corporate),
  * the origin exists,
  * each species trait exists AND is selectable at empire creation for a normal
    biological species (not ascension/cyborg/robotic/shroud, and not locked to a
    specific phenotype via species_class).

Catalogs are read once from the install (cached). If the install can't be found
we report 'unknown' rather than failing builds. This is the same logic the
standalone audit_builds.py uses, exposed so the app can show a live "verified"
badge in the builder.
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
    data = {'install': install, 'civic_names': {}, 'civic_cat': {},
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
                'startable': startable, 'phenotype': locked, 'nonstart': nonstartable}


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

    for civ in build['civics']:
        name = re.sub(r'\s*[—-].*$', '', civ).strip()
        ids = cat['civic_names'].get(_norm(name))
        if not ids:
            issues.append(f'civic "{civ}" not found in game files')
            continue
        cats = {cat['civic_cat'].get(i, 'unknown') for i in ids}
        if not _civic_ok(cats, kind):
            issues.append(f'civic "{civ}" not available to a {build["authority"]} empire')

    oname = re.sub(r'\s*\(.*?\)|\s+or\s+.*$', '', build['origin']).strip()
    if not cat['origin_names'].get(_norm(oname)):
        issues.append(f'origin "{build["origin"]}" not found in game files')

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

    return {'verified': not issues, 'issues': issues, 'checked': True}
