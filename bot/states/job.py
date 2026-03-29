from aiogram.fsm.state import State, StatesGroup

class JobCreationState(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_category = State()
    waiting_for_city = State()
    waiting_for_budget = State()
