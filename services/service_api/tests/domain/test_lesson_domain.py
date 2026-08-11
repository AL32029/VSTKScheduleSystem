import pytest

from service_api.domain.entities import Cabinet, CabinetLesson, GroupLesson
from tests.test_contains import (
    _CABINET_LESSON_VALUES,
    _GROUP_LESSON_VALUES,
)


# ====================== [ТЕСТЫ СУЩНОСТИ GroupLesson] ======================
@pytest.mark.parametrize('start, end, name, cabinets', _GROUP_LESSON_VALUES)
def test_create_group_lesson_entity(start, end, name, cabinets):
    """Тест должен корректно создать сущность GroupLesson"""
    lesson = GroupLesson(start, end, name, cabinets)

    assert lesson.start == start
    assert lesson.end == end

    assert lesson.name == name

    assert lesson.cabinets
    assert len(list(lesson.cabinets)) == len(cabinets)
    assert all(isinstance(cabinet, Cabinet) for cabinet in lesson.cabinets)


@pytest.mark.parametrize('start, end, name, cabinets', _GROUP_LESSON_VALUES)
def test_group_lesson_entity_equal(start, end, name, cabinets):
    """Тест должен создать 2 идентичные сущности GroupLesson и провести их сравнение"""

    first_lesson = GroupLesson(start, end, name, cabinets)
    second_lesson = GroupLesson(start, end, name, cabinets)

    assert first_lesson == second_lesson


@pytest.mark.parametrize('start, end, name, cabinets', _GROUP_LESSON_VALUES)
def test_group_lesson_entity_equal_hash(start, end, name, cabinets):
    """Тест должен создать 2 идентичные сущности GroupLesson и провести сравнение хэшей"""

    first_lesson = GroupLesson(start, end, name, cabinets)
    second_lesson = GroupLesson(start, end, name, cabinets)

    assert hash(first_lesson) == hash(second_lesson)


# ====================== [ТЕСТЫ СУЩНОСТИ CabinetLesson] ======================
@pytest.mark.parametrize('start, end, group, name, cabinets', _CABINET_LESSON_VALUES)
def test_create_cabinet_lesson_entity(start, end, group, name, cabinets):
    """Тест должен корректно создать сущность CabinetLesson"""
    lesson = CabinetLesson(start, end, group, name, cabinets)

    assert lesson.start == start
    assert lesson.end == end

    assert lesson.group == group

    assert lesson.name == name

    assert lesson.cabinets
    assert len(list(lesson.cabinets)) == len(cabinets)
    assert all(isinstance(cabinet, Cabinet) for cabinet in lesson.cabinets)


@pytest.mark.parametrize('start, end, group, name, cabinets', _CABINET_LESSON_VALUES)
def test_cabinet_lesson_entity_equal(start, end, group, name, cabinets):
    """Тест должен создать 2 идентичные сущности CabinetLesson и провести их сравнение"""

    first_lesson = CabinetLesson(start, end, group, name, cabinets)
    second_lesson = CabinetLesson(start, end, group, name, cabinets)

    assert first_lesson == second_lesson


@pytest.mark.parametrize('start, end, group, name, cabinets', _CABINET_LESSON_VALUES)
def test_cabinet_lesson_entity_equal_hash(start, end, group, name, cabinets):
    """Тест должен создать 2 идентичные сущности CabinetLesson и провести сравнение хэшей"""

    first_lesson = CabinetLesson(start, end, group, name, cabinets)
    second_lesson = CabinetLesson(start, end, group, name, cabinets)

    assert hash(first_lesson) == hash(second_lesson)
