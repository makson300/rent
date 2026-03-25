import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.states.listing import ListingCreateStates
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

router = Router()
logger = logging.getLogger(__name__)

from bot.constants import CITY_MAP, CATEGORY_MAP

def get_cities_kb():
    kb = [[KeyboardButton(text=city)] for city in CITY_MAP.values()]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_categories_kb():
    # Only show rental categories (id < 6)
    kb = [[KeyboardButton(text=name)] for cid, name in CATEGORY_MAP.items() if int(cid) < 6]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


@router.callback_query(F.data == "start_listing_create")
async def start_listing_create_payment_choice(callback: types.CallbackQuery, state: FSMContext):
    """Выбор тарифа перед созданием объявления"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from db.base import async_session
    from db.crud.user import get_user
    
    async with async_session() as session:
        user = await get_user(session, callback.from_user.id)
        
    if not user or not user.phone:
        await callback.message.answer("⚠️ Сначала необходимо зарегистрироваться! Используйте /start.")
        await callback.answer()
        return

    user_type = user.user_type

    if user_type == "company":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔹 1 месяц (5 объявлений) — 2 500 ₽", callback_data="pay_rent_2500")],
            [InlineKeyboardButton(text="🔹 6 месяцев (5 объявлений) — 7 000 ₽", callback_data="pay_rent_7000")],
            [InlineKeyboardButton(text="🔹 12 месяцев (5 объявлений) — 9 000 ₽", callback_data="pay_rent_9000")],
        ])
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔸 1 мес (1 объявление) — 700 ₽", callback_data="pay_rent_700")],
            [InlineKeyboardButton(text="🔸 6 мес (1 объявление) — 2 500 ₽", callback_data="pay_rent_2500_single")],
            [InlineKeyboardButton(text="🔸 12 мес (1 объявление) — 3 500 ₽", callback_data="pay_rent_3500_single")],
            [InlineKeyboardButton(text="🔹 Пакет 5 объявлений (от 2 500 ₽)", callback_data="show_packages")],
        ])

    await callback.message.edit_text(
        "💳 <b>Выберите тарифный план для размещения:</b>",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data.startswith("pay_rent_"))
async def process_rent_payment(callback: types.CallbackQuery, state: FSMContext):
    """Создание платежа через ЮKassa"""
    from bot.services.yookassa_service import create_payment
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    amount = int(callback.data.split("_")[2])
    # Уникальная ссылка возврата (можно использовать bot username)
    bot_info = await callback.bot.get_me()
    return_url = f"https://t.me/{bot_info.username}"

    try:
        payment = await create_payment(amount, f"Оплата размещения объявления ({amount} RUB)", return_url)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Перейти к оплате", url=payment.confirmation.confirmation_url)],
            [InlineKeyboardButton(text="✅ Проверить оплату", callback_data=f"check_pay_rent_{payment.id}")]
        ])

        await callback.message.answer(
            f"💰 <b>Счет сформирован!</b>\nСумма: {amount} ₽\n\n"
            "После оплаты нажмите кнопку «Проверить оплату».",
            parse_mode="HTML",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Yookassa error: {e}")
        await callback.message.answer("❌ Ошибка при формировании счета. Попробуйте позже.")

    await callback.answer()

@router.callback_query(F.data.startswith("check_pay_rent_"))
async def check_rent_payment(callback: types.CallbackQuery, state: FSMContext):
    """Проверка статуса платежа"""
    from bot.services.yookassa_service import get_payment_status
    payment_id = callback.data.replace("check_pay_rent_", "")

    status = await get_payment_status(payment_id)

    if status == "succeeded":
        await callback.message.answer("✅ Оплата прошла успешно! Приступаем к созданию объявления.")
        await start_listing_create(callback, state)
    else:
        await callback.answer("⏳ Оплата еще не получена или в процессе (статус: " + status + ")", show_alert=True)

async def start_listing_create(callback: types.CallbackQuery, state: FSMContext):
    """Начало создания объявления (Шаг 1)"""
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
    from aiogram.utils.markdown import html_decoration as hd
    await state.update_data(title=hd.quote(message.text))
    await message.answer("📝 <b>Шаг 4/9</b>\nВведите подробное описание:")
    await state.set_state(ListingCreateStates.waiting_for_description)


@router.message(ListingCreateStates.waiting_for_description, F.text)
async def process_description(message: types.Message, state: FSMContext):
    from aiogram.utils.markdown import html_decoration as hd
    await state.update_data(description=hd.quote(message.text))
    await message.answer("📝 <b>Шаг 5/9</b>\nУкажите условия залога (требуется ли паспорт, депозит и т.д.):")
    await state.set_state(ListingCreateStates.waiting_for_deposit)


@router.message(ListingCreateStates.waiting_for_deposit, F.text)
async def process_deposit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # If it's a sale, we might want to skip or label it differently, 
    # but for now we'll just allow setting it or skip if empty.
    await state.update_data(deposit_terms=message.text)
    await message.answer("📝 <b>Шаг 6/9</b>\nУкажите условия доставки/самовывоза:")
    await state.set_state(ListingCreateStates.waiting_for_delivery)


@router.message(ListingCreateStates.waiting_for_delivery, F.text)
async def process_delivery(message: types.Message, state: FSMContext):
    await state.update_data(delivery_terms=message.text)
    await message.answer("📝 <b>Шаг 7/9</b>\nУкажите цены (например, 1 день - 500р, 3 дня - 1200р):")
    await state.set_state(ListingCreateStates.waiting_for_price)


@router.message(ListingCreateStates.waiting_for_price, F.text)
async def process_price(message: types.Message, state: FSMContext):
    # Basic numeric/length check for security/UX
    if len(message.text) > 500:
        await message.answer("⚠️ Текст слишком длинный. Пожалуйста, сократите описание цен.")
        return
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
    from db.crud.user import get_user
    from bot.keyboards.main_menu import get_main_menu
    
    async with async_session() as session:
        # Получаем реального ID пользователя из БД
        db_user = await get_user(session, callback.from_user.id)
        user_db_id = db_user.id if db_user else 1 # Фоллбек на системного, если не зарегистрирован
        
        # Определяем тип объявления и категорию
        l_type = data.get("listing_type", "rental")
        cat_id = data.get("category_id", 1) # По умолчанию 1 (Аренда)
        
        # Получаем созданное объявление (с ID)
        new_listing = await create_listing(
            session=session,
            user_id=user_db_id,
            category_id=cat_id,
            city=data["city"],
            title=data["title"],
            description=data["description"],
            deposit_terms=data.get("deposit_terms", "Не требуется"),
            delivery_terms=data["delivery_terms"],
            price_list=data["price_list"],
            contacts=data["contacts"],
            photo_ids=photos,
            listing_type=l_type,
            status="moderation"
        )
        
    # Уведомляем админов
    from bot.handlers.admin import ADMIN_IDS
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"mod_approve_{new_listing.id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"mod_reject_{new_listing.id}")
        ]
    ])
    
    admin_text = (
        f"🆕 <b>Новое объявление на модерации!</b>\n\n"
        f"👤 От: {callback.from_user.full_name} (@{callback.from_user.username})\n"
        f"🏙 Город: {data['city']}\n"
        f"🏷 Категория: {data['category']}\n"
        f"📦 Название: {data['title']}\n"
        f"📝 Описание: {data['description']}\n"
        f"💰 Цены: {data['price_list']}"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            if photos:
                await callback.bot.send_photo(
                    admin_id, photos[0], caption=admin_text[:1024], reply_markup=admin_kb, parse_mode="HTML"
                )
            else:
                await callback.bot.send_message(
                    admin_id, admin_text, reply_markup=admin_kb, parse_mode="HTML"
                )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

    await state.clear()
    await callback.message.answer(
        "✅ <b>Ваше объявление успешно создано и отправлено на модерацию!</b>\n\n"
        "Мы сообщим вам, когда оно станет активно.",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )
    await callback.answer()
