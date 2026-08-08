from .base_exceptions import DataSavingError


class GroupAlreadyInsertedError(DataSavingError):
    """Ошибка сохранения уже добавленной группы"""

    def __init__(self, group_number: str):
        self.group_number = group_number
        super().__init__(f"У вас уже добавлена группа {group_number}")


class CabinetAlreadyInsertedError(DataSavingError):
    """Ошибка сохранения уже добавленного кабинета"""

    def __init__(self, cabinet_number: str):
        self.cabinet_number = cabinet_number
        super().__init__(f"У вас уже добавлен кабинет {cabinet_number}")
