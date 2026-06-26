"""
Tiny zero-dependency web server for the advisor dashboard.

Routes:
  GET /              -> the dashboard's built index.html (frontend/dist)
  GET /assets/*, etc -> the dashboard's other built static files (JS/CSS/icons)
  GET /api/advice    -> JSON: current snapshot + advice (refreshes on save change)

The dashboard polls /api/advice every few seconds, so a new autosave shows up
automatically with no clicks.

The dashboard itself is a React + Vite app (frontend/); this server only ever
serves its *built* output (frontend/dist, produced by `npm run build`), never
runs Node or a dev server -- the Python side stays dependency-free.
"""

import json
import mimetypes
import os
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .watcher import AdvisorState, list_campaigns
from .builds import recommend_builds, GOALS
from .validate import validate_build

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DIST = os.path.join(_HERE, 'frontend', 'dist')


def make_handler(state):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # keep the console quiet

        def _send(self, code, body, ctype):
            data = body.encode('utf-8') if isinstance(body, str) else body
            self.send_response(code)
            self.send_header('Content-Type', ctype + '; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(data)

        def _send_static(self, path, immutable=False):
            try:
                with open(path, 'rb') as f:
                    data = f.read()
            except OSError:
                self._send(404, 'Not found', 'text/plain')
                return
            ctype, _ = mimetypes.guess_type(path)
            self.send_response(200)
            self.send_header('Content-Type', ctype or 'application/octet-stream')
            self.send_header('Content-Length', str(len(data)))
            # Built assets are content-hashed by Vite, so they're safe to
            # cache hard; index.html is not (its filename never changes but
            # its contents do whenever assets are rebuilt), so it stays
            # no-store like the rest of the dynamic app.
            self.send_header('Cache-Control',
                              'public, max-age=31536000, immutable' if immutable else 'no-store')
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            parsed = urlparse(self.path)
            route, query = parsed.path, parse_qs(parsed.query)

            if route == '/api/advice':
                try:
                    payload = state.refresh()
                except Exception as e:
                    payload = {'ok': False, 'error': f'Server error: {e}'}
                self._send(200, json.dumps(payload), 'application/json')
                return

            if route == '/api/campaigns':
                try:
                    camps = list_campaigns(state.save_root)
                    payload = {'ok': True, 'selected': state.campaign or '',
                               'campaigns': camps}
                except Exception as e:
                    payload = {'ok': False, 'error': str(e), 'campaigns': []}
                self._send(200, json.dumps(payload), 'application/json')
                return

            if route == '/api/fleet':
                try:
                    payload = state.fleet_report()
                except Exception as e:
                    payload = {'ok': False, 'error': f'Server error: {e}'}
                self._send(200, json.dumps(payload), 'application/json')
                return

            if route == '/api/builds':
                goal = (query.get('goal') or [''])[0] or None
                try:
                    dlc = state.dlc()
                    builds = recommend_builds(dlc['names'], goal)
                    for b in builds:
                        b.update(validate_build(b))
                    payload = {'ok': True, 'owned_dlc': dlc['names'],
                               'declared': dlc.get('declared', []),
                               'goals': GOALS, 'builds': builds}
                except Exception as e:
                    payload = {'ok': False, 'error': str(e), 'builds': []}
                self._send(200, json.dumps(payload), 'application/json')
                return

            if route == '/api/select':
                campaign = (query.get('campaign') or [''])[0]
                state.set_campaign(campaign)
                payload = state.refresh()
                self._send(200, json.dumps(payload), 'application/json')
                return

            if route in ('/', '/index.html'):
                self._send_static(os.path.join(_DIST, 'index.html'))
                return

            # Built static assets (hashed JS/CSS under /assets/, favicon, etc).
            # Guard against path traversal: resolve and require the result to
            # still be inside _DIST before ever opening it.
            rel = route.lstrip('/')
            asset_path = os.path.abspath(os.path.join(_DIST, rel))
            if (os.path.commonpath([asset_path, _DIST]) == _DIST
                    and os.path.isfile(asset_path)):
                self._send_static(asset_path, immutable=rel.startswith('assets/'))
                return

            self._send(404, 'Not found', 'text/plain')

    return Handler


def serve(state=None, host='127.0.0.1', port=8770):
    state = state or AdvisorState()
    httpd = ThreadingHTTPServer((host, port), make_handler(state))
    return httpd
