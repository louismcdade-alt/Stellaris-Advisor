"""
Tiny zero-dependency web server for the advisor dashboard.

Routes:
  GET /              -> the dashboard page (templates/dashboard.html)
  GET /api/advice    -> JSON: current snapshot + advice (refreshes on save change)

The dashboard polls /api/advice every few seconds, so a new autosave shows up
automatically with no clicks.
"""

import json
import os
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .watcher import AdvisorState, list_campaigns
from .builds import recommend_builds, GOALS
from .validate import validate_build

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TEMPLATE = os.path.join(_HERE, 'templates', 'dashboard.html')


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
                try:
                    with open(_TEMPLATE, encoding='utf-8') as f:
                        html = f.read()
                    self._send(200, html, 'text/html')
                except FileNotFoundError:
                    self._send(500, 'dashboard.html not found', 'text/plain')
                return
            self._send(404, 'Not found', 'text/plain')

    return Handler


def serve(state=None, host='127.0.0.1', port=8770):
    state = state or AdvisorState()
    httpd = ThreadingHTTPServer((host, port), make_handler(state))
    return httpd
