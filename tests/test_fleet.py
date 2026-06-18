from advisor import fleet


def test_recommend_with_no_warships_suggests_starting_hull():
    player = {'fleet': {'composition': {}}, 'researched_techs': [], 'used_naval_capacity': 0}
    out = fleet.recommend(player)
    assert out['warships'] == 0
    assert out['tier'] == 'Corvette'
    assert any('no warships' in n for n in out['notes'])
    # Default budget (16) split entirely on the only unlocked tier (corvette).
    assert out['rows'] == [] or all(r['class'] == 'Corvette' for r in out['rows'])


def test_recommend_scales_budget_to_existing_fleet():
    # 20 corvettes already in the field -> budget should track that (not the
    # default-of-16 floor), since 20 * slot_cost(1) = 20 >= 8.
    player = {'fleet': {'composition': {'corvette': 20}},
              'researched_techs': [], 'used_naval_capacity': 20}
    out = fleet.recommend(player)
    assert out['warships'] == 20
    corvette_row = next(r for r in out['rows'] if r['class'] == 'Corvette')
    assert corvette_row['current'] == 20
    assert corvette_row['recommended'] == 20


def test_recommend_unlocks_destroyers_with_tech():
    player = {'fleet': {'composition': {'corvette': 10, 'destroyer': 2}},
              'researched_techs': ['tech_destroyers'], 'used_naval_capacity': 14}
    out = fleet.recommend(player)
    classes = {r['class'] for r in out['rows']}
    assert 'Destroyer' in classes
    assert out['tier'] == 'Destroyer'
