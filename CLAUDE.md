# CLAUDE.md — guide for working in the Stellaris Advisor repo

## What this is

A desktop app that reads the player's **Stellaris save files** and gives live,
auto-updating strategic advice while they play. It watches the save-games folder,
re-parses the newest `.sav` whenever it changes, runs a rules engine over the
extracted state, and serves a dashboard with three tabs:

- **Live Advisor** — prioritized advice (economy, military, diplomacy, expansion,
  research, ascension, identity) for the current save.
- **Fleet Manager** — counts the player's warships by hull class and recommends a
  target composition for their tech tier.
- **Empire Builder** — curated, synergistic empire designs to pick at creation,
  filtered to owned DLC and validated against the game files.

It is a **rules engine, not an LLM** — fully offline, no API keys, no network
calls in the core. Accuracy-sensitive numbers (ship costs, civic/trait
availability) are read **live from the player's installed game files** so they
track the patch instead of being hard-coded.

## Tech stack

- **Language:** Python 3.12, Windows.
- **Core (`advisor/` package):** Python **standard library only** — no third-party
  imports. Keep it that way.
- **Desktop window (`app.py`):** [pywebview](https://pywebview.flowrl.com/) (Edge
  WebView2, built into Windows). Imported lazily/guarded; the browser mode needs
  no dependencies.
- **Icon generation (`make_icon.py`):** Pillow (dev-time only).
- **Frontend:** a single self-contained `templates/dashboard.html` (vanilla
  HTML/CSS/JS, canvas starfield, polls the JSON API). No build step, no framework.

## Commands

Confirmed from `requirements.txt`, `app.py`, `run.py`, `audit_builds.py`,
`make_icon.py`. There is **no** package.json / pyproject / test suite.

```sh
# One-time: desktop-window dependency
python -m pip install pywebview

# Run as a desktop window (primary way the user runs it)
python app.py                       # default http://127.0.0.1:8770, opens a native window
python app.py --campaign <folder>   # watch one save-games subfolder
python app.py --on-top              # keep window above the game (single monitor)
python app.py --save-root "D:\path\to\save games"

# Run in a browser instead (zero dependencies)
python run.py                       # opens http://127.0.0.1:8770/
python run.py --no-browser          # don't auto-open a browser

# Windows: double-click "Stellaris Advisor.vbs" (runs `pythonw app.py`, no console)

# Validate every Empire Builder build against the installed game files
python audit_builds.py

# Regenerate icon.ico / icon.png from logo.svg (needs: python -m pip install pillow)
python make_icon.py
```

Shared CLI flags: `--campaign`, `--save-root`, `--port` (default `8770`).
`run.py` adds `--host`, `--no-browser`; `app.py` adds `--on-top`.

**Tests:** none exist yet. (Adding pytest coverage is the top backlog item.)

## Data flow

```
.sav (zip → "gamestate", Clausewitz text)
  └─ extract.build_snapshot()        parse country/species_db (clausewitz) + regex scans
       └─ analyze.analyze()          rules engine; uses profile + knowledge
            └─ watcher.AdvisorState  finds newest save, re-parses on change, caches
                 └─ server (stdlib http) /api/advice, /api/fleet, /api/builds, /api/campaigns, /api/select
                      └─ templates/dashboard.html   3 tabs, polls every 5s
```

## Project structure

```
advisor/                 core package (stdlib only)
  clausewitz.py          tolerant parser for the Paradox save format (+ extract_block brace matcher)
  extract.py             build_snapshot(): turns a .sav into a structured dict; on-demand fleet scan
  analyze.py             rules engine; analyze() aggregates analyze_economy/military/standing/… into advice
  profile.py             EmpireProfile: classifies ethics/authority/civics/traits (gestalt, genocidal, etc.)
  knowledge.py           origin tips, civic tips, ascension-path data & recommendations
  builds.py              BUILDS list (Empire Builder) + recommend_builds() (DLC filter)
  validate.py            validates builds vs game files (civics/origin/traits); single source of truth
  fleet.py               recommend(): warship composition advice by tech tier (standard + bioship families)
  gamedata.py            reads ship_sizes (naval-cap cost, prereq tech) live from the install
  dlc.py                 detect_dlc(): owned DLC from install + saves + owned_dlc.txt
  watcher.py             AdvisorState (caching, save watching), list_campaigns()
  server.py              ThreadingHTTPServer; routes + serves dashboard.html
app.py                   desktop launcher: pywebview window, Win32 icon, single-instance guard, stdout→advisor.log
run.py                   browser launcher (server only)
audit_builds.py          CLI wrapper around advisor.validate
make_icon.py             renders logo.svg → icon.ico/icon.png with Pillow
templates/dashboard.html the entire UI
owned_dlc.txt            user-editable: DLC to treat as owned (Steam not finished downloading)
logo.svg                 source logo (inlined in dashboard.html header; source for the icon)
```

## Conventions

- **No third-party imports in `advisor/`.** Core must run on a bare Python
  install. pywebview/Pillow live only in `app.py` / `make_icon.py`.
- **Heavy save scans are on-demand and cached per save.** The full ship scan
  (`extract.compute_fleet`) runs only via `AdvisorState.fleet_report()` (the Fleet
  tab) and is cached by save path+mtime. Never put it in `build_snapshot` or
  `payload()` (those run on every 5s poll — keep them ~1.5s).
- **Read the game, don't hard-code it.** Ship costs, civic categories, trait
  availability come from the install via `gamedata.py` / `validate.py`. When the
  data exists in game files, parse it rather than embedding values.
- **Dashboard re-renders a section only when its data signature changes** (see the
  `sig*` vars in `dashboard.html`) so animations don't flicker each poll.
- **Large gamestate sections** (`country`, `ships`, `ship_design`, `species_db`)
  are brace-extracted with `clausewitz.extract_block` then parsed/regex-scanned —
  never full-parse the whole 20+ MB file.

## Do not touch / be careful

- **Player save files** — read-only. Never write to the Stellaris save-games
  folder; the advisor only reads `.sav` archives.
- **Generated files:** `advisor.log` (runtime log), `icon.ico`, `icon.png`. To
  change the icon, edit `logo.svg` then run `make_icon.py` — don't hand-edit the
  binaries.
- **`owned_dlc.txt`** is user data; don't overwrite it programmatically.
- **`.claude/settings.local.json`** is local tooling permissions.
- No secrets or API keys exist in this repo (and none should be added — the core
  is offline by design).
