from aiogram.fsm.state import State, StatesGroup

class EmergencyState(StatesGroup):
    waiting_for_location = State()
    waiting_for_details = State()
