"""
Empire Builder — curated, synergistic empire designs to pick at creation time.

Each build lists ethics, authority, civics, origin, species traits and a
recommended ascension, plus a short "why it works" that explains the synergy.
Every build is tagged with the DLC it needs, so the builder only ever shows you
empires you can actually create with the content you own.

Trait/civic/origin names use their in-game display names. Picks lean on
well-established synergies (growth + output, war bonuses that stack, etc.).
"""

# DLC keywords (matched against owned DLC names, case-insensitive substrings).
BASE = []
UTOPIA = ['Utopia']
BIOGENESIS = ['BioGenesis']
SYNTH_DAWN = ['Synthetic Dawn']
MEGACORP = ['MegaCorp']

# goals taxonomy used by the UI filter
GOALS = ['Tall', 'Wide', 'Tech', 'Military', 'Trade', 'Economy', 'Bio', 'Gestalt']


BUILDS = [
    # ---------------- Base game ----------------
    {
        'name': 'Technocratic Pioneers',
        'goals': ['Tech', 'Economy'],
        'dlc': BASE,
        'ethics': ['Fanatic Materialist', 'Xenophile'],
        'authority': 'Oligarchic',
        'civics': ['Technocracy', 'Meritocracy'],
        'origin': 'Prosperous Unification',
        'traits': ['Intelligent', 'Natural Engineers', 'Rapid Breeders', 'Deviants (-)', 'Repugnant (-)'],
        'ascension': 'Synthetic (needs Utopia)',
        'why': 'Technocracy turns researchers into a physics engine and Meritocracy boosts '
               'all specialists, so Intelligent + Natural Engineers compound your research '
               'lead. Rapid Breeders keeps the labs staffed; the negative traits are cheap '
               'because Deviants/Repugnant barely matter when you are heads-down on research, '
               'not diplomacy.',
    },
    {
        'name': 'Iron Conquerors',
        'goals': ['Military', 'Wide'],
        'dlc': BASE,
        'ethics': ['Fanatic Militarist', 'Authoritarian'],
        'authority': 'Imperial',
        'civics': ['Citizen Service', 'Distinguished Admiralty'],
        'origin': 'Prosperous Unification',
        'traits': ['Very Strong', 'Industrious', 'Slow Learners (-)', 'Repugnant (-)'],
        'ascension': 'Cybernetic (needs Utopia)',
        'why': 'Militarist + Distinguished Admiralty + Citizen Service stack fleet bonuses and '
               'give cheap, strong armies. Very Strong makes your soldiers and worker '
               'output brutal for early conquest; Slow Learners and Repugnant are fine dumps '
               'since you win by fighting, not out-teching or making friends.',
    },
    {
        'name': 'Free Republic Traders',
        'goals': ['Trade', 'Wide', 'Economy'],
        'dlc': BASE,
        'ethics': ['Fanatic Egalitarian', 'Xenophile'],
        'authority': 'Democratic',
        'civics': ['Beacon of Liberty', 'Free Haven'],
        'origin': 'Prosperous Unification',
        'traits': ['Charismatic', 'Thrifty', 'Slow Breeders (-)'],
        'ascension': 'Synthetic or Psionic (needs Utopia)',
        'why': 'Egalitarian + Free Haven = happy, immigrant-magnet pops; Charismatic and '
               'Beacon of Liberty keep stability high while Thrifty pumps trade value. '
               'A peaceful, snowballing economy.',
    },
    {
        'name': 'Agrarian Idyll (Tall)',
        'goals': ['Tall', 'Economy'],
        'dlc': BASE,
        'ethics': ['Fanatic Pacifist', 'Egalitarian'],
        'authority': 'Democratic',
        'civics': ['Agrarian Idyll', 'Environmentalist'],
        'origin': 'Prosperous Unification',
        'traits': ['Agrarian', 'Conservationist', 'Traditional', 'Sedentary (-)', 'Deviants (-)'],
        'ascension': 'Genetic / Biomorphosis (needs BioGenesis)',
        'why': 'Pacifist stability + Agrarian Idyll let rural districts carry your economy with '
               'low sprawl, so you play tall and efficient. Conservationist cuts upkeep and '
               'Traditional accelerates the unity you need for traditions and ascension. '
               'Deviants is a non-issue for a tall, largely single-species empire.',
    },

    # ---------------- Utopia ----------------
    {
        'name': 'Hive Devouring Swarm',
        'goals': ['Gestalt', 'Military', 'Wide'],
        'dlc': UTOPIA,
        'ethics': ['Gestalt Consciousness'],
        'authority': 'Hive Mind',
        'civics': ['Devouring Swarm', 'Subspace Ephapse'],
        'origin': 'Prosperous Unification',
        'traits': ['Strong', 'Rapid Breeders', 'Wasteful (-)', 'Deviants — n/a'],
        'ascension': 'Genetic / Biomorphosis (needs BioGenesis)',
        'why': 'No consumer goods, no happiness, free war on everyone. Rapid Breeders + the '
               'swarm growth bonuses flood the galaxy with pops while Strong makes your armies '
               'and workers vicious. Pure aggression and expansion.',
    },
    {
        'name': 'Synthetic Ascendancy',
        'goals': ['Tech', 'Tall'],
        'dlc': UTOPIA,
        'ethics': ['Fanatic Materialist', 'Authoritarian'],
        'authority': 'Dictatorial',
        'civics': ['Technocracy', 'Meritocracy'],
        'origin': 'Prosperous Unification',
        'traits': ['Intelligent', 'Natural Physicists', 'Quick Learners', 'Fleeting (-)', 'Quarrelsome (-)'],
        'ascension': 'Synthetic',
        'why': 'Rush the Synthetic ascension path: once your pops are synths, output soars and '
               'food/consumer-goods worries vanish. Technocracy + Intelligent gets you there '
               'fastest; Fleeting is a free dump because synths discard biological lifespans, '
               'and Quarrelsome barely matters when you are racing for ascension, not harmony.',
    },
    {
        'name': 'Psionic Enlightened',
        'goals': ['Tall', 'Tech'],
        'dlc': UTOPIA,
        'ethics': ['Fanatic Spiritualist', 'Militarist'],
        'authority': 'Imperial',
        'civics': ['Imperial Cult', 'Aristocratic Elite'],
        'origin': 'Prosperous Unification',
        'traits': ['Intelligent', 'Natural Sociologists', 'Traditional', 'Repugnant (-)'],
        'ascension': 'Psionic',
        'why': 'Fanatic Spiritualist makes the rare Psionic Theory tech far more likely, '
               'unlocking the Psionic path and the Shroud. Imperial Cult + Spiritualist gives '
               'huge unity/amenities, and psionic pops add output plus powerful Shroud rewards.',
    },

    # ---------------- BioGenesis ----------------
    {
        'name': 'Wilderness Living World',
        'goals': ['Tall', 'Bio', 'Gestalt'],
        'dlc': BIOGENESIS,
        'ethics': ['Gestalt Consciousness'],
        'authority': 'Hive Mind',
        'civics': ['Aerospace Adaptation', 'One Mind'],
        'origin': 'Wilderness',
        'traits': ['Intelligent', 'Rapid Breeders', 'Strong', 'Sedentary (-)', 'Nonadaptive (-)'],
        'ascension': 'Biomorphosis — Purity (only path Wilderness allows)',
        'why': 'You ARE a sapient planet, growing as a tall living ecosystem and fielding '
               'bioships built from food, not minerals. Wilderness blocks every ascension '
               'path except the Purity branch of Biomorphosis, so lean into Purity to perfect '
               'your single living species. One Mind rewards your single-species nature and '
               'Aerospace Adaptation strengthens your food-grown bioship fleets. Nonadaptive '
               'costs nothing — the Wilderness origin keeps you on your one living world anyway.',
    },
    {
        'name': 'Evolutionary Predators',
        'goals': ['Military', 'Bio'],
        'dlc': BIOGENESIS,
        'ethics': ['Fanatic Militarist', 'Xenophobe'],
        'authority': 'Dictatorial',
        'civics': ['Genetic Identification', 'Distinguished Admiralty'],
        'origin': 'Evolutionary Predators',
        'traits': ['Strong', 'Industrious', 'Rapid Breeders', 'Slow Learners (-)', 'Repugnant (-)'],
        'ascension': 'Biomorphosis — Purity',
        'why': 'You literally eat rivals to absorb their best genetic traits, so every war makes '
               'your species stronger. Militarist + Xenophobe fuels constant hunting; Purity '
               'Biomorphosis bakes your stolen advantages into a perfected master species. '
               'Repugnant barely matters — Xenophobe predators were never trying to make friends.',
    },
    {
        'name': 'Clone-Vat Swarm',
        'goals': ['Wide', 'Bio', 'Economy'],
        'dlc': BIOGENESIS,
        'ethics': ['Authoritarian', 'Militarist'],
        'authority': 'Dictatorial',
        'civics': ['Crowdsourcing', 'Meritocracy'],
        'origin': 'Prosperous Unification',
        'traits': ['Rapid Breeders', 'Communal', 'Strong', 'Repugnant (-)'],
        'ascension': 'Biomorphosis — Cloning',
        'why': 'Cloning Biomorphosis plus growth traits gives explosive pop output — colonise '
               'and fill worlds faster than anyone. Meritocracy turns those plentiful pops into '
               'strong specialists; a wide, pop-driven economic juggernaut. Repugnant costs '
               'nothing since a clone-vat empire is not trying to win hearts and minds.',
    },
    {
        'name': 'Gene Purists (Tall)',
        'goals': ['Tall', 'Bio', 'Tech'],
        'dlc': BIOGENESIS,
        'ethics': ['Fanatic Authoritarian', 'Materialist'],
        'authority': 'Imperial',
        'civics': ['Genetic Identification', 'Civil Education'],
        'origin': 'Prosperous Unification',
        'traits': ['Intelligent', 'Talented', 'Quick Learners', 'Nonadaptive (-)'],
        'ascension': 'Biomorphosis — Purity',
        'why': 'Purity Biomorphosis builds one flawless, heavily-traited master species. Civil '
               'Education + Materialist push leader and research quality, and Genetic '
               'Identification keeps your perfected pops dominant. A tall, high-output empire.',
    },
    {
        'name': 'Starlit Citadel Defender',
        'goals': ['Military', 'Tall'],
        'dlc': BIOGENESIS,
        'ethics': ['Militarist', 'Xenophobe'],
        'authority': 'Oligarchic',
        'civics': ['Distinguished Admiralty', 'Functional Architecture'],
        'origin': 'Starlit Citadel',
        'traits': ['Strong', 'Industrious', 'Quarrelsome (-)'],
        'ascension': 'Biomorphosis — Mutation',
        'why': 'Early access to the Deep Space Citadel megastructure turns your chokepoints '
               'into fortresses — ideal for a defensive, turtle-then-counterattack game. '
               'Distinguished Admiralty sharpens the fleets you anchor there and Functional '
               'Architecture makes building up those strongpoints cheaper.',
    },
]


def _owns(owned_names, required):
    from .dlc import has
    return all(has(owned_names, kw) for kw in required)


def recommend_builds(owned_names, goal=None):
    """Return builds the player can make (DLC-filtered), optionally by goal.

    Each returned build carries an extra 'dlc_label' for display.
    """
    out = []
    for b in BUILDS:
        if not _owns(owned_names, b['dlc']):
            continue
        if goal and goal not in b['goals']:
            continue
        item = dict(b)
        item['dlc_label'] = ' + '.join(b['dlc']) if b['dlc'] else 'Base game'
        out.append(item)
    return out
