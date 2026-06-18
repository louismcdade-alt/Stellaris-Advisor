from advisor.analyze import analyze_economy, analyze_military


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
