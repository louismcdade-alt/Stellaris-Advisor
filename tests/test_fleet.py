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


def test_recommend_reports_current_and_recommended_naval_capacity():
    # 20 corvettes, fallback slot_cost(corvette) == 1 -> current capacity 20.
    # Budget tracks the existing fleet (20 >= 8), and the only unlocked tier
    # is corvette, so the whole budget goes to corvettes -> recommended == 20.
    player = {'fleet': {'composition': {'corvette': 20}},
              'researched_techs': [], 'used_naval_capacity': 20}
    out = fleet.recommend(player)
    assert out['current_naval_capacity'] == 20
    assert out['recommended_naval_capacity'] == 20


def test_recommend_naval_capacity_totals_only_count_this_hull_family():
    # destroyer slot_cost == 2 (fallback); 5 destroyers -> current capacity 10.
    player = {'fleet': {'composition': {'destroyer': 5}},
              'researched_techs': ['tech_destroyers'], 'used_naval_capacity': 10}
    out = fleet.recommend(player)
    assert out['current_naval_capacity'] == 10
    assert out['recommended_naval_capacity'] > 0


def test_recommend_surfaces_colossus_as_a_special_not_a_tier_row():
    player = {'fleet': {'composition': {'corvette': 10, 'colossus': 1}},
              'researched_techs': [], 'used_naval_capacity': 42}
    out = fleet.recommend(player)
    assert out['specials'] == [{'class': 'Colossus', 'count': 1, 'naval_capacity': 32}]
    assert not any(r['class'] == 'Colossus' for r in out['rows'])
    # Owning a Colossus must not change the corvette tier's own recommendation.
    plain = fleet.recommend({'fleet': {'composition': {'corvette': 10}},
                              'researched_techs': [], 'used_naval_capacity': 10})
    corvette_with = next(r for r in out['rows'] if r['class'] == 'Corvette')
    corvette_without = next(r for r in plain['rows'] if r['class'] == 'Corvette')
    assert corvette_with['recommended'] == corvette_without['recommended']


def test_recommend_specials_empty_with_no_capital_hulls():
    player = {'fleet': {'composition': {'corvette': 5}},
              'researched_techs': [], 'used_naval_capacity': 5}
    out = fleet.recommend(player)
    assert out['specials'] == []
