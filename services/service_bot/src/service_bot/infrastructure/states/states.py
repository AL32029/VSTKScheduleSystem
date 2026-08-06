from aiogram.fsm.state import State, StatesGroup


class BotStates(StatesGroup):
    main_menu = State()
    add_schedule_item = State()
