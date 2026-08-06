import datetime
import random

from service_bot.domain.entities import Group

# ====================== [ВАЛИДНЫЕ ЗНАЧЕНИЯ] ======================
_GROUP_NUMBERS = [('жби21', 'ЖБИ-21'), ('ос21', 'ОС-21'), ('пэс215', 'ПЭС-215')]
_CABINET_NUMBERS = [('упм1л6', 'упм. 1, л. 6'), ('52к', '52к'), ('31', '31')]
_LESSON_VALUES = [
    (datetime.time(9, 0), datetime.time(9, 45),
     'Биология', (random.choice(_CABINET_NUMBERS),)),
    (datetime.time(12, 40), datetime.time(13, 25),
     'Мех. оборудование', (random.choice(_CABINET_NUMBERS),)),
    (datetime.time(9, 55), datetime.time(10, 40),
     'Физкультура', (random.choice(_CABINET_NUMBERS),)),
    (datetime.time(10, 50), datetime.time(11, 35),
     'Математика', (random.choice(_CABINET_NUMBERS),)),
    (datetime.time(11, 45), datetime.time(12, 30),
     'Информатика', (random.choice(_CABINET_NUMBERS),)),
]
_CABINET_LESSON_VALUES = [(start, end, Group(_GROUP_NUMBERS[0][0], _GROUP_NUMBERS[0][1]), name, cabinets)
                          for (start, end, name, cabinets) in _LESSON_VALUES]
_SCHEDULE_DATE = datetime.date(2099, 12, 31)
