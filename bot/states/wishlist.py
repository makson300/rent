from aiogram.fsm.state import State, StatesGroup

class WishlistStates(StatesGroup):
    waiting_for_query = State()
