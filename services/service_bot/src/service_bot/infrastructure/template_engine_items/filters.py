import datetime

_MONTHS_GENITIVE = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}


def format_ru_date(value: datetime.datetime, fmt: str = "%d %B %Y года") -> str:
    """Фильтр преобразования даты в читаемый формат"""
    if value is None:
        return ""

    month_name = _MONTHS_GENITIVE[value.month]

    date_str = value.strftime(fmt.replace("%B", "###MONTH###"))

    return date_str.replace("###MONTH###", month_name).lower()
