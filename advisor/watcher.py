"""
Find the save the player is currently in, and re-parse it only when it changes.

Stellaris writes a new autosave file (e.g. autosave_2245.07.01.sav) periodically
and a manual save when you hit save. We watch the whole save-games tree and treat
the most-recently-modified .sav as "the game you're playing right now".
"""

import os
import glob
import time

from .extract import build_snapshot, compute_fleet
from .analyze import analyze
from .profile import EmpireProfile
from .dlc import detect_dlc
from .fleet import recommend as recommend_fleet


# Default Stellaris save location. OneDrive redirection is handled by trying
# both the plain Documents path and the OneDrive one.
def default_save_root():
    candidates = [
        os.path.expandvars(r'%USERPROFILE%\Documents\Paradox Interactive\Stellaris\save games'),
        os.path.expandvars(r'%USERPROFILE%\OneDrive\Documents\Paradox Interactive\Stellaris\save games'),
        os.path.expandvars(r'%ONEDRIVE%\Documents\Paradox Interactive\Stellaris\save games'),
    ]
    for c in candidates:
        if c and os.path.isdir(c):
            return c
    return candidates[0]


def _read_meta(sav_path):
    """Cheap read of a save's meta block for empire name + in-game date."""
    import zipfile
    import re
    try:
        with zipfile.ZipFile(sav_path) as z:
            meta = z.read('meta').decode('utf-8', 'replace')
        name = re.search(r'name="([^"]*)"', meta)
        date = re.search(r'date="([^"]*)"', meta)
        return (name.group(1) if name else None,
                date.group(1) if date else None)
    except Exception:
        return None, None


def list_campaigns(save_root):
    """List campaign folders that contain saves, newest first.

    Each entry: {folder, empire, date, file, mtime}. `empire`/`date` come from
    the newest save's meta block.
    """
    out = []
    if not os.path.isdir(save_root):
        return out
    for folder in os.listdir(save_root):
        path = os.path.join(save_root, folder)
        if not os.path.isdir(path):
            continue
        saves = glob.glob(os.path.join(path, '*.sav'))
        if not saves:
            continue
        newest = max(saves, key=os.path.getmtime)
        empire, date = _read_meta(newest)
        out.append({
            'folder': folder,
            'empire': empire or folder,
            'date': date or '',
            'file': os.path.basename(newest),
            'mtime': os.path.getmtime(newest),
        })
    out.sort(key=lambda e: e['mtime'], reverse=True)
    return out


def newest_save(save_root, campaign=None):
    """Return path to the most recently modified .sav, or None.

    If `campaign` is given, only look inside that campaign subfolder.
    """
    if campaign:
        pattern = os.path.join(save_root, campaign, '*.sav')
    else:
        pattern = os.path.join(save_root, '*', '*.sav')
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


class AdvisorState:
    """Caches the latest analysis and refreshes when a newer save appears."""

    def __init__(self, save_root=None, campaign=None):
        self.save_root = save_root or default_save_root()
        self.campaign = campaign
        self._current_path = None
        self._current_mtime = None
        self._result = None
        self._error = None
        self._dlc = None  # detected once, lazily
        self._fleet_cache = None  # (path, mtime, report)

    def fleet_report(self):
        """Fleet composition + recommendation for the current save.

        This is the expensive bit (scans every ship in the galaxy), so it runs
        only when asked (the Fleet tab) and is cached per save until it changes.
        """
        self.refresh()
        if self._result is None:
            return {'ok': False, 'error': self._error or 'No save loaded.'}
        path, mtime = self._current_path, self._current_mtime
        if self._fleet_cache and self._fleet_cache[0] == path and self._fleet_cache[1] == mtime:
            return self._fleet_cache[2]
        player = dict(self._result['snapshot']['player'])
        try:
            player['fleet'] = compute_fleet(path, set(player.get('owned_fleet_ids', [])))
            report = recommend_fleet(player)
            report['ok'] = True
        except Exception as e:
            report = {'ok': False, 'error': f'Fleet scan failed: {e}'}
        self._fleet_cache = (path, mtime, report)
        return report

    def dlc(self):
        if self._dlc is None:
            self._dlc = detect_dlc(self.save_root)
        return self._dlc

    def set_campaign(self, campaign):
        """Switch which campaign to watch ('' / None = auto, newest of all).

        Clears the cache so the next refresh re-parses the chosen save.
        """
        self.campaign = campaign or None
        self._current_path = None
        self._current_mtime = None
        self._result = None
        self._error = None

    def _parse_with_retry(self, path, attempts=3):
        # The file may still be flushing to disk when we notice it; retry briefly.
        last = None
        for i in range(attempts):
            try:
                snap = build_snapshot(path)
                snap['dlc'] = self.dlc()
                return {'snapshot': snap, 'advice': analyze(snap)}
            except Exception as e:  # zip not finished, transient read error, etc.
                last = e
                time.sleep(0.4)
        raise last

    def refresh(self):
        """Re-read the newest save if it changed. Returns the current result dict."""
        path = newest_save(self.save_root, self.campaign)
        if path is None:
            self._error = (f'No .sav files found under {self.save_root}. '
                           f'Start a game and let it autosave, or check the path.')
            self._result = None
            return self.payload()

        try:
            mtime = os.path.getmtime(path)
        except OSError:
            mtime = None

        changed = (path != self._current_path) or (mtime != self._current_mtime)
        if changed:
            try:
                self._result = self._parse_with_retry(path)
                self._current_path = path
                self._current_mtime = mtime
                self._error = None
            except Exception as e:
                self._error = f'Could not parse {os.path.basename(path)}: {e}'
        return self.payload()

    def payload(self):
        if self._result is None:
            return {'ok': False, 'error': self._error,
                    'save_file': os.path.basename(self._current_path or ''),
                    'campaign': self.campaign}
        snap = self._result['snapshot']
        prof = EmpireProfile(snap['player'].get('identity'))
        return {
            'ok': True,
            'error': None,
            'date': snap['date'],
            'save_file': snap['save_file'],
            'campaign': os.path.basename(os.path.dirname(self._current_path or '')),
            'player': snap['player'],
            'profile': {
                'title': prof.title(),
                'species': prof.species_name,
                'traits': [t.replace('trait_', '').replace('pc_', '')
                           .replace('_preference', '').replace('_', ' ').title()
                           for t in prof.traits if not t.startswith('trait_pc_')],
            },
            'empires': list(snap['empires'].values()),
            'advice': self._result['advice'],
            'dlc': self.dlc(),
        }
