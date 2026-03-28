import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.states.listing import ListingCreateStates
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

router = Router()
logger = logging.getLogger(__name__)

from bot.constants import CITIES, CATEGORIES


from bot.constants import CITY_MAP, CATEGORY_MAP

def get_cities_kb():
    kb = [[KeyboardButton(text=city_name)] for city_name in CITY_MAP.values()]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_categories_kb():
    # Only show main rental categories here (0, 1, 2)
    kb = [[KeyboardButton(text=CATEGORY_MAP[i])] for i in range(3)]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


@router.callback_query(F.data == "start_listing_create")
async def start_listing_create(callback: types.CallbackQuery, state: FSMContext):
    """Начало создания объявления после заглушки оплаты"""
    from db.base import async_session
    from db.crud.user import get_user
    
    async with async_session() as session:
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.message.answer("⚠️ Вы не зарегистрированы! Используйте /start.")
            await callback.answer()
            return
            
        if user.user_type == "company" and user.ad_slots <= 0:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💎 Купить пакет", callback_data="buy_slots_from_create")],
                [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")]
            ])
            await callback.message.answer(
                "⚠️ <b>У вас закончились доступные слоты для объявлений.</b>\n\n"
                "Так как вы зарегистрировались как <b>Компания</b>, для размещения в аренду необходимо иметь оплаченный пакет.\n\n"
                "Пожалуйста, приобретите новый пакет для продолжения.",
                parse_mode="HTML",
                reply_markup=kb
            )
            await callback.answer()
            return

    await state.set_state(ListingCreateStates.waiting_for_city)
    # Assuming get_cities_keyboard is similar to get_cities_kb but might be in a different module
    # If get_cities_keyboard is not defined, you might need to adjust this line
    # For now, using the existing get_cities_kb()
    await callback.message.edit_text("📍 Выберите город:", reply_markup=get_cities_kb())
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
    
    data = await state.get_data()
    if data.get("listing_type") == "sale":
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🏢 Магазин (Новые устройства)")],
                [KeyboardButton(text="👤 Частное лицо (Б/У)")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer(
            "📝 <b>Уточните тип продавца:</b>\n\n"
            "Вы публикуете объявление от лица Магазина или как Частное лицо?",
            reply_markup=kb,
            parse_mode="HTML"
        )
        await state.set_state(ListingCreateStates.waiting_for_seller_type)
    else:
        await message.answer(
            "📝 <b>Шаг 3/9</b>\nВведите название вашего оборудования (до 100 символов):",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(ListingCreateStates.waiting_for_title)

@router.message(ListingCreateStates.waiting_for_seller_type)
async def process_seller_type(message: types.Message, state: FSMContext):
    if "Магазин" in message.text:
        await state.update_data(seller_type="store")
    else:
        await state.update_data(seller_type="individual")
        
    await message.answer(
        "📝 <b>Шаг 3/9</b>\nВведите название вашего оборудования (до 100 символов):",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ListingCreateStates.waiting_for_title)


@router.message(ListingCreateStates.waiting_for_title, F.text)
async def process_title(message: types.Message, state: FSMContext):
    if len(message.text) > 100:
        await message.answer("⚠️ Название слишком длинное. Максимум 100 символов.")
        return
    await state.update_data(title=message.text)
    await message.answer(
        "📝 <b>Шаг 4/9</b>\nВведите подробное описание оборудования:\n\n"
        "<i>Совет: Укажите комплектацию и особенности, чтобы привлечь больше клиентов.</i>",
        parse_mode="HTML"
    )
    await state.set_state(ListingCreateStates.waiting_for_description)


@router.message(ListingCreateStates.waiting_for_description, F.text)
async def process_description(message: types.Message, state: FSMContext):
    if len(message.text) > 2000:
        await message.answer("⚠️ Описание слишком длинное. Максимум 2000 символов.")
        return
    await state.update_data(description=message.text)
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
    await state.update_data(price_list=message.text)

    from db.base import async_session
    from db.crud.user import get_user
    async with async_session() as session:
        user = await get_user(session, message.from_user.id)

    contact_text = user.phone if user and user.phone else ""
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=contact_text)]] if contact_text else [],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        "📝 <b>Шаг 8/9</b>\nУкажите контактные данные для связи.\n\n"
        "<i>Вы можете использовать номер телефона из вашего профиля (кнопка ниже) или ввести другой контакт (например, ссылку на Telegram).</i>",
        reply_markup=kb,
        parse_mode="HTML"
    )
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
        
    # ИИ модерация первого (основного) фото
    wait_msg = await callback.message.answer("⏳ <i>MoMoA AI анализирует ваше фото на соответствие правилам...</i>", parse_mode="HTML")
    
    from bot.services.vision_moderator import analyze_photo_with_vision
    vision_result = await analyze_photo_with_vision(callback.bot, photos[0])
    
    await wait_msg.delete()
    
    if not vision_result.get("is_valid", True):
        # Если ИИ отклонил фото
        reason = vision_result.get("reason", "Несоответствующее изображение.")
        await callback.message.answer(
            f"❌ <b>ИИ-Модератор отклонил ваше фото!</b>\n\n"
            f"<b>Причина:</b> {reason}\n\n"
            "Пожалуйста, загрузите реальную фотографию вашего оборудования (БПЛА, техника, и т.д.).",
            parse_mode="HTML"
        )
        # Очищаем фотки, чтобы человек начал заливать их заново, но оставляем остальную сессию (город, цены и тд)
        await state.update_data(photos=[])
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Завершить загрузку", callback_data="finish_photos")]])
        await callback.message.answer("Отправьте фото заново (до 10 шт):", reply_markup=kb)
        return
        
    # Показываем предпросмотр
    preview_text = (
        "👀 <b>Предпросмотр вашего объявления:</b>\n\n"
        f"🏙 <b>Город:</b> {data['city']}\n"
        f"🏷 <b>Категория:</b> {data['category']}\n"
        f"📦 <b>Название:</b> {data['title']}\n"
        f"📝 <b>Описание:</b> {data['description']}\n"
        f"💰 <b>Цены:</b> {data['price_list']}\n"
        f"🛡 <b>Залог:</b> {data.get('deposit_terms', 'Не требуется')}\n"
        f"🚚 <b>Доставка:</b> {data['delivery_terms']}\n"
        f"📞 <b>Контакты:</b> {data['contacts']}\n\n"
        "<i>Проверьте данные. Если всё верно, нажмите «Опубликовать».</i>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опубликовать", callback_data="confirm_listing_publish")],
        [InlineKeyboardButton(text="❌ Начать заново", callback_data="start_listing_create")]
    ])

    if photos:
        await callback.message.answer_photo(photos[0], caption=preview_text[:1024], reply_markup=kb, parse_mode="HTML")
    else:
        await callback.message.answer(preview_text, reply_markup=kb, parse_mode="HTML")

    await callback.answer()

