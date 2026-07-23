import pytest

from service_parser.domain.entities import Cabinet


@pytest.mark.parametrize("source,index", [
    ['упм. 1, л. 6', 'упм1л6'],
    ['315', '315'],
    ['СЗ3', 'сз3'],
    ['эксКурсия', 'экскурсия'],
    ['к. 2, тир', 'к2тир'],
])
def test_cabinet_creation_and_index_normalization(source, index):
    cabinet = Cabinet(source)

    assert cabinet.number == source

    assert str(cabinet) == source

    assert cabinet.index == index


@pytest.mark.parametrize("first_cabinet,second_cabinet", [
    ['упм. 1, л. 6', 'УПМ 1 л 6'],
    ['ТиР   корп 2', 'ТИР, КОРП.  2'],
    ['ЭКСКУРСИЯ', 'ЭкСкУрСиЯ'],
])
def test_cabinet_equalizing(first_cabinet, second_cabinet):
    first_cabinet_model = Cabinet(first_cabinet)
    second_cabinet_model = Cabinet(second_cabinet)

    assert first_cabinet_model == second_cabinet_model


@pytest.mark.parametrize("first_cabinet,second_cabinet", [
    ['упм. 1, л. 6', 'УПМ 1 л 6'],
    ['ТиР   корп 2', 'ТИР, КОРП.  2'],
    ['ЭКСКУРСИЯ', 'ЭкСкУрСиЯ'],
])
def test_cabinet_equalizing_not_implemented_error(first_cabinet, second_cabinet):
    first_cabinet_model = Cabinet(first_cabinet)

    with pytest.raises(NotImplementedError):
        assert first_cabinet_model == second_cabinet


@pytest.mark.parametrize("first_cabinet,second_cabinet", [
    ['ЖБИ-21', 'ЖбИ-21'],
    ['ОС-21', 'ос-21'],
    ['ПэС-215', 'Пэс-215'],
])
def test_cabinet_hash_equalizing(first_cabinet, second_cabinet):
    first_cabinet_model = Cabinet(first_cabinet)
    second_cabinet_model = Cabinet(second_cabinet)

    assert hash(first_cabinet_model) == hash(second_cabinet_model)

    assert hash(first_cabinet_model) == hash(first_cabinet_model)

    assert len({first_cabinet_model, second_cabinet_model}) == 1
