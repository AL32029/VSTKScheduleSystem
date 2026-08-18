import datetime

from service_parser.domain.entities import Cabinet, DaySchedule, Group, Lesson

# ===================== [СУЩНОСТИ ДЛЯ ТЕСТОВ] =====================
_GROUP_NUMBER = "ЖБИ-21"
_GROUP_ITEM = Group(_GROUP_NUMBER)
_SCHEDULE_DATE = datetime.date(2099, 12, 31)
_SCHEDULE_DATES = [
    datetime.date(2099, 12, 1) + datetime.timedelta(days=i) for i in range(5)
]
_SCHEDULE_LESSON_TO_REPLACE_VALUES = [
    (datetime.time(9, 0), datetime.time(9, 45), "Биология", (Cabinet("12к"),)),
    (datetime.time(9, 55), datetime.time(10, 40), "Математика", (Cabinet("42к"),)),
    (datetime.time(10, 50), datetime.time(11, 35), " Рус. лит. ", (Cabinet("31"),)),
    (datetime.time(11, 45), datetime.time(12, 30), "Физкультура", (Cabinet("сз3"),)),
]
_SCHEDULE_LESSON_VALUES = [
    (datetime.time(9, 0), datetime.time(9, 45), "Математика", (Cabinet("42к"),)),
    (datetime.time(9, 55), datetime.time(10, 40), "Биология", (Cabinet("12к"),)),
    (datetime.time(10, 50), datetime.time(11, 35), " Физкультура ", (Cabinet("сз3"),)),
    (datetime.time(11, 45), datetime.time(12, 30), "Рус. лит.", (Cabinet("31"),)),
]
_SCHEDULE_LESSON_TO_REPLACE_ITEMS = [
    Lesson(start, end, name, cabinets)
    for start, end, name, cabinets in _SCHEDULE_LESSON_TO_REPLACE_VALUES
]
_SCHEDULE_LESSON_ITEMS = [
    Lesson(start, end, name, cabinets)
    for start, end, name, cabinets in _SCHEDULE_LESSON_VALUES
]
_DAY_SCHEDULE_TO_REPLACE = DaySchedule.from_existing(
    _GROUP_NUMBER, _SCHEDULE_LESSON_TO_REPLACE_ITEMS
)
_DAY_SCHEDULE = DaySchedule.from_existing(_GROUP_NUMBER, _SCHEDULE_LESSON_ITEMS)
