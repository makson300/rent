from aiogram.fsm.state import State, StatesGroup

class ListingCreateStates(StatesGroup):
    """Пошаговая форма создания объявления"""
    waiting_for_city = State()
    waiting_for_category = State()
    waiting_for_seller_type = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_deposit = State()
    waiting_for_delivery = State()
    waiting_for_price = State()
    waiting_for_contacts = State()
    waiting_for_photos = State()
