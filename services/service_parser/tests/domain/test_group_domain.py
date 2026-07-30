import pytest

from service_parser.domain.entities import Group, GroupParser
from service_parser.domain.exceptions import GroupNumberFormatError, GroupParserPositionError
from service_parser.domain.shared.patterns import ITEM_INDEX

# ====================== [ВАЛИДНЫЕ ЗНАЧЕНИЯ] ======================
_VALID_GROUP_NUMBERS = ['ЖБИ-21', 'ОС-21', 'ПЭС-215']
_VALID_GROUP_PARSER_POSITIONS = [(1, 1), (2, 10), (5, 3)]
_VALID_GROUP_PARSER_VALUES = [(group, x, y)
                              for group, (x, y) in zip(_VALID_GROUP_NUMBERS, _VALID_GROUP_PARSER_POSITIONS)]

# ====================== [НЕВАЛИДНЫЕ ЗНАЧЕНИЯ] ======================
_INVALID_GROUP_NUMBERS = ['ZHBI-21', 'ос 21', 'ПЭС 2']
_INVALID_GROUP_PARSER_POSITIONS = [(-1, 1), (2, -10), (-5, -3)]
_INVALID_GROUP_PARSER_VALUES = [(group, x, y)
                                for group, (x, y) in zip(_VALID_GROUP_NUMBERS, _INVALID_GROUP_PARSER_POSITIONS)]

# ====================== [СУЩНОСТИ] ======================
_GROUP_ITEMS = [Group(group) for group in _VALID_GROUP_NUMBERS]
_GROUP_PARSER_ITEMS = [GroupParser(group, x, y)
                       for group, (x, y) in zip(_VALID_GROUP_NUMBERS, _VALID_GROUP_PARSER_POSITIONS)]


# ====================== [ТЕСТЫ СУЩНОСТИ GROUP] ======================
@pytest.mark.parametrize('group_number', _VALID_GROUP_NUMBERS)
def test_create_group_entity(group_number: str):
    """Тест должен корректно создать сущность Group"""
    group = Group(group_number)

    assert group.number == group_number
    assert group.index == ITEM_INDEX.sub('', group_number.lower())


@pytest.mark.parametrize('invalid_group_number', _INVALID_GROUP_NUMBERS)
def test_create_group_entity_with_invalid_number(invalid_group_number: str):
    """Тест должен выдать ошибку GroupNumberFormatError"""
    with pytest.raises(GroupNumberFormatError) as exc_info:
        Group(invalid_group_number)

    assert exc_info.value.args[0] == f'Invalid group number: {invalid_group_number!r}'


@pytest.mark.parametrize('group_number', _VALID_GROUP_NUMBERS)
def test_group_entity_equal(group_number: str):
    """Тест должен проверить равенство двух равных сущностей Group"""
    first_group = Group(group_number)
    second_group = Group(group_number)

    assert first_group == second_group


@pytest.mark.parametrize('group_number', _VALID_GROUP_NUMBERS)
def test_group_entity_equal_hash(group_number: str):
    """Тест должен проверить равенство хэша двух равных сущностей Group"""
    first_group = Group(group_number)
    second_group = Group(group_number)

    assert hash(first_group) == hash(second_group)


@pytest.mark.parametrize('group_item', _GROUP_ITEMS)
def test_group_entity_string_representation(group_item: Group):
    """Тест должен вернуть номер группы при str(group_item)"""

    assert str(group_item) == group_item.number


# ====================== [ТЕСТЫ СУЩНОСТИ GROUPPARSER] ======================
@pytest.mark.parametrize('group_number, pos_x, pos_y', _VALID_GROUP_PARSER_VALUES)
def test_create_group_parser_entity(group_number: str, pos_x: int, pos_y: int):
    """Тест должен корректно создать сущность GroupParser"""
    group = GroupParser(group_number, pos_x, pos_y)

    assert group.group.number == group_number
    assert group.group.index == ITEM_INDEX.sub('', group_number.lower())
    assert group.pos_x == pos_x
    assert group.pos_y == pos_y


@pytest.mark.parametrize('group_number, pos_x, pos_y', _INVALID_GROUP_PARSER_VALUES)
def test_create_group_parser_entity_with_invalid_number(group_number: str, pos_x: int, pos_y: int):
    """Тест должен выдать ошибку NegativeGroupPositionError"""
    with pytest.raises(GroupParserPositionError) as exc_info:
        GroupParser(group_number, pos_x, pos_y)

    assert str(exc_info.value).endswith('position must be positive')


@pytest.mark.parametrize('group_number, pos_x, pos_y', _VALID_GROUP_PARSER_VALUES)
def test_group_parser_entity_equal(group_number: str, pos_x: int, pos_y: int):
    """Тест должен проверить равенство двух равных сущностей GroupParser"""
    first_group_parser = GroupParser(group_number, pos_x, pos_y)
    second_group_parser = GroupParser(group_number, pos_x, pos_y)

    assert first_group_parser == second_group_parser


@pytest.mark.parametrize('group_number, pos_x, pos_y', _VALID_GROUP_PARSER_VALUES)
def test_group_parser_entity_equal_hash(group_number: str, pos_x: int, pos_y: int):
    """Тест должен проверить равенство хэша двух равных сущностей GroupParser"""
    first_group_parser = GroupParser(group_number, pos_x, pos_y)
    second_group_parser = GroupParser(group_number, pos_x, pos_y)

    assert hash(first_group_parser) == hash(second_group_parser)


@pytest.mark.parametrize("group_parser_item", _GROUP_PARSER_ITEMS)
def test_group_parser_entity_string_representation(group_parser_item: GroupParser):
    """Тест должен вернуть номер группы при str(group_parser_item)"""

    assert str(group_parser_item) == group_parser_item.group.number
