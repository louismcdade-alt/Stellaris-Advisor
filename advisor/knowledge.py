"""
Game knowledge: origin tips, civic tips, and ascension-path recommendations.

This is the "strategy book" part of the advisor. It's intentionally kept as
plain data + small functions so it's easy to extend as you learn more or as the
game changes between patches.

Ascension note (Stellaris 4.x): the four organic/synthetic ascension paths are
adopted as *tradition trees* (Genetic, Cybernetic, Synthetic, Psionic). Each is
unlocked by researching its prerequisite technology and then taking up the tree;
finishing it transforms your whole species. We detect the active path from the
empire's tradition trees and recommend one that fits the empire's ethics.
"""

# ---------------------------------------------------------------------------
# Origins — only the more impactful ones; others simply produce no card.
# ---------------------------------------------------------------------------
ORIGIN_TIPS = {
    'origin_tree_of_life': (
        'Origin: Tree of Life',
        'Your Tree gives empire-wide bonuses that grow as it levels — keep your '
        'core worlds and the Tree protected, and lean into pop growth/unity.'),
    'origin_galactic_doorstep': (
        'Origin: Galactic Doorstep',
        'A dormant gateway sits in your home system. Research gateway activation '
        'to unlock galaxy-spanning movement long before rivals.'),
    'origin_void_dwellers': (
        'Origin: Void Dwellers',
        'You live on habitats, not planets. Prioritise habitat tech, trade and '
        'researcher/specialist jobs; you have weak habitability on normal worlds.'),
    'origin_shattered_ring': (
        'Origin: Shattered Ring',
        'Your ring-world segments are your heartland — repair and develop them, '
        'and protect the home system since it is your economy.'),
    'origin_scion': (
        'Origin: Scion',
        'Your Fallen Empire patron can gift tech and protection — stay in their '
        'favour and use the early-game safety to expand aggressively.'),
    'origin_doomsday': (
        'Origin: Doomsday',
        'Your homeworld will explode — you are on a timer. Expand and resettle off '
        'the homeworld fast before it is destroyed.'),
    'origin_remnants': (
        'Origin: Remnants',
        'Your relic homeworld can be excavated for strong bonuses — dig the chain '
        'and exploit the extra building slots.'),
    'origin_lost_colony': (
        'Origin: Lost Colony',
        'There is a stronger humanoid cousin empire out there — decide early '
        'whether to befriend or rival them.'),
}

# ---------------------------------------------------------------------------
# Civics — surfaced when present; we show at most a couple to avoid clutter.
# ---------------------------------------------------------------------------
CIVIC_TIPS = {
    'civic_technocracy': (
        'Civic: Technocracy',
        'Researchers also produce a share of physics — overbuild labs and '
        'researcher jobs; your tech lead is your win condition.'),
    'civic_mining_guilds': (
        'Civic: Mining Guilds',
        'Bonus minerals from miners — favour mineral-heavy builds and feed the '
        'surplus into alloys and construction.'),
    'civic_merchant_guilds': (
        'Civic: Merchant Guilds',
        'Extra trade value and clerk jobs — build trade-focused worlds and keep '
        'trade routes protected from piracy.'),
    'civic_beacon_of_liberty': (
        'Civic: Beacon of Liberty',
        'High stability/unity from low sprawl — play a bit taller and cash the '
        'unity into traditions and ascension perks.'),
    'civic_inwards_perfection': (
        'Civic: Inward Perfection',
        'No offensive wars and limited diplomacy, but big growth/unity/stability. '
        'Play tall, max out your few worlds, and rush traditions.'),
    'civic_fanatic_purifiers': (
        'Civic: Fanatic Purifiers',
        'Bonus war damage and no diplomacy — out-tech and out-build neighbours, '
        'then cleanse them. War is your only foreign policy.'),
    'civic_pompous_purists': (
        'Civic: Pompous Purists',
        'Diplomatic penalties but strong bonuses — expect rivals and prepare to '
        'defend; lean on your edicts and economy.'),
    'civic_meritocracy': (
        'Civic: Meritocracy',
        'Specialists produce more — push specialist jobs (researchers, '
        'metallurgists, artisans) over basic workers.'),
    'civic_corporate_dominion': (
        'Civic: Corporate Dominion',
        'Extra branch-office slot — aggressively open branch offices on every '
        'empire you have commercial pacts with.'),
    'civic_hive_devouring_swarm': (
        'Civic: Devouring Swarm',
        'Eat the galaxy: bonus army damage and free war on everyone. Never stop '
        'expanding, and keep growth high to replace losses.'),
    'civic_machine_servitor': (
        'Civic: Rogue Servitor',
        'Your organic "bio-trophies" generate huge unity/amenities — pamper them '
        'and protect them; they are your unity engine.'),
}

