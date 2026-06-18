"""
Launch the Stellaris Live Advisor.

    python run.py                 # watch all campaigns, use newest save
    python run.py --campaign foo  # only watch one campaign folder
    python run.py --port 8770     # change the web port
    python run.py --no-browser    # don't auto-open the browser

Then drag the browser window to your second monitor and play. Every time
Stellaris autosaves (or you save), the advice refreshes on its own.
"""

import argparse
import threading
import webbrowser

from advisor.watcher import AdvisorState, default_save_root, newest_save
from advisor.server import serve


def main():
    ap = argparse.ArgumentParser(description='Stellaris Live Advisor')
    ap.add_argument('--campaign', default=None,
                    help='Name of a single save-games subfolder to watch')
    ap.add_argument('--save-root', default=None, help='Override Stellaris save games path')
    ap.add_argument('--port', type=int, default=8770)
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--no-browser', action='store_true')
    args = ap.parse_args()

    root = args.save_root or default_save_root()
    print('Stellaris save folder:', root)
    latest = newest_save(root, args.campaign)
    if latest:
        print('Newest save found:', latest)
    else:
        print('No .sav files found yet — start a game and let it autosave.')

    state = AdvisorState(save_root=root, campaign=args.campaign)
    httpd = serve(state, host=args.host, port=args.port)
    url = f'http://{args.host}:{args.port}/'
    print(f'\nAdvisor running at {url}')
    print('Drag this browser window to your second monitor. Ctrl+C to stop.\n')

    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down.')
        httpd.shutdown()


if __name__ == '__main__':
    main()
