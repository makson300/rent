import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.states.listing import ListingCreateStates
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

router = Router()
logger = logging.getLogger(__name__)

# Заглушка городов и категорий
CITIES = ["Москва", "Санкт-Петербург", "Казань", "Екатеринбург", "Новосибирск"]
CATEGORIES = ["Камеры и оптика", "Квадрокоптеры", "Кемпинг", "Спорт", "Инструменты"]


def get_cities_kb():
    kb = [[KeyboardButton(text=city)] for city in CITIES]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_categories_kb():
    kb = [[KeyboardButton(text=cat)] for cat in CATEGORIES]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


@router.callback_query(F.data == "start_listing_create")
async def start_listing_create(callback: types.CallbackQuery, state: FSMContext):
    """Начало создания объявления после заглушки оплаты"""
    await callback.message.answer(
        "📝 <b>Создание объявления (Шаг 1/9)</b>\n\n"
        "Выберите город из списка:",
        parse_mode="HTML",
        reply_markup=get_cities_kb()
    )
    await state.set_state(ListingCreateStates.waiting_for_city)
    await callback.answer()


@router.message(ListingCreateStates.waiting_for_city)
async def process_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer(
        "📝 <b>Шаг 2/9</b>\nВыберите категорию оборудования:",
        reply_markup=get_categories_kb()
    )
    await state.set_state(ListingCreateStates.waiting_for_category)


@router.message(ListingCreateStates.waiting_for_category)
async def process_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer(
        "📝 <b>Шаг 3/9</b>\nВведите название вашего оборудования (до 100 символов):",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ListingCreateStates.waiting_for_title)


@router.message(ListingCreateStates.waiting_for_title, F.text)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("📝 <b>Шаг 4/9</b>\nВведите подробное описание:")
    await state.set_state(ListingCreateStates.waiting_for_description)


@router.message(ListingCreateStates.waiting_for_description, F.text)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("📝 <b>Шаг 5/9</b>\nУкажите условия залога (требуется ли паспорт, депозит и т.д.):")
    await state.set_state(ListingCreateStates.waiting_for_deposit)


@router.message(ListingCreateStates.waiting_for_deposit, F.text)
async def process_deposit(message: types.Message, state: FSMContext):
    await state.update_data(deposit_terms=message.text)
    await message.answer("📝 <b>Шаг 6/9</b>\nУстаните условия доставки/самовывоза:")
    await state.set_state(ListingCreateStates.waiting_for_delivery)


@router.message(ListingCreateStates.waiting_for_delivery, F.text)
async def process_delivery(message: types.Message, state: FSMContext):
    await state.update_data(delivery_terms=message.text)
    await message.answer("📝 <b>Шаг 7/9</b>\nУкажите цены (например, 1 день - 500р, 3 дня - 1200р):")
    await state.set_state(ListingCreateStates.waiting_for_price)


@router.message(ListingCreateStates.waiting_for_price, F.text)
async def process_price(message: types.Message, state: FSMContext):
    await state.update_data(price_list=message.text)
    await message.answer("📝 <b>Шаг 8/9</b>\nУкажите контактные данные (номер телефона, ссылки):")
    await state.set_state(ListingCreateStates.waiting_for_contacts)


@router.message(ListingCreateStates.waiting_for_contacts, F.text)
async def process_contacts(message: types.Message, state: FSMContext):
    await state.update_data(contacts=message.text)
    await state.update_data(photos=[])
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Завершить загрузку", callback_data="finish_photos")]])
    
    await message.answer(
        "📝 <b>Шаг 9/9</b>\nОтправьте от 1 до 10 фотографий.\n\n"
        "<i>Отправляйте фото по одному. Когда закончите, нажмите кнопку ниже.</i>",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await state.set_state(ListingCreateStates.waiting_for_photos)


@router.message(ListingCreateStates.waiting_for_photos, F.photo)
async def process_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if len(photos) >= 10:
        await message.answer("⚠️ Вы уже загрузили максимальное количество фото (10). Нажмите 'Завершить загрузку'.")
        return
        
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Завершить загрузку", callback_data="finish_photos")]])
    
    await message.answer(f"📸 Фото добавлено ({len(photos)}/10). Можете отправить еще, либо завершить.", reply_markup=kb)


@router.callback_query(F.data == "finish_photos", ListingCreateStates.waiting_for_photos)
async def finish_photos(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    if not photos:
        await callback.answer("Нужно отправить хотя бы одно фото!", show_alert=True)
        return
        
    # Сохраняем в БД
    from db.base import async_session
    from db.crud.listing import create_listing
    from bot.keyboards.main_menu import get_main_menu
    
    # Для MVP используем id = 1 вместо реального (заглушка категории) пока не сделаем crud-поиск категории
    # То же самое с юзером, но у нас есть user id из телеграма.
    async with async_session() as session:
        # TODO: Заменить на реальные IDs когда создадим их в БД
        await create_listing(
            session=session,
            user_id=1,  # Заглушка, нужно брать реального юзера
            category_id=1, # Заглушка
            city=data["city"],
            title=data["title"],
            description=data["description"],
            deposit_terms=data["deposit_terms"],
            delivery_terms=data["delivery_terms"],
            price_list=data["price_list"],
            contacts=data["contacts"],
            photo_ids=photos
        )
        
    await state.clear()
    await callback.message.answer(
        "✅ <b>Ваше объявление успешно создано и отправлено на модерацию!</b>\n\n"
        "Мы сообщим вам, когда оно станет активно.",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )
    await callback.answer()
