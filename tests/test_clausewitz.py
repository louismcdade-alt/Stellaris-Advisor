from advisor.clausewitz import parse, extract_block


def test_parse_simple_key_value():
    doc = parse('name="Sol" date=2200.01.01 count=5')
    assert doc['name'] == 'Sol'
    assert doc['date'] == '2200.01.01'
    assert doc['count'] == 5


def test_parse_booleans_and_negative_numbers():
    doc = parse('active=yes inactive=no shield=-12.5')
    assert doc['active'] is True
    assert doc['inactive'] is False
    assert doc['shield'] == -12.5


def test_parse_duplicate_keys_become_list():
    doc = parse('technology="tech_a" technology="tech_b" technology="tech_c"')
    assert list(doc['technology']) == ['tech_a', 'tech_b', 'tech_c']


def test_parse_nested_block():
    doc = parse('country={ name="Empire" fleet={ power=42 } }')
    assert doc['country']['name'] == 'Empire'
    assert doc['country']['fleet']['power'] == 42


def test_parse_bare_array():
    doc = parse('colors={ "black" "black" } random={ 0 4207665165 }')
    assert doc['colors'] == ['black', 'black']
    assert doc['random'] == [0, 4207665165]


def test_extract_block_finds_matching_braces():
    text = 'prefix\ncountry={\n  name="Empire"\n}\nsuffix'
    block, end = extract_block(text, 'country')
    assert block == '{\n  name="Empire"\n}'
    assert end == text.index('}') + 1


def test_extract_block_handles_nested_braces():
    text = 'fleet={ ships={ a=1 b={ c=2 } } } trailer=1'
    block, end = extract_block(text, 'fleet')
    assert block is not None
    assert block.count('{') == block.count('}')
    assert block.startswith('{') and block.endswith('}')
    inner = parse(block[1:-1])
    assert inner['ships']['a'] == 1
    assert inner['ships']['b']['c'] == 2


def test_extract_block_returns_none_if_missing():
    block, end = extract_block('no_match_here=1', 'country')
    assert block is None
    assert end == -1
