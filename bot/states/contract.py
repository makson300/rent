from aiogram.fsm.state import State, StatesGroup

class ContractCreateStates(StatesGroup):
    waiting_for_lessor = State()
    waiting_for_lessee = State()
    waiting_for_item = State()
    waiting_for_price = State()
    waiting_for_deposit = State()
    waiting_for_dates = State()
