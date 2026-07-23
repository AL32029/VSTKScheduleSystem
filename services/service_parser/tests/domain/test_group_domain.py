import pytest

from service_parser.domain.entities import Group, GroupParser
from service_parser.domain.exceptions.parser_exceptions import InvalidGroupNumberFormatError, NegativeGroupPositionError


@pytest.mark.parametrize("source,index", [
    ['ЖБИ-21', 'жби21'],
    [' ЖБИ-21 ', 'жби21'],
    ['ЖбИ-21', 'жби21'],
    ['ОС-21', 'ос21'],
    ['Ос-21', 'ос21'],
    ['ПЭС-215', 'пэс215'],
    ['пЭС-215', 'пэс215'],
])
def test_group_creation_and_index_normalization(source, index):
    group = Group(source)

    assert group.number == source.upper().strip()

    assert str(group) == source.upper().strip()

    assert group.index == index


@pytest.mark.parametrize("first_group,second_group", [
    ['ЖБИ-21', 'ЖбИ-21'],
    ['ОС-21', 'ос-21'],
    ['ПэС-215', 'Пэс-215'],
])
def test_group_equalizing(first_group, second_group):
    first_group_model = Group(first_group)
    second_group_model = Group(second_group)

    assert first_group_model == second_group_model


@pytest.mark.parametrize("first_group,second_group", [
    ['ЖБИ-21', 'ЖбИ-21'],
    ['ОС-21', 'ос-21'],
    ['ПэС-215', 'Пэс-215'],
])
def test_group_equalizing_not_implemented_error(first_group, second_group):
    first_group_model = Group(first_group)

    with pytest.raises(NotImplementedError):
        assert first_group_model == second_group


@pytest.mark.parametrize("first_group,second_group", [
    ['ЖБИ-21', 'ЖбИ-21'],
    ['ОС-21', 'ос-21'],
    ['ПэС-215', 'Пэс-215'],
])
def test_group_hash_equalizing(first_group, second_group):
    first_group_model = Group(first_group)
    second_group_model = Group(second_group)

    assert hash(first_group_model) == hash(second_group_model)

    assert hash(first_group_model) == hash(first_group_model)

    assert len({first_group_model, second_group_model}) == 1


@pytest.mark.parametrize('source', [
    'ЖБИ 21',
    '-32',
    'ГРУППА-20',
    'А-1',
])
def test_group_creation_error_invalid_format(source):
    with pytest.raises(InvalidGroupNumberFormatError) as exc_info:
        Group(source)

    assert exc_info.value.args[0] == f'Invalid group number: {source!r}'


@pytest.mark.parametrize('source,pos_x,pos_y', [
    ['ЖБИ-21', 1, 1],
    [' ЖБИ-21 ', 2, 2],
    ['ОС-21', 4, 3],
    ['ПЭС-215', 2, 12],
])
def test_group_parser_creation_and_index_normalization(source, pos_x, pos_y):
    group_parser = GroupParser(source, pos_x, pos_y)

    assert isinstance(group_parser, GroupParser)
    assert isinstance(group_parser.group, Group)

    assert group_parser.group.number == source.upper().strip()
    assert str(group_parser) == source.upper().strip()

    assert group_parser.pos_x == pos_x
    assert group_parser.pos_y == pos_y


@pytest.mark.parametrize('source,pos_x,pos_y', [
    ['ЖБИ-21', -10, 1],
    [' ЖБИ-21 ', 2, -2],
    ['ОС-21', -4, -3],
    ['ПЭС-215', -2, 12],
])
def test_group_parser_creation_exception_negative_position(source, pos_x, pos_y):
    with pytest.raises(NegativeGroupPositionError) as exc_info:
        GroupParser(source, pos_x, pos_y)

    if pos_x < 0:
        assert exc_info.value.args[0] == 'X position must be positive'
    elif pos_y < 0:
        assert exc_info.value.args[0] == 'Y position must be positive'


@pytest.mark.parametrize("first_group,second_group", [
    ['ЖБИ-21', 'ЖбИ-21'],
    ['ОС-21', 'ос-21'],
    ['ПэС-215', 'Пэс-215'],
])
def test_group_parser_equalizing(first_group, second_group):
    first_group_model = GroupParser(first_group, 1, 1)
    second_group_model = GroupParser(second_group, 1, 1)

    assert first_group_model == second_group_model


@pytest.mark.parametrize("first_group,second_group", [
    ['ЖБИ-21', 'ЖбИ-21'],
    ['ОС-21', 'ос-21'],
    ['ПэС-215', 'Пэс-215'],
])
def test_group_parser_equalizing_not_implemented_error(first_group, second_group):
    first_group_model = GroupParser(first_group, 1, 1)

    with pytest.raises(NotImplementedError):
        assert first_group_model == second_group


@pytest.mark.parametrize("first_group,second_group", [
    ['ЖБИ-21', 'ЖбИ-21'],
    ['ОС-21', 'ос-21'],
    ['ПэС-215', 'Пэс-215'],
])
def test_group_parser_hash_equalizing(first_group, second_group):
    first_group_model = GroupParser(first_group, 1, 1)
    second_group_model = GroupParser(second_group, 1, 1)

    assert hash(first_group_model) == hash(second_group_model)

    assert hash(first_group_model) == hash(first_group_model)

    assert len({first_group_model, second_group_model}) == 1
