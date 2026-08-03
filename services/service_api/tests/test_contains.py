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
_VALID_GROUP_NUMBERS = ['ЖБИ-21', 'ОС-21', 'ПЭС-215']
_VALID_CABINET_NUMBERS = ['11', '12к', '31', '315', '42к', '52к', 'сз3', 'упм. 1, л. 6']

# ====================== [НЕВАЛИДНЫЕ ЗНАЧЕНИЯ] ======================
_INVALID_GROUP_NUMBERS = ['ZHBI-21', 'ос 21', 'ПЭС 2']

# ====================== [БАЗОВЫЕ СУЩНОСТИ] ======================
_GROUP_ITEM = Group('ЖБИ-21')
_GROUP_ITEM_NOT_SAVED = Group('ЖБИ-11')
_CABINET_ITEM = Cabinet('упм. 1, л. 6')
_CABINET_ITEM_NOT_SAVED = Cabinet('22к')
_DAY_SCHEDULE_DATE = datetime.date(2099, 12, 31)

# ====================== [ИСХОДНЫЕ ДАННЫЕ ДЛЯ РАСПИСАНИЯ] ======================
_GROUP_LESSON_VALUES = [
    (datetime.time(9, 0), datetime.time(9, 45),
     'Математика', (Cabinet(random.choice(_VALID_CABINET_NUMBERS)),)),
    (datetime.time(9, 55), datetime.time(10, 40),
     'Биология', (Cabinet(random.choice(_VALID_CABINET_NUMBERS)),)),
    (datetime.time(10, 50), datetime.time(11, 35),
     'Физкультура', (Cabinet(random.choice(_VALID_CABINET_NUMBERS)),)),
    (datetime.time(11, 45), datetime.time(12, 40),
     'Рус. лит.', (Cabinet(random.choice(_VALID_CABINET_NUMBERS)),)),
    (datetime.time(12, 30), datetime.time(13, 25),
     'ОТСМ', (_CABINET_ITEM,)),
]

# ====================== [СПИСКИ ОБЪЕКТОВ] ======================
_GROUP_LESSON_ITEMS = [
    GroupLesson(start, end, name, cabinets)
    for (start, end, name, cabinets) in _GROUP_LESSON_VALUES
]

_GROUP_ITEMS = [
    Group(group) for group in _VALID_GROUP_NUMBERS
]

_CABINET_ITEMS = [
    Cabinet(cabinet) for cabinet in _VALID_CABINET_NUMBERS
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
_GROUP_DAY_SCHEDULE_ITEM = GroupDaySchedule(_GROUP_ITEM, _DAY_SCHEDULE_DATE, _GROUP_LESSON_ITEMS)
_CABINET_DAY_SCHEDULE_ITEM = CabinetDaySchedule(_CABINET_ITEM, _DAY_SCHEDULE_DATE, _CABINET_LESSON_ITEMS)

# ====================== [НЕВАЛИДНЫЕ ВАРИАНТЫ] ======================
_GROUP_LESSON_ITEMS_INVALID_END_TIME = [
    (end, start, name, cabinets)
    for (start, end, name, cabinets) in _GROUP_LESSON_VALUES
]

_CABINET_LESSON_VALUES_INVALID_END_TIME = [
    (end, start, group, name, cabinets)
    for (start, end, group, name, cabinets) in _CABINET_LESSON_VALUES
]
