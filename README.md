# Stellaris Live Advisor

Reads your Stellaris autosaves while you play and shows constantly-updating
advice on a dashboard — economy, military, diplomacy and research — so you don't
have to ask "what should I do?" each turn. Put it on your second monitor.

## How it works

1. Stellaris writes an autosave every game-month (and whenever you save).
2. The advisor watches your save-games folder and re-parses the **newest** `.sav`
   the instant it changes.
3. It extracts your resources, income, fleet power, the power of every rival
   empire, your diplomatic standing and research, then runs a rules engine that
   surfaces the things you're most likely to have missed.
4. A local web dashboard (auto-refreshing every 5s) shows it all.

The advisor itself uses only Python's standard library. The desktop window
(`app.py`) additionally uses pywebview (see Run it).

## Run it

**As a desktop window (recommended):**

Just **double-click `Stellaris Advisor.vbs`** — it opens the app in its own window
with no console, using the Edge WebView2 engine built into Windows. Put it on your
second monitor and play. (Tip: right-click it → *Send to → Desktop (create
shortcut)* to launch it from your desktop, and you can pin that shortcut.)

First time only, install the window dependency:

```
python -m pip install pywebview
```

Equivalent from a terminal if you prefer: `python app.py`.

```
python app.py --on-top          # keep the window above the game (single monitor)
python app.py --campaign tebridhomolog_1186672995   # watch one save folder only
```

**As a browser tab (no install needed):**

```
python run.py
```

Opens `http://127.0.0.1:8770/`. Either way the advice updates by itself on every
autosave.

Shared options (both launchers): `--campaign <folder>`, `--port <n>`,
`--save-root "D:\path\to\save games"`.

Tip: in Stellaris, set **Settings → Game → Autosave** to *Monthly* for the most
frequent advice updates.

## Personalised to your empire

The advisor reads your empire's **ethics, authority, civics, origin and species
traits** and tailors advice to them — and, just as importantly, *suppresses
advice that doesn't apply*:

- Gestalts (Hive Mind / Machine) get no consumer-goods nagging; Machines aren't
  warned about food they don't eat.
- Genocidal empires (Devouring Swarm, Determined Exterminator, Fanatic Purifiers)
  and Driven Assimilators get no "make an ally" suggestions they could never act
  on — instead a tailored war/expansion playstyle card.
- Militarists are told to press attacks; Pacifists are reminded they can't start
  offensive wars and should build tall/defensive.
- Each empire gets one "play to your strengths" card for its type.

The empire's classification (e.g. *Fanatic Materialist, Xenophile Dictatorship*)
shows in the header, with species traits on hover.

## Fleet Manager

The **🚀 Fleet Manager** tab reads your actual fleets and recommends how many of
each warship class (corvette/destroyer/cruiser/battleship/titan) you should field
for your tech tier, comparing it to what you currently have so you can see what to
build or retire. The scan is heavier than the live advice, so it runs only when
the tab is open and is cached until your next save.

## Empire Builder (creation helper)

Switch to the **🧬 Empire Builder** tab to get curated, synergistic empire designs
to pick at game creation — each lists ethics, authority, civics, origin, species
traits and a recommended ascension, with a "why it works" explaining the synergy.
Filter by goal (Tall, Wide, Tech, Military, Trade, Bio, Gestalt). Only empires you
can actually build with your **owned DLC** are shown, including BioGenesis content.

### DLC detection

The advisor detects your DLC from your Steam install. If you just bought DLC that
Steam hasn't finished downloading, add its name to `owned_dlc.txt` (one per line)
and it'll be included immediately.

## Choosing which game to watch

By default the advisor follows your **most recently played** save across all
campaigns. Use the dropdown in the top-right to lock it to a specific empire
instead — it lists every campaign with its empire name and in-game date.

## What it advises on

- **Empire identity** — a tailored playstyle card based on your ethics/civics.
- **Origin & civics** — tips specific to your origin (Tree of Life, Void
  Dwellers, …) and signature civics (Technocracy, Mining Guilds, …).
- **Ascension** — reads the perks you have, detects your active ascension path,
  and recommends a path (Genetic / Cybernetic / Synthetic / Psionic) and next
  perks that fit your empire.
- **Economy** — resources about to bottom out (with months of runway), wasted
  influence at cap, alloy/strategic-resource surpluses and shortages.
- **Strategic standing** — your rank among real empires in economy, technology
  and fleet power, and which dimension you're falling behind in.
- **Expansion** — your colony count vs. the galaxy, when to settle/conquer more.
- **Military** — fleet-power rank, rivals that have outgrown you, active-war
  reminders, and Fallen Empires to avoid provoking.
- **Diplomacy** — active rivalries, ally suggestions, existing pacts.
- **Research** — idle research slots and what each field is working on.
- **Progression** — unspent unity / ascension perks and inactive edicts.

## Project layout

```
advisor/
  clausewitz.py   Parser for the Paradox save format
  extract.py      Builds a clean snapshot from a .sav
  analyze.py      The rules engine that produces advice  <-- tune advice here
  watcher.py      Finds the newest save, re-parses on change
  server.py       Serves the dashboard + JSON API
templates/
  dashboard.html  The dashboard UI
run.py            Launcher
```

## Tuning the advice

`advisor/analyze.py` is where the rules live. Each rule appends a dict with a
`priority` (critical/warning/info/good), `category`, `title` and `detail`. Add or
adjust thresholds there to match your playstyle.

## Possible next steps

- Per-fleet breakdown and "where is my fleet vs. the threat" positioning.
- Planet/job management hints (unemployment, free building slots).
- Optional Claude API layer for free-form strategic narration on top of the rules.
