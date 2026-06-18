"""
Interpret an empire's identity (ethics, authority, civics, origin, traits) into
the things the advice engine actually needs to know:

  * What kind of empire is this? (gestalt? genocidal? trade-focused?)
  * Which economy rules even apply? (machines have no food; gestalts no consumer
    goods; only some empires care about trade.)
  * What playstyle advice fits? (a Militarist should press war; a Pacifist can't
    even declare offensive wars; a Devouring Swarm has no diplomacy at all.)

Keeping this separate from analyze.py means all the "who is this empire" logic
lives in one place, and the rules can just ask the profile yes/no questions.
"""

# Civics that make an empire permanently hostile / unable to do normal diplomacy.
_GENOCIDAL = {
    'civic_hive_devouring_swarm': 'Devouring Swarm',
    'civic_machine_terminator': 'Determined Exterminator',
    'civic_fanatic_purifiers': 'Fanatic Purifiers',
}
# Assimilators can't do normal diplomacy either, but play differently (assimilate
# rather than purge).
_ASSIMILATOR = {'civic_machine_assimilator': 'Driven Assimilator'}

_ETHIC_LABEL = {
    'militarist': 'Militarist', 'pacifist': 'Pacifist',
    'xenophobe': 'Xenophobe', 'xenophile': 'Xenophile',
    'materialist': 'Materialist', 'spiritualist': 'Spiritualist',
    'authoritarian': 'Authoritarian', 'egalitarian': 'Egalitarian',
}

_AUTH_LABEL = {
    'auth_democratic': 'Democracy', 'auth_oligarchic': 'Oligarchy',
    'auth_dictatorial': 'Dictatorship', 'auth_imperial': 'Empire',
    'auth_corporate': 'Megacorp', 'auth_hive_mind': 'Hive Mind',
    'auth_machine_intelligence': 'Machine Intelligence',
}


def _parse_ethics(ethics):
    """Return {base_ethic: 'normal'|'fanatic'} from raw ethic ids."""
    out = {}
    for e in ethics:
        if not isinstance(e, str):
            continue
        name = e.replace('ethic_', '')
        fanatic = name.startswith('fanatic_')
        name = name.replace('fanatic_', '')
        if name == 'gestalt_consciousness':
            out['gestalt'] = 'normal'
        else:
            out[name] = 'fanatic' if fanatic else out.get(name, 'normal')
    return out


