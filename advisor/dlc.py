"""
Detect which Stellaris DLC the player actually owns/has installed.

Steam only puts a DLC's files under the game's `dlc/` folder if you own it, and
each folder carries a `.dlc` manifest with a clean `name = "..."`. So listing
those names is a reliable "what do I own" check — better than a save's
`required_dlcs`, which only lists the DLC that *one* save happens to use.

We also union in the DLC referenced by the player's saves, so even if the install
folder can't be found we still know what their games rely on.
"""

import os
import re
import glob
import zipfile

# Common Steam install locations to probe before consulting library folders.
_DEFAULT_INSTALLS = [
    r'C:\Program Files (x86)\Steam\steamapps\common\Stellaris',
    r'C:\Program Files\Steam\steamapps\common\Stellaris',
]


def _library_installs():
    """Find Stellaris installs across all Steam library folders."""
    found = []
    for base in (r'C:\Program Files (x86)\Steam', r'C:\Program Files\Steam'):
        vdf = os.path.join(base, 'steamapps', 'libraryfolders.vdf')
        if not os.path.isfile(vdf):
            continue
        try:
            text = open(vdf, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        for path in re.findall(r'"path"\s*"([^"]+)"', text):
            candidate = os.path.join(path.replace('\\\\', '\\'),
                                     'steamapps', 'common', 'Stellaris')
            if os.path.isdir(candidate):
                found.append(candidate)
    return found


def find_install():
    for p in _DEFAULT_INSTALLS + _library_installs():
        if os.path.isdir(os.path.join(p, 'dlc')):
            return p
    return None


def _names_from_install(install):
    names = set()
    for dlc_file in glob.glob(os.path.join(install, 'dlc', '*', '*.dlc')):
        try:
            text = open(dlc_file, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        m = re.search(r'name\s*=\s*"([^"]+)"', text)
        if m:
            names.add(m.group(1))
    return names


def _names_from_saves(save_root):
    names = set()
    for sav in glob.glob(os.path.join(save_root, '*', '*.sav')):
        try:
            with zipfile.ZipFile(sav) as z:
                meta = z.read('meta').decode('utf-8', 'replace')
        except Exception:
            continue
        block = re.search(r'required_dlcs=\s*\{(.*?)\}', meta, re.S)
        if block:
            names.update(re.findall(r'"([^"]+)"', block.group(1)))
    return names


def _declared_dlc():
    """DLC the user has manually listed in owned_dlc.txt at the project root."""
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'owned_dlc.txt')
    names = set()
    try:
        for line in open(path, encoding='utf-8', errors='replace'):
            line = line.strip()
            if line and not line.startswith('#'):
                names.add(line)
    except OSError:
        pass
    return names


def detect_dlc(save_root=None):
    """Return {'names': sorted list, 'source': ..., 'declared': [...]}.

    Combines: the install folder (true ownership), DLC referenced by saves, and
    any DLC manually declared in owned_dlc.txt (for just-bought DLC Steam hasn't
    finished installing yet).
    """
    install = find_install()
    names = _names_from_install(install) if install else set()
    source = 'install' if names else 'none'
    if save_root and os.path.isdir(save_root):
        save_names = _names_from_saves(save_root)
        if not names and save_names:
            source = 'saves'
        names |= save_names
    declared = _declared_dlc()
    names |= declared
    return {'names': sorted(names), 'source': source, 'install': install,
            'declared': sorted(declared)}


def has(names, *keywords):
    """True if any owned DLC name contains all of the given keywords (case-insensitive)."""
    low = [n.lower() for n in names]
    return any(all(k.lower() in n for k in keywords) for n in low)
