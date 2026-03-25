from aiogram.fsm.state import StatesGroup, State

class ListingCreateStates(StatesGroup):
    waiting_for_city = State()
    waiting_for_category = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_deposit = State()
    waiting_for_delivery = State()
    waiting_for_price = State()
    waiting_for_contacts = State()
    waiting_for_photos = State()

class EducationApplyStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_phone = State()