class EmpireProfile:
    def __init__(self, identity):
        identity = identity or {}
        self.authority = identity.get('authority')
        self.civics = [c for c in identity.get('civics', []) if isinstance(c, str)]
        self.origin = identity.get('origin')
        self.government_type = identity.get('government_type')
        self.species_class = identity.get('species_class')
        self.species_name = identity.get('species_name')
        self.traits = [t for t in identity.get('species_traits', []) if isinstance(t, str)]
        self.tradition_trees = [t for t in identity.get('tradition_trees', [])
                                if isinstance(t, str)]
        self.ethics = _parse_ethics(identity.get('ethics', []))

        civset = set(self.civics)
        self.is_hive = self.authority == 'auth_hive_mind'
        self.is_machine = self.authority == 'auth_machine_intelligence'
        self.is_gestalt = self.is_hive or self.is_machine or 'gestalt' in self.ethics
        self.is_megacorp = self.authority == 'auth_corporate'

        self.genocidal_kind = next((label for civ, label in _GENOCIDAL.items()
                                    if civ in civset), None)
        self.assimilator = next((label for civ, label in _ASSIMILATOR.items()
                                 if civ in civset), None)
        self.inward = 'civic_inwards_perfection' in civset
        # No peaceful diplomacy is possible for purifiers/swarms/exterminators.
        self.no_diplomacy = self.genocidal_kind is not None

    # --- ethic questions ---
    def has(self, ethic):
        return ethic in self.ethics

    def is_fanatic(self, ethic):
        return self.ethics.get(ethic) == 'fanatic'

    @property
    def militarist(self): return self.has('militarist')
    @property
    def pacifist(self): return self.has('pacifist')
    @property
    def xenophobe(self): return self.has('xenophobe')
    @property
    def xenophile(self): return self.has('xenophile')
    @property
    def materialist(self): return self.has('materialist')
    @property
    def spiritualist(self): return self.has('spiritualist')

    # --- economy applicability ---
    def uses_consumer_goods(self):
        return not self.is_gestalt

    def uses_food(self):
        # Hive pops eat; machine pops don't.
        return not self.is_machine

    def uses_trade(self):
        return not self.is_gestalt

    # --- display ---
    def title(self):
        if self.genocidal_kind:
            return self.genocidal_kind
        if self.assimilator:
            return self.assimilator
        if self.is_gestalt:
            return _AUTH_LABEL.get(self.authority, 'Gestalt Consciousness')
        # Ordinary empire: "Fanatic Materialist, Xenophile Megacorp"
        # (Stellaris lists the fanatic ethic first.)
        order = ('militarist', 'pacifist', 'xenophobe', 'xenophile',
                 'materialist', 'spiritualist', 'authoritarian', 'egalitarian')
        present = [b for b in order if b in self.ethics]
        present.sort(key=lambda b: not self.is_fanatic(b))  # fanatic ethics first
        parts = [('Fanatic ' + _ETHIC_LABEL[b]) if self.is_fanatic(b) else _ETHIC_LABEL[b]
                 for b in present]
        auth = _AUTH_LABEL.get(self.authority, '')
        ethic_str = ', '.join(parts)
        return f'{ethic_str} {auth}'.strip() or auth or 'Empire'

    def identity_advice(self):
        """One tailored 'play to your strengths' card for this empire type."""
        if self.genocidal_kind == 'Devouring Swarm':
            return ('identity',
                    'Devouring Swarm — diplomacy is closed',
                    'Every empire is food; you cannot make peace or allies. Keep an '
                    'aggressive fleet, never stop conquering, and keep pop growth high to '
                    'feed your assembly. No consumer goods to manage — focus food, minerals '
                    'and alloys.')
        if self.genocidal_kind == 'Determined Exterminator':
            return ('identity',
                    'Determined Exterminator — no diplomacy',
                    'You purge organics rather than negotiate. No food or consumer goods — '
                    'run on energy, minerals and alloys. Expand relentlessly and keep your '
                    'fleet ahead of every neighbour.')
        if self.genocidal_kind == 'Fanatic Purifiers':
            return ('identity',
                    'Fanatic Purifiers — war is the only option',
                    'You cannot make peace with other empires. Out-tech and out-produce '
                    'your neighbours, then cleanse them. Lean on your bonus war damage.')
        if self.assimilator:
            return ('identity',
                    'Driven Assimilator — conquer to assimilate',
                    'No standard diplomacy; take organic worlds and cyborg-assimilate their '
                    'pops for growth. No food/consumer goods — manage energy and minerals.')
        if self.is_machine:
            return ('identity',
                    'Machine Intelligence — energy is life',
                    'No food or consumer goods. Machine pops run on energy upkeep, so watch '
                    'energy as you grow, and use minerals/alloys for expansion. You can\'t '
                    'use migration treaties.')
        if self.is_hive:
            return ('identity',
                    'Hive Mind — one will, no economy of happiness',
                    'No consumer goods or happiness/factions to manage; keep food positive '
                    'and amenities covered (maintenance drones). Expand by colonisation and '
                    'selective war — migration treaties aren\'t available to you.')
        # Ordinary empires: surface the dominant ethic's playstyle.
        if self.is_fanatic('militarist') or self.militarist:
            return ('identity',
                    'Militarist — press your advantage',
                    'Claims are cheaper and war works in your favour. Build fleets early, '
                    'pick fights you can win, and use the bonus war score / damage.')
        if self.is_fanatic('pacifist') or self.pacifist:
            return ('identity',
                    'Pacifist — you can\'t start offensive wars',
                    'You need claims or to be attacked to fight. Invest in a tall, efficient '
                    'economy, strong defensive fleets/starbases, and federations.')
        if self.is_fanatic('materialist') or self.materialist:
            return ('identity',
                    'Materialist — out-tech the galaxy',
                    'Research is your edge. Prioritise labs and researcher jobs, embrace '
                    'robots/AI, and aim for technological-ascendancy style perks.')
        if self.spiritualist:
            return ('identity',
                    'Spiritualist — unity and unrest',
                    'Lean on temples/unity and Spiritualist bonuses; avoid AI/synth paths '
                    'that clash with your pops\' ethics.')
        if self.is_megacorp:
            return ('identity',
                    'Megacorp — trade is your empire',
                    'Maximise trade value, build branch offices on other empires\' worlds, '
                    'and sign commercial pacts to grow your economy.')
        return None
