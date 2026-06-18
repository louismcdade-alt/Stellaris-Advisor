"""
Stellaris Live Advisor — native desktop window.

This is the "real app" launcher. It starts the advisor server in the background
and shows the dashboard in its own window (no browser, no address bar), using the
Edge WebView2 engine built into Windows.

    python app.py                 # open the advisor window
    python app.py --campaign foo  # watch one campaign folder only
    python app.py --on-top        # keep the window above the game (single monitor)

If you'd rather use a browser tab instead of a window, run `python run.py`.
"""

import argparse
import os
import socket
import sys
import threading
import time

from advisor.watcher import AdvisorState, default_save_root, newest_save
from advisor.server import serve

_HERE = os.path.dirname(os.path.abspath(__file__))

# Launched windowed (pythonw, fully detached) there is no console, so the default
# stdout/stderr handles are invalid and any print() would crash the process
# silently. Redirect output to a log file — this both prevents the crash and
# captures any errors for debugging.
try:
    _logf = open(os.path.join(_HERE, 'advisor.log'), 'a', encoding='utf-8', buffering=1)
    sys.stdout = _logf
    sys.stderr = _logf
except Exception:
    pass


def _apply_window_icon(title, ico_path):
    """Set the window + taskbar icon via Win32 once the window exists.

    pywebview's own `icon=` argument is ignored by the Windows EdgeChromium
    backend, so we load the .ico ourselves and send WM_SETICON to the window.
    """
    try:
        import ctypes
        u = ctypes.windll.user32
        IMAGE_ICON, LR_LOADFROMFILE = 1, 0x00000010
        WM_SETICON, ICON_SMALL, ICON_BIG = 0x0080, 0, 1
        big = u.LoadImageW(0, ico_path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
        small = u.LoadImageW(0, ico_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
        for _ in range(100):                      # poll until the window appears
            hwnd = u.FindWindowW(None, title)
            if hwnd:
                if big:
                    u.SendMessageW(hwnd, WM_SETICON, ICON_BIG, big)
                if small:
                    u.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, small)
                return
            time.sleep(0.1)
    except Exception as e:
        print('icon set failed:', e)


def _free_port(preferred):
    """Use the preferred port if open, otherwise let the OS pick a free one."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('127.0.0.1', preferred))
        s.close()
        return preferred
    except OSError:
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.bind(('127.0.0.1', 0))
        port = s2.getsockname()[1]
        s2.close()
        return port


def _already_running(port):
    """True if an advisor is already answering on the default port."""
    import urllib.request
    try:
        urllib.request.urlopen(f'http://127.0.0.1:{port}/api/advice', timeout=1)
        return True
    except Exception:
        return False


def _focus_window(title):
    """Bring an existing advisor window to the foreground."""
    try:
        import ctypes
        u = ctypes.windll.user32
        hwnd = u.FindWindowW(None, title)
        if hwnd:
            u.ShowWindow(hwnd, 9)        # SW_RESTORE
            u.SetForegroundWindow(hwnd)
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser(description='Stellaris Live Advisor (desktop window)')
    ap.add_argument('--campaign', default=None,
                    help='Name of a single save-games subfolder to watch')
    ap.add_argument('--save-root', default=None, help='Override Stellaris save games path')
    ap.add_argument('--port', type=int, default=8770)
    ap.add_argument('--on-top', action='store_true',
                    help='Keep the window above other windows (good for one monitor)')
    args = ap.parse_args()

    # Single instance: if the advisor is already running, just focus its window
    # instead of opening a duplicate (handy if the launcher is clicked twice).
    if _already_running(args.port):
        print('Advisor already running — focusing existing window.')
        _focus_window('Stellaris Live Advisor')
        return

    try:
        import webview
    except ImportError:
        print('The desktop window needs pywebview:\n    python -m pip install pywebview\n'
              'Or use the browser version instead:\n    python run.py')
        return

    root = args.save_root or default_save_root()
    print('Stellaris save folder:', root)
    latest = newest_save(root, args.campaign)
    print('Newest save:', latest or '(none yet — start a game and let it autosave)')

    port = _free_port(args.port)
    state = AdvisorState(save_root=root, campaign=args.campaign)
    httpd = serve(state, host='127.0.0.1', port=port)

    # Server runs in the background; the GUI must own the main thread.
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    url = f'http://127.0.0.1:{port}/'
    print(f'Advisor window opening ({url}) — close the window to quit.')

    icon_path = os.path.join(_HERE, 'icon.ico')
    title = 'Stellaris Live Advisor'

    # Give the app its own taskbar identity so Windows uses our window icon
    # (rather than grouping under the generic Python executable icon).
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('StellarisLiveAdvisor')
    except Exception:
        pass

    webview.create_window(
        title,
        url,
        width=560, height=820,
        min_size=(420, 560),
        on_top=args.on_top,
        background_color='#070b16',
    )

    # Apply the icon once the window is up (runs in the background).
    if os.path.isfile(icon_path):
        threading.Thread(target=_apply_window_icon, args=(title, icon_path),
                         daemon=True).start()

    webview.start()
    httpd.shutdown()


if __name__ == '__main__':
    main()
