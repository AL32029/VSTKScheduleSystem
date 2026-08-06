import pytest

from service_bot.domain.entities import CabinetLesson, Lesson
from tests.test_contains import _CABINET_LESSON_VALUES, _LESSON_VALUES


# ====================== [ТЕСТЫ СУЩНОСТИ LESSON] ======================
@pytest.mark.parametrize('start, end, name, cabinets', _LESSON_VALUES)
def test_lesson_entity_creation(start, end, name, cabinets):
    """Тест должен корректно создать сущность Lesson"""
    lesson = Lesson(start, end, name, cabinets)

    assert isinstance(lesson.cabinets, list)

# ====================== [ТЕСТЫ СУЩНОСТИ GROUPLESSON] ======================
@pytest.mark.parametrize('start, end, group, name, cabinets', _CABINET_LESSON_VALUES)
def test_cabinet_lesson_entity_creation(start, end, group, name, cabinets):
    """Тест должен корректно создать сущность CabinetLesson"""
    lesson = CabinetLesson(start, end, group, name, cabinets)

    assert isinstance(lesson.cabinets, list)
    assert isinstance(lesson, Lesson)