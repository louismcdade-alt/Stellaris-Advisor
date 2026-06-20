from advisor.analyze import analyze_economy, analyze_military, analyze_species, analyze_diplomacy


def _player(**overrides):
    base = {
        'id': '0',
        'identity': {
            'authority': 'auth_democratic',
            'civics': [],
            'ethics': ['ethic_materialist'],
            'species_traits': [],
        },
        'resources': {'energy': 500, 'minerals': 500, 'alloys': 500, 'food': 500,
                       'consumer_goods': 500, 'influence': 100},
        'balance': {'energy': 0, 'minerals': 0, 'alloys': 0, 'food': 0,
                    'consumer_goods': 0, 'trade': 0},
        'military_power': 1000,
        'relations': [],
        'in_federation': False,
    }
    base.update(overrides)
    return base


def _snap(player, empires=None):
    return {'player': player, 'empires': empires or {}, 'date': '2200.01.01'}


def test_analyze_economy_flags_critical_runway():
    player = _player(resources={'energy': 20, 'minerals': 500, 'alloys': 500,
                                 'food': 500, 'consumer_goods': 500, 'influence': 100},
                      balance={'energy': -10, 'minerals': 0, 'alloys': 0, 'food': 0,
                               'consumer_goods': 0, 'trade': 0})
    snap = _snap(player)
    out = analyze_economy(snap)
    critical = [a for a in out if a['priority'] == 'critical']
    assert critical, 'expected a critical alert for energy about to run out'
    assert 'Energy' in critical[0]['title']


def test_analyze_economy_reports_stable_when_nothing_trending_down():
    snap = _snap(_player())
    out = analyze_economy(snap)
    assert len(out) == 1
    assert out[0]['priority'] == 'good'
    assert out[0]['title'] == 'Economy stable'


def test_analyze_military_warns_when_outgunned():
    player = _player(military_power=500)
    rival = {'id': '1', 'type': 'default', 'name': 'Rival Empire', 'military_power': 2000}
    snap = _snap(player, {'1': rival})
    out = analyze_military(snap)
    warnings = [a for a in out if a['priority'] == 'warning' and 'outguns' in a['title']]
    assert warnings
    assert 'Rival Empire' in warnings[0]['title']


def test_analyze_military_reports_strongest_when_player_leads():
    player = _player(military_power=5000)
    rival = {'id': '1', 'type': 'default', 'name': 'Rival Empire', 'military_power': 1000}
    snap = _snap(player, {'1': rival})
    out = analyze_military(snap)
    good = [a for a in out if a['priority'] == 'good']
    assert good
    assert good[0]['title'] == 'Strongest military among rivals'


def test_analyze_military_reports_active_war_by_opponent_name():
    player = _player(wars=[{'opponent': 'Oxbraxi', 'side': 'defender',
                            'war_exhaustion': 0.0427, 'start_date': '2273.09.04'}])
    out = analyze_military(_snap(player))
    warnings = [a for a in out if a['priority'] == 'warning' and 'Oxbraxi' in a['title']]
    assert warnings
    assert 'Defending against Oxbraxi' in warnings[0]['detail']
    assert '4%' in warnings[0]['detail']


def test_analyze_military_falls_back_to_recently_at_war_when_no_active_war():
    player = _player(last_date_at_war='2199.12.01')
    out = analyze_military(_snap(player))
    cards = [a for a in out if a['title'] == 'Recently at war']
    assert cards
    assert cards[0]['priority'] == 'info'


def test_analyze_military_no_war_card_when_neither_active_nor_recent():
    player = _player()
    out = analyze_military(_snap(player))
    assert not [a for a in out if 'war' in a['title'].lower()]


def test_analyze_species_tips_on_mapped_trait():
    player = _player()
    player['identity']['species_traits'] = ['trait_intelligent', 'trait_unmapped_xyz']
    out = analyze_species(_snap(player))
    assert len(out) == 1
    assert out[0]['category'] == 'research'
    assert 'research' in out[0]['detail'].lower()


def test_analyze_species_yields_nothing_for_unmapped_traits():
    player = _player()
    player['identity']['species_traits'] = ['trait_unmapped_xyz', 'trait_also_unmapped']
    out = analyze_species(_snap(player))
    assert out == []


def _diplomacy_setup(in_federation):
    rivalA = {'id': '1', 'type': 'default', 'name': 'Rival A', 'military_power': 100}
    contactB = {'id': '2', 'type': 'default', 'name': 'Contact B', 'military_power': 500}
    contactC = {'id': '3', 'type': 'default', 'name': 'Contact C', 'military_power': 200}
    player = _player(relations=[
        {'country': 1, 'communications': True, 'is_rival': True},
        {'country': 2, 'communications': True},
        {'country': 3, 'communications': True},
    ], in_federation=in_federation)
    snap = _snap(player, {'1': rivalA, '2': contactB, '3': contactC})
    return snap


def test_analyze_diplomacy_suggests_ally_when_not_in_federation():
    out = analyze_diplomacy(_diplomacy_setup(in_federation=False))
    titles = [a['title'] for a in out]
    assert 'No allies yet — consider a defensive pact' in titles


def test_analyze_diplomacy_suppresses_ally_suggestion_when_in_federation():
    out = analyze_diplomacy(_diplomacy_setup(in_federation=True))
    titles = [a['title'] for a in out]
    assert 'No allies yet — consider a defensive pact' not in titles
    assert 'Federation member' in titles
    good = [a for a in out if a['title'] == 'Federation member']
    assert good[0]['priority'] == 'good'
