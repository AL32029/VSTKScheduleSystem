import re

ITEM_INDEX = re.compile(r'[^а-я0-9]', flags=re.IGNORECASE)

GROUP_NUMBER = re.compile(r'([А-Я]{1,3}-[0-9]{2,3})')

CABINET_NUMBER = re.compile(r'([А-Я]{1,3}-[0-9]{2,3})')