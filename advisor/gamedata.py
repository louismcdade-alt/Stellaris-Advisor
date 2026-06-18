"""
Read live values from the installed Stellaris game files so the advisor stays
accurate across patches instead of hard-coding numbers that go stale.

Right now this reads ship_sizes (naval-capacity cost = fleet_slot_size, hull
class, and prerequisite tech per hull). If the install can't be found, callers
fall back to sensible built-in defaults.
"""

import os
import re
import glob

from .dlc import find_install

_cache = None


def _iter_blocks(text):
    """Yield (name, block_text) for each top-level `name = { ... }` definition."""
    for m in re.finditer(r'^([a-z0-9_]+)\s*=\s*\{', text, re.M):
        start = text.index('{', m.start())
        depth, i, n = 0, start, len(text)
        while i < n:
            c = text[i]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        yield m.group(1), text[start:i + 1]


def ship_sizes():
    """{ship_size_name: {'slot': int, 'class': str, 'prereq': str|None}} (cached)."""
    global _cache
    if _cache is not None:
        return _cache
    out = {}
    install = find_install()
    if install:
        folder = os.path.join(install, 'common', 'ship_sizes')
        for path in glob.glob(os.path.join(folder, '*.txt')):
            try:
                text = open(path, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            for name, block in _iter_blocks(text):
                fss = re.search(r'\bfleet_slot_size\s*=\s*([0-9]+)', block)
                if not fss:
                    continue
                cls = re.search(r'\bclass\s*=\s*(\w+)', block)
                pre = re.search(r'prerequisites\s*=\s*\{\s*"?([a-z0-9_]+)', block)
                out[name] = {
                    'slot': int(fss.group(1)),
                    'class': cls.group(1) if cls else '',
                    'prereq': pre.group(1) if pre else None,
                }
    _cache = out
    return out


def is_loaded():
    return bool(ship_sizes())
