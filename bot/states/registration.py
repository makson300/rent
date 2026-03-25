from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """Состояния для процесса регистрации"""
    waiting_for_contact = State()
    waiting_for_user_type = State()
