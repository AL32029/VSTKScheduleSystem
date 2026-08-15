import datetime
import random

from service_api.domain.entities import (
    Cabinet,
    CabinetDaySchedule,
    CabinetLesson,
    Group,
    GroupDaySchedule,
    GroupLesson,
)

# ====================== [ВАЛИДНЫЕ ЗНАЧЕНИЯ] ======================
_VALID_GROUP_NUMBERS = [("жби21", "ЖБИ-21"), ("ос21", "ОС-21"), ("пэс215", "ПЭС-215")]
_VALID_CABINET_NUMBERS = [
    ("11", "11"),
    ("12к", "12К"),
    ("31", "31"),
    ("315", "315"),
    ("42к", "42К"),
    ("52к", "52К"),
    ("сз3", "СЗ3"),
    ("упм1л6", "упм. 1, л. 6"),
]

# ====================== [НЕВАЛИДНЫЕ ЗНАЧЕНИЯ] ======================
_INVALID_GROUP_NUMBERS = ["ZHBI-21", "ос 21", "ПЭС 2"]

# ====================== [СУЩНОСТИ] ======================
_GROUP_ITEM = Group("жби21", "ЖБИ-21")
_GROUP_ITEM_NOT_SAVED = Group("жби11", "ЖБИ-11")
_CABINET_ITEM = Cabinet("упм1л6", "упм. 1, л. 6")
_CABINET_ITEM_NOT_SAVED = Cabinet("22к", "22к")
_DAY_SCHEDULE_DATE = datetime.date(2099, 12, 31)
_GROUP_ITEMS = [Group(index, number) for index, number in _VALID_GROUP_NUMBERS]
_CABINET_ITEMS = [Cabinet(index, number) for index, number in _VALID_CABINET_NUMBERS]

# ====================== [ИСХОДНЫЕ ДАННЫЕ ДЛЯ РАСПИСАНИЯ] ======================
_GROUP_LESSON_VALUES = [
    (
        datetime.time(9, 0),
        datetime.time(9, 45),
        "Математика",
        (random.choice(_CABINET_ITEMS),),
    ),
    (
        datetime.time(9, 55),
        datetime.time(10, 40),
        "Биология",
        (random.choice(_CABINET_ITEMS),),
    ),
    (
        datetime.time(10, 50),
        datetime.time(11, 35),
        "Физкультура",
        (random.choice(_CABINET_ITEMS),),
    ),
    (
        datetime.time(11, 45),
        datetime.time(12, 40),
        "Рус. лит.",
        (random.choice(_CABINET_ITEMS),),
    ),
    (datetime.time(12, 30), datetime.time(13, 25), "ОТСМ", (_CABINET_ITEM,)),
]

# ====================== [СПИСКИ ОБЪЕКТОВ] ======================
_GROUP_LESSON_ITEMS = [
    GroupLesson(start, end, name, cabinets)
    for (start, end, name, cabinets) in _GROUP_LESSON_VALUES
]

_CABINET_LESSON_VALUES = [
    (start, end, _GROUP_ITEM, name, cabinets)
    for (start, end, name, cabinets) in _GROUP_LESSON_VALUES
    if _CABINET_ITEM in cabinets
]

_CABINET_LESSON_ITEMS = [
    CabinetLesson(start, end, group, name, cabinets)
    for (start, end, group, name, cabinets) in _CABINET_LESSON_VALUES
]

# ====================== [РАСПИСАНИЕ НА ДЕНЬ] ======================
_GROUP_DAY_SCHEDULE_ITEM = GroupDaySchedule(
    _GROUP_ITEM, _DAY_SCHEDULE_DATE, _GROUP_LESSON_ITEMS
)
_CABINET_DAY_SCHEDULE_ITEM = CabinetDaySchedule(
    _CABINET_ITEM, _DAY_SCHEDULE_DATE, _CABINET_LESSON_ITEMS
)

# ====================== [НЕВАЛИДНЫЕ ВАРИАНТЫ] ======================
_GROUP_LESSON_ITEMS_INVALID_END_TIME = [
    (end, start, name, cabinets)
    for (start, end, name, cabinets) in _GROUP_LESSON_VALUES
]

_CABINET_LESSON_VALUES_INVALID_END_TIME = [
    (end, start, group, name, cabinets)
    for (start, end, group, name, cabinets) in _CABINET_LESSON_VALUES
]