# ---------------------------------------------------------------------------
# Ascension paths — tradition tree + the perk that opens it, with a fit note.
# ---------------------------------------------------------------------------
# Tech prerequisites confirmed from save tech ids + the official Paradox wiki.
ASCENSION_PATHS = {
    'genetic': {
        'tree': 'tradition_genetics',
        'perks': {'ap_engineered_evolution', 'ap_evolutionary_mastery', 'ap_biomorphosis'},
        'name': 'Genetic',
        'prereq_tech': {'tech_gene_tailoring'},
        'prereq_name': 'Gene Tailoring (follows Genome Mapping)',
        'desc': 'Reshape your species with extra trait points, cloning and tailored '
                'sub-species. The flexible path — strong for tall, pop-focused and '
                'hive empires.',
    },
    'cybernetic': {
        'tree': 'tradition_cybernetics',
        'perks': {'ap_the_flesh_is_weak', 'ap_organo_machine_interfacing'},
        'name': 'Cybernetic',
        'prereq_tech': {'tech_integrated_cybernetics'},
        'prereq_name': 'Integrated Cybernetics (follows Powered Exoskeletons + '
                       'Colonial Centralization)',
        'desc': 'Turn pops into cyborgs: strong production, habitability and army '
                'bonuses that blend organic and machine. A powerful all-rounder.',
    },
    'synthetic': {
        'tree': 'tradition_synthetics',
        'perks': {'ap_synthetic_evolution', 'ap_synthetic_age'},
        'name': 'Synthetic',
        'prereq_tech': {'tech_synthetic_personality_matrix', 'tech_synthetic_thought_patterns'},
        'prereq_name': 'Synthetic Personality Matrix (advanced robotics/AI line)',
        'desc': 'Convert your pops to synthetics for the highest output and no food/'
                'consumer-goods worries. Best for Materialists.',
    },
    'psionic': {
        'tree': 'tradition_psionics',
        'perks': {'ap_mind_over_matter', 'ap_transcendence'},
        'name': 'Psionic',
        'prereq_tech': {'tech_psionic_theory'},
        'prereq_name': 'Psionic Theory (rare tech — easier to roll as Spiritualist)',
        'desc': 'Unlock psionic pops and the Shroud for powerful, sometimes random '
                'bonuses. Best for Spiritualists.',
    },
}

# Tech that, by itself, grants an ascension-perk slot (besides finishing a tree).
ASCENSION_THEORY = 'tech_ascension_theory'

# Machine Intelligence ascension (The Machine Age DLC). Unlocked by the Synthetic
# Age perk, which starts a situation; at the end you pick ONE of these trees.
# Machines cannot take the organic paths (Genetic/Cybernetic/Synthetic/Psionic).
MACHINE_PATHS = {
    'modularity': {
        'tree': 'tradition_modularity', 'name': 'Modularity',
        'desc': 'Swappable modular pops and great flexibility — the balanced, '
                'all-rounder machine path.',
    },
    'nanotech': {
        'tree': 'tradition_nanotech', 'name': 'Nanotech',
        'desc': 'Nanite swarms and aggressive military/industrial power — best for '
                'warlike machine empires.',
    },
    'virtuality': {
        'tree': 'tradition_virtuality', 'name': 'Virtuality',
        'desc': 'Fewer, virtual pops with huge per-pop output — a strong tall, '
                'research-focused path.',
    },
}
MACHINE_UNLOCK_PERK = 'ap_synthetic_age'

# Strong "generic" perks worth picking up, with a short why (from the wiki).
GENERIC_PERKS = {
    'ap_technological_ascendancy': 'big research boost and +50% rare-tech chance '
        '(usually a great first perk)',
    'ap_interstellar_dominion': '-20% claim/starbase cost and -25% empire-size penalty '
        '— ideal for wide empires',
    'ap_grasp_the_void': '+5 starbase capacity and better FTL-tech odds',
    'ap_galactic_wonders': 'unlocks megastructures (Dyson Sphere, Ring World, etc.)',
    'ap_galactic_force_projection': '+150 naval capacity, +20% command limit, +1 commander',
    'ap_world_shaper': 'Gaia-world terraforming and -25% terraform cost',
    'ap_defender_of_the_galaxy': '+50% damage to the endgame crisis and big opinion gains',
    'ap_executive_vigor': 'longer, stronger edicts',
    'ap_one_vision': 'unity and stability from a unified empire',
}

