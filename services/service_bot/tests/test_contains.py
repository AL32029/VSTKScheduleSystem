import datetime
import random
from itertools import chain

from service_bot.domain.entities import (
    Cabinet,
    CabinetLesson,
    DaySchedule,
    Group,
    Lesson,
)

# ====================== [ВАЛИДНЫЕ ЗНАЧЕНИЯ] ======================
_GROUP_NUMBERS = [("жби21", "ЖБИ-21"), ("ос21", "ОС-21"), ("пэс215", "ПЭС-215")]
_CABINET_NUMBERS = [("упм1л6", "упм. 1, л. 6"), ("52к", "52к"), ("31", "31")]
_LESSON_VALUES = [
    (
        datetime.time(9, 0),
        datetime.time(9, 45),
        "Биология",
        (random.choice(_CABINET_NUMBERS),),
    ),
    (
        datetime.time(12, 40),
        datetime.time(13, 25),
        "Мех. оборудование",
        (random.choice(_CABINET_NUMBERS),),
    ),
    (
        datetime.time(9, 55),
        datetime.time(10, 40),
        "Физкультура",
        (random.choice(_CABINET_NUMBERS),),
    ),
    (
        datetime.time(10, 50),
        datetime.time(11, 35),
        "Математика",
        (random.choice(_CABINET_NUMBERS),),
    ),
    (
        datetime.time(11, 45),
        datetime.time(12, 30),
        "Информатика",
        (random.choice(_CABINET_NUMBERS),),
    ),
]
_CABINET_LESSON_VALUES = [
    (start, end, Group(_GROUP_NUMBERS[0][0], _GROUP_NUMBERS[0][1]), name, cabinets)
    for (start, end, name, cabinets) in _LESSON_VALUES
]
_SCHEDULE_DATE = datetime.date(2099, 12, 31)
_USER_ID = 319201832

# ====================== [ДОМЕННЫЕ СУЩНОСТИ] ======================
_GROUP_ITEMS = [Group(index, number) for index, number in _GROUP_NUMBERS]
_GROUP_ITEM = next(chain(_GROUP_ITEMS), None)
_CABINET_ITEMS = [Cabinet(index, number) for index, number in _CABINET_NUMBERS]
_CABINET_ITEM = next(chain(_CABINET_ITEMS), None)
_LESSON_ITEMS = [
    Lesson(start, end, name, (Cabinet(index, number) for index, number in cabinets))
    for start, end, name, cabinets in _LESSON_VALUES
]
_CABINET_LESSON_ITEMS = [
    CabinetLesson(
        start, end, name, (Cabinet(index, number) for index, number in cabinets), group
    )
    for start, end, group, name, cabinets in _CABINET_LESSON_VALUES
]
_GROUP_DAY_SCHEDULE = DaySchedule(_SCHEDULE_DATE, _GROUP_ITEMS[0], _LESSON_ITEMS)
_CABINET_DAY_SCHEDULE = DaySchedule(
    _SCHEDULE_DATE, _CABINET_ITEMS[0], _CABINET_LESSON_ITEMS
)