@router.callback_query(F.data == "confirm_listing_publish")
async def confirm_listing_publish(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    seller_type = data.get("seller_type", "individual")
    listing_type = data.get("listing_type", "rental")
    
    if listing_type == "sale":
        price_stars = 250 if seller_type == "store" else 50
        desc = "Размещение объявления о продаже (Магазин)" if seller_type == "store" else "Размещение объявления о продаже (Б/У)"
    elif listing_type == "rental":
        price_stars = 50
        desc = "Размещение объявления об аренде"
    else:
        price_stars = 50
        desc = "Размещение объявления"

    from aiogram.types import LabeledPrice
    prices = [LabeledPrice(label="Оплата", amount=price_stars)]
    
    await callback.message.delete()
    await callback.message.answer_invoice(
        title="Публикация объявления",
        description=f"{desc}.\nСтоимость: {price_stars} ⭐️",
        payload=f"publish_listing_{callback.from_user.id}",
        currency="XTR",
        prices=prices,
        provider_token="" # empty for Telegram Stars
    )
    await callback.answer()

@router.pre_checkout_query(lambda query: query.invoice_payload.startswith("publish_listing_"))
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment, lambda message: message.successful_payment.invoice_payload.startswith("publish_listing_"))
async def process_successful_payment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    seller_type = data.get("seller_type", "individual")
    from db.base import async_session
    from db.crud.listing import create_listing
    from db.crud.user import get_user
    from bot.keyboards.main_menu import get_main_menu
    
    async with async_session() as session:
        # Получаем реального ID пользователя из БД
        db_user = await get_user(session, message.from_user.id)
        user_db_id = db_user.id if db_user else 1 # Фоллбек на системного, если не зарегистрирован
        
        # Определяем тип объявления и категорию
        l_type = data.get("listing_type", "rental")
        # Map category name to DB id
        cat_name = data.get("category", "Дроны")
        cat_map = {"Дроны": 1, "Техника для съемки": 4, "Другое": 5, "Операторы": 6}
        cat_id = data.get("category_id") or cat_map.get(cat_name, 1)
        
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
        new_listing.seller_type = seller_type  # Устанавливаем seller_type
        await session.commit()
        
        # Referral Bonus Logic
        if db_user and getattr(db_user, 'referrer_id', None):
            ref_id = db_user.referrer_id
            from sqlalchemy import update
            from db.models.user import User
            from db.crud.user import get_user_by_db_id
            
            await session.execute(
                update(User).where(User.id == ref_id).values(referral_bonus=User.referral_bonus + 1)
            )
            db_user.referrer_id = None
            await session.commit()
            
            ref_user = await get_user_by_db_id(session, ref_id)
            if ref_user and ref_user.telegram_id:
                try:
                    await message.bot.send_message(
                        ref_user.telegram_id,
                        "🎁 <b>Бонус за друга!</b>\n\n"
                        "Пользователь, которого вы пригласили, оплатил свое первое объявление.\n"
                        "Вам начислен <b>+1 купон на бесплатное VIP-размещение</b> (поднятие в ТОП)!\n\n"
                        "<i>Перейдите в Профиль -> Мои объявления, чтобы использовать его.</i>",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify referrer {ref_id}: {e}")
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
        f"👤 От: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"🏙 Город: {data['city']}\n"
        f"🏷 Категория: {data['category']}\n"
        f"📦 Название: {data['title']}\n"
        f"📝 Описание: {data['description']}\n"
        f"💰 Цены: {data['price_list']}"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            if photos:
                await message.bot.send_photo(
                    admin_id, photos[0], caption=admin_text[:1024], reply_markup=admin_kb, parse_mode="HTML"
                )
            else:
                await message.bot.send_message(
                    admin_id, admin_text, reply_markup=admin_kb, parse_mode="HTML"
                )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

    await state.clear()
    await message.answer(
        "✅ <b>Ваше объявление успешно создано и отправлено на модерацию!</b>\n\n"
        "Мы сообщим вам, когда оно станет активно.",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )
