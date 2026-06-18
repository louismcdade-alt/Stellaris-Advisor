from advisor.validate import (_ethic_requirements, _build_ethic_ids, _ethic_ok,
                               _trait_opposites, _traits_conflict)


def test_ethic_requirements_parses_or_as_required():
    block = '''
    civic_example = {
        possible = {
            ethics = {
                OR = {
                    text = civic_tooltip_authoritarian
                    value = ethic_authoritarian
                    value = ethic_fanatic_authoritarian
                }
            }
        }
    }
    '''
    required, excluded = _ethic_requirements(block)
    assert required == {'ethic_authoritarian', 'ethic_fanatic_authoritarian'}
    assert excluded == set()


def test_ethic_requirements_parses_not_nor_as_excluded():
    block = '''
    civic_example = {
        possible = {
            ethics = {
                NOR = {
                    text = civic_tooltip_not_egalitarian
                    value = ethic_egalitarian
                    value = ethic_fanatic_egalitarian
                }
            }
        }
    }
    '''
    required, excluded = _ethic_requirements(block)
    assert required == set()
    assert excluded == {'ethic_egalitarian', 'ethic_fanatic_egalitarian'}


def test_ethic_requirements_discards_gestalt_noise():
    # Every non-gestalt civic excludes gestalt consciousness in `potential` —
    # that's redundant with the existing authority-category filtering, so it
    # should never show up as a meaningful requirement/exclusion.
    block = '''
    civic_example = {
        potential = {
            ethics = { NOT = { value = ethic_gestalt_consciousness } }
        }
        possible = {
            ethics = { OR = { value = ethic_militarist } }
        }
    }
    '''
    required, excluded = _ethic_requirements(block)
    assert required == {'ethic_militarist'}
    assert excluded == set()


def test_build_ethic_ids_maps_labels_including_fanatic():
    ids = _build_ethic_ids(['Fanatic Materialist', 'Xenophile'])
    assert ids == {'ethic_fanatic_materialist', 'ethic_xenophile'}


def test_ethic_ok_required_and_excluded():
    have = {'ethic_egalitarian'}
    assert _ethic_ok(set(), set(), have) is True
    assert _ethic_ok({'ethic_authoritarian'}, set(), have) is False
    assert _ethic_ok({'ethic_egalitarian'}, set(), have) is True
    assert _ethic_ok(set(), {'ethic_egalitarian'}, have) is False


def test_trait_opposites_parses_quoted_list():
    block = '''
    trait_rapid_breeders = {
        cost = 2
        opposites = { "trait_slow_breeders" "trait_fertile" }
    }
    '''
    assert _trait_opposites(block) == {'trait_slow_breeders', 'trait_fertile'}


def test_trait_opposites_handles_multiline_block():
    block = '''
    trait_auto_mod_biological = {
        opposites = {
            "trait_wilderness"
        }
    }
    '''
    assert _trait_opposites(block) == {'trait_wilderness'}


def test_trait_opposites_empty_when_absent():
    assert _trait_opposites('trait_x = { cost = 2 }') == set()


def test_traits_conflict_checks_both_directions():
    info = {
        'trait_rapid_breeders': {'opposites': {'trait_slow_breeders'}},
        'trait_slow_breeders': {'opposites': set()},
        'trait_unrelated': {'opposites': set()},
    }
    assert _traits_conflict('trait_rapid_breeders', 'trait_slow_breeders', info) is True
    assert _traits_conflict('trait_slow_breeders', 'trait_rapid_breeders', info) is True
    assert _traits_conflict('trait_rapid_breeders', 'trait_unrelated', info) is False