# Perks worth recommending only for certain empires.
RESTRICTED_PERKS = {
    'ap_consecrated_worlds': ('spiritualist', 'Consecrated Worlds',
        'consecrate planets for empire-wide unity/bonuses — a Spiritualist staple'),
    'ap_universal_transactions': ('megacorp', 'Universal Transactions',
        'huge trade value from your branch offices — a top Megacorp perk'),
    'ap_colossus': ('militarist', 'Colossus Project',
        'build a planet-killer — strong for an aggressive Militarist'),
}

# Readable names for perks we might mention.
PERK_NAMES = {
    'ap_technological_ascendancy': 'Technological Ascendancy',
    'ap_interstellar_dominion': 'Interstellar Dominion',
    'ap_grasp_the_void': 'Grasp the Void',
    'ap_galactic_wonders': 'Galactic Wonders',
    'ap_galactic_force_projection': 'Galactic Force Projection',
    'ap_world_shaper': 'World Shaper',
    'ap_defender_of_the_galaxy': 'Defender of the Galaxy',
    'ap_executive_vigor': 'Executive Vigor',
    'ap_one_vision': 'One Vision',
    'ap_transcendent_learning': 'Transcendent Learning',
    'ap_eternal_vigilance': 'Eternal Vigilance',
    'ap_synthetic_evolution': 'Synthetic Evolution',
    'ap_mind_over_matter': 'Mind over Matter',
    'ap_engineered_evolution': 'Engineered Evolution',
    'ap_the_flesh_is_weak': 'The Flesh is Weak',
}


def perk_name(ap):
    return PERK_NAMES.get(ap, ap.replace('ap_', '').replace('_', ' ').title())


def origin_civic_cards(profile):
    """Return advice cards for the empire's origin and most-impactful civics."""
    cards = []
    tip = ORIGIN_TIPS.get(profile.origin)
    if tip:
        cards.append(('origin', tip[0], tip[1]))
    shown = 0
    for civ in profile.civics:
        tip = CIVIC_TIPS.get(civ)
        if tip:
            cards.append(('civics', tip[0], tip[1]))
            shown += 1
            if shown >= 2:   # keep it focused
                break
    return cards


def _detect_path(trees, perks):
    treeset, perkset = set(trees), set(perks)
    for key, p in ASCENSION_PATHS.items():
        if p['tree'] in treeset or (perkset & p['perks']):
            return key
    return None


def recommend_path(profile):
    """Pick the ascension path that best fits this empire's identity."""
    if profile.is_machine:
        return None  # machine empires have their own (different) progression
    if profile.spiritualist:
        return 'psionic'
    if profile.materialist:
        return 'synthetic'
    if profile.is_hive or profile.xenophobe:
        return 'genetic'
    # No strong lean: cybernetic is the safe, strong all-rounder.
    return 'cybernetic'


def _owns(dlc, *keywords):
    """Whether the player owns a DLC; if DLC is unknown (None) assume yes."""
    if dlc is None:
        return True
    from .dlc import has
    return has(dlc, *keywords)


