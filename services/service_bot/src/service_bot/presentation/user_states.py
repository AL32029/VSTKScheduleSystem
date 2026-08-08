from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    main_menu = State()
    add_schedule_item = State()
