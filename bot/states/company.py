from aiogram.fsm.state import StatesGroup, State

class CompanyState(StatesGroup):
    waiting_for_inn = State()
    waiting_for_company_name = State()