def ascension_cards(profile, perks, techs=None, dlc=None):
    """Advice about ascension perks and which path to pursue.

    `perks` = list of ap_* ids the empire has. `techs` = list of researched tech
    ids, used to check whether a path's prerequisite technology is already known.
    `dlc` = list of owned DLC names (gates path availability). The active path is
    detected from the empire's tradition trees plus perks.
    """
    cards = []
    perkset = set(perks)
    techset = set(techs or [])
    trees = getattr(profile, 'tradition_trees', []) or []
    active = _detect_path(trees, perks)
    has_utopia = _owns(dlc, 'utopia')
    has_machine_age = _owns(dlc, 'machine', 'age')

    # Machine Intelligence empires use a completely separate ascension system.
    if profile.is_machine:
        if has_machine_age:
            cards.extend(_machine_cards(profile, perkset, trees))
        else:
            cards.append(('ascension', 'Machine ascension unavailable (no Machine Age DLC)',
                          'The machine ascension paths (Modularity / Nanotech / Virtuality) '
                          'need The Machine Age DLC, which you don\'t have. Focus on the '
                          'strong general ascension perks instead.'))
        cards.extend(_generic_perk_cards(profile, perkset))
        return cards

    # Ascension perks and the organic paths come from Utopia.
    if not has_utopia:
        cards.append(('ascension', 'Ascension perks need Utopia',
                      'The ascension-perk and ascension-path system requires the Utopia DLC, '
                      'which you don\'t have. The other recommendations still apply.'))
        return cards

    if active:
        p = ASCENSION_PATHS[active]
        cards.append(('ascension', f'{p["name"]} ascension underway',
                      f'{p["desc"]} Finish the {p["name"]} tradition tree and take its '
                      f'perks to complete the transformation.'))
    else:
        rec = recommend_path(profile)
        if rec:
            p = ASCENSION_PATHS[rec]
            why = (
                'fits your Spiritualist ethics' if rec == 'psionic' else
                'fits your Materialist, tech-focused ethics' if rec == 'synthetic' else
                'fits your hive/pop-focused style' if rec == 'genetic' else
                'is the strong, flexible all-rounder')
            has_prereq = bool(techset & p['prereq_tech'])
            if has_prereq:
                gate = (f'You already have the prerequisite tech — take {_first_perk(p)} '
                        f'when a perk slot opens, then adopt the {p["name"]} tradition tree.')
            else:
                gate = (f'First research {p["prereq_name"]}; then take {_first_perk(p)} '
                        f'and the {p["name"]} tradition tree when you have a free perk slot.')
            cards.append(('ascension', f'Consider the {p["name"]} ascension path',
                          f'{p["desc"]} It {why}. {gate}'))

    # If they have no perks yet, point at how slots are unlocked.
    if not perkset and ASCENSION_THEORY not in techset:
        cards.append(('ascension', 'Unlock your first ascension perk',
                      'Finish a tradition tree or research Ascension Theory to open an '
                      'ascension-perk slot — these are some of the biggest power spikes '
                      'in the game.'))

    cards.extend(_generic_perk_cards(profile, perkset))
    return cards


def _machine_cards(profile, perkset, trees):
    """Machine-Intelligence ascension: the Modularity/Nanotech/Virtuality paths.

    Machines can't take the organic paths — these come from The Machine Age DLC
    and are opened by the Synthetic Age perk.
    """
    treeset = set(trees)
    active = next((m for m in MACHINE_PATHS.values() if m['tree'] in treeset), None)
    if active:
        return [('ascension', f'{active["name"]} ascension underway',
                 f'{active["desc"]} Finish the {active["name"]} tradition tree to complete '
                 f'your machine ascension.')]

    # Recommend one of the three by playstyle.
    if profile.militarist or profile.no_diplomacy or profile.assimilator:
        rec = MACHINE_PATHS['nanotech']
    elif profile.materialist:
        rec = MACHINE_PATHS['virtuality']
    else:
        rec = MACHINE_PATHS['modularity']
    note = ('Note: this is the machine ascension system (not the organic Cybernetic/'
            'Synthetic paths) and needs The Machine Age DLC.')
    if MACHINE_UNLOCK_PERK in perkset:
        how = (f'You\'ve taken Synthetic Age — finish the situation and pick a path. '
               f'{rec["name"]} fits you best: {rec["desc"]}')
    else:
        how = (f'Take the Synthetic Age ascension perk to start machine ascension, then '
               f'pick one of Modularity, Nanotech or Virtuality. {rec["name"]} fits you '
               f'best: {rec["desc"]}')
    return [('ascension', 'Machine ascension (Modularity / Nanotech / Virtuality)',
             f'{how} {note}')]


def _generic_perk_cards(profile, perkset):
    """Strong general-purpose and ethics-fitting perk suggestions (any empire)."""
    cards = []
    if 'ap_technological_ascendancy' not in perkset:
        cards.append(('ascension', 'Pick up Technological Ascendancy',
                      'A large research boost and +50% rare-tech chance — usually the '
                      'strongest opening perk. Take it as soon as a slot opens.'))
    else:
        for ap in ('ap_interstellar_dominion', 'ap_galactic_force_projection',
                   'ap_grasp_the_void', 'ap_galactic_wonders'):
            if ap not in perkset:
                cards.append(('ascension', f'Next perk idea: {perk_name(ap)}',
                              f'{GENERIC_PERKS[ap].capitalize()}.'))
                break

    for ap, (req, name, why) in RESTRICTED_PERKS.items():
        if ap in perkset:
            continue
        fits = ((req == 'spiritualist' and profile.spiritualist) or
                (req == 'megacorp' and profile.is_megacorp) or
                (req == 'militarist' and profile.militarist))
        if fits:
            cards.append(('ascension', f'Strong fit: {name}', f'{why.capitalize()}.'))
            break
    return cards


def _first_perk(path):
    """A readable name for the entry perk of an ascension path."""
    # Pick the canonical opener (sorted gives a stable, sensible choice).
    for ap in sorted(path['perks']):
        return perk_name(ap)
    return 'its ascension perk'
