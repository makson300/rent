from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.keyboards import get_main_menu
from bot.states.feedback import FeedbackStates

router = Router()


from bot.constants import CITY_MAP

@router.message(F.text == "🔍 Арендовать")
async def rental_menu(message: types.Message):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=city_name, callback_data=f"view_city_{city_id}")]
        for city_id, city_name in CITY_MAP.items()
    ])
    
    await message.answer(
        "🔍 <b>Раздел «Аренда»</b>\n\n"
        "Выберите город из списка ниже 🏙",
        parse_mode="HTML",
        reply_markup=kb,
    )


@router.message(F.text == "🏷 Сдать оборудование")
async def rent_out_menu(message: types.Message):
    """Вывод правил и пакетов размещения на основе типа пользователя"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from db.base import async_session
    from db.crud.user import get_user
    
    async with async_session() as session:
        user = await get_user(session, message.from_user.id)
    
    user_type = user.user_type if user else "private"
    
    if user_type == "company":
        text = (
            "🏢 <b>Размещение для компаний и прокатов</b>\n\n"
            "Для компаний доступно размещение только <b>пакетами от 5 объявлений</b>.\n\n"
            "<b>Тарифы на пакеты (5 объявлений):</b>\n"
            "🔹 1 месяц суммарно — 2 500 ₽\n"
            "🔹 6 месяцев суммарно — 7 000 ₽\n"
            "🔹 12 месяцев суммарно — 9 000 ₽\n\n"
            "<i>Выберите пакет для продолжения публикации.</i>"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 1 мес (2500 ₽)", callback_data="pay_tariff_company_1"),
             InlineKeyboardButton(text="⭐️ 1 мес (1250 ⭐️)", callback_data="pay_tariff_xtr_company_1")],
            [InlineKeyboardButton(text="💳 6 мес (7000 ₽)", callback_data="pay_tariff_company_6"),
             InlineKeyboardButton(text="⭐️ 6 мес (3500 ⭐️)", callback_data="pay_tariff_xtr_company_6")],
            [InlineKeyboardButton(text="💳 12 мес (9000 ₽)", callback_data="pay_tariff_company_12"),
             InlineKeyboardButton(text="⭐️ 12 мес (4500 ⭐️)", callback_data="pay_tariff_xtr_company_12")]
        ])
    else:
        text = (
            "👤 <b>Размещение для частных лиц</b>\n\n"
            "<b>Тарифы (1 объявление):</b>\n"
            "🔹 1 месяц — 700 ₽\n"
            "🔹 6 месяцев — 2 500 ₽\n"
            "🔹 12 месяцев — 3 500 ₽\n\n"
            "<b>Пакеты (5 объявлений):</b>\n"
            "🔹 1 месяц суммарно — 2 500 ₽\n"
            "🔹 6 месяцев суммарно — 7 000 ₽\n"
            "🔹 12 месяцев суммарно — 9 000 ₽\n\n"
            "<i>Вы можете выбрать разовое размещение или выгодный пакет.</i>"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 1 мес (700 ₽)", callback_data="pay_tariff_private_1"),
             InlineKeyboardButton(text="⭐️ 1 мес (350 ⭐️)", callback_data="pay_tariff_xtr_private_1")],
            [InlineKeyboardButton(text="💳 Пакет 1 мес (2500 ₽)", callback_data="pay_tariff_company_1"),
             InlineKeyboardButton(text="⭐️ Пакет 1 мес (1250 ⭐️)", callback_data="pay_tariff_xtr_company_1")]
        ])
        
    await message.answer(text, parse_mode="HTML", reply_markup=kb)

@router.callback_query(F.data.startswith("pay_tariff_"))
async def process_payment_init(callback: types.CallbackQuery):
    """Инициация оплаты через ЮKassa"""
    parts = callback.data.split("_")
    u_type = parts[2]
    duration = parts[3]

    prices = {
        "private": {"1": 700, "6": 2500, "12": 3500},
        "company": {"1": 2500, "6": 7000, "12": 9000}
    }

    amount = prices.get(u_type, {}).get(duration, 100)
    description = f"Оплата размещения ({u_type}, {duration} мес) в RentBot"

    from bot.payments import create_payment
    # В реальном боте return_url должен вести на бота или веб-хук
    payment = await create_payment(amount, description, "https://t.me/rent_equipment_bot")

    if payment and payment.confirmation and payment.confirmation.confirmation_url:
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🔗 Перейти к оплате", url=payment.confirmation.confirmation_url)],
            [types.InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"check_pay_rent_{payment.id}")]
        ])
        await callback.message.answer(
            f"💳 <b>Счет на оплату сформирован</b>\n\n"
            f"Сумма: {amount} ₽\n"
            f"Услуга: {description}\n\n"
            f"После оплаты нажмите кнопку «Я оплатил».",
            parse_mode="HTML",
            reply_markup=kb
        )
    else:
        await callback.answer("Ошибка при создании платежа. Попробуйте позже.", show_alert=True)
    await callback.answer()

@router.callback_query(F.data.startswith("check_pay_rent_"))
async def check_payment_handler(callback: types.CallbackQuery, state: FSMContext):
    payment_id = callback.data.split("_")[3]
    from bot.payments import check_payment_status
    status = await check_payment_status(payment_id)

    if status == "succeeded":
        await callback.message.answer(
            "✅ <b>Оплата прошла успешно!</b>\n\n"
            "Теперь вы можете приступить к созданию объявления.",
            parse_mode="HTML"
        )
        # Переходим к созданию
        from bot.handlers.listing_create import start_listing_create
        await start_listing_create(callback, state)
    else:
        await callback.answer(f"Платеж еще не подтвержден. Статус: {status}", show_alert=True)

@router.callback_query(F.data.startswith("pay_tariff_xtr_"))
async def process_payment_xtr_init(callback: types.CallbackQuery):
    """Инициация оплаты через Stars"""
    parts = callback.data.split("_")
    u_type = parts[3]
    duration = parts[4]

    prices_rub = {
        "private": {"1": 700, "6": 2500, "12": 3500},
        "company": {"1": 2500, "6": 7000, "12": 9000}
    }

    amount_rub = prices_rub.get(u_type, {}).get(duration, 100)
    amount_xtr = amount_rub // 2 # 1:2 конвертация

    description = f"Оплата размещения ({u_type}, {duration} мес) в RentBot"

    from aiogram.types import LabeledPrice
    await callback.message.answer_invoice(
        title="Оплата тарифа",
        description=description,
        payload=f"pay_tariff_xtr_{u_type}_{duration}_{callback.from_user.id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Тариф размещения", amount=amount_xtr)]
    )
    await callback.answer()

@router.pre_checkout_query(lambda query: query.invoice_payload.startswith("pay_tariff_xtr_"))
async def pre_checkout_tariff_xtr(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment, lambda message: message.successful_payment.invoice_payload.startswith("pay_tariff_xtr_"))
async def process_tariff_payment_xtr(message: types.Message, state: FSMContext):
    await message.answer(
        "✅ <b>Оплата Stars прошла успешно!</b>\n\n"
        "Теперь вы можете приступить к созданию объявления.",
        parse_mode="HTML"
    )
    from bot.handlers.listing_create import start_listing_create
    await start_listing_create(message, state)


@router.message(F.text == "📩 Обратная связь")
async def feedback_start(message: types.Message, state: FSMContext):
    """Начало сбора обратной связи"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💡 Предложение", callback_data="feedback_type_proposal")],
        [InlineKeyboardButton(text="🤝 Сотрудничество", callback_data="feedback_type_cooperation")],
        [InlineKeyboardButton(text="⚠️ Проблема", callback_data="feedback_type_problem")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_feedback")]
    ])
    
    await message.answer(
        "📩 <b>Обратная связь</b>\n\n"
        "Выберите тип вашего сообщения:",
        parse_mode="HTML",
        reply_markup=kb
    )
    await state.set_state(FeedbackStates.waiting_for_type)

@router.callback_query(F.data.startswith("feedback_type_"), FeedbackStates.waiting_for_type)
async def feedback_type_selected(callback: types.CallbackQuery, state: FSMContext):
    f_type = callback.data.split("_")[2]
    await state.update_data(feedback_type=f_type)
    
    type_names = {
        "proposal": "предложение",
        "cooperation": "сотрудничество",
        "problem": "проблему"
    }
    
    await callback.message.edit_text(
        f"📝 Опишите ваше <b>{type_names.get(f_type, 'сообщение')}</b>:\n\n"
        "<i>Вы можете отправить текст одним сообщением.</i>",
        parse_mode="HTML"
    )
    await state.set_state(FeedbackStates.waiting_for_message)
    await callback.answer()

@router.message(FeedbackStates.waiting_for_message, F.text)
async def process_feedback_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    f_type = data.get("feedback_type", "proposal")
    
    from db.base import async_session
    from db.models.feedback import Feedback
    from db.crud.user import get_user
    
    async with async_session() as session:
        db_user = await get_user(session, message.from_user.id)
        user_db_id = db_user.id if db_user else 1
        
        new_feedback = Feedback(
            user_id=user_db_id,
            type=f_type,
            message=message.text,
            status="pending"
        )
        session.add(new_feedback)
        await session.commit()
        feedback_id = new_feedback.id
    
    await state.clear()
    
    # AI Support Query
    from bot.services.support_agent import ask_support_agent
    ai_answer = await ask_support_agent(message.text)
    
    from bot.keyboards.main_menu import get_main_menu
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    if ai_answer:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Позвать человека", callback_data=f"escalate_{feedback_id}")]
        ])
        await message.answer(
            f"🤖 <b>Ответ ИИ-Саппорта:</b>\n\n{ai_answer}",
            parse_mode="HTML",
            reply_markup=kb
        )
        await message.answer("⬇️", reply_markup=get_main_menu())
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Передать администратору", callback_data=f"escalate_{feedback_id}")]
        ])
        await message.answer(
            "✅ <b>Спасибо за обратную связь!</b>\n"
            "Если вам требуется помощь человека, нажмите кнопку ниже.",
            parse_mode="HTML",
            reply_markup=kb
        )
        await message.answer("Перешли в меню.", reply_markup=get_main_menu())

@router.callback_query(F.data == "cancel_feedback")
async def cancel_feedback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Отправка обратной связи отменена.")
    await callback.answer()

@router.message(F.text == "🆘 ЧП")
async def emergency_menu(message: types.Message):
    """Меню гуманитарной миссии ЧП"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🙋‍♂️ Готов помочь (есть дрон)", callback_data="chp_ready_to_help")],
        [InlineKeyboardButton(text="🔍 Поиск оператора (экстренно)", callback_data="chp_need_operator")],
        [InlineKeyboardButton(text="📰 Мониторинг ЧП в РФ", callback_data="chp_monitoring")],
        [InlineKeyboardButton(text="🔝 В главное меню", callback_data="back_to_main")]
    ])

    await message.answer(
        "🆘 <b>ЧП / Гуманитарная миссия</b>\n\n"
        "Это бесплатный раздел для поиска и анализа чрезвычайных ситуаций в России.\n\n"
        "🔹 <b>Если у вас есть дрон</b> и вы готовы помочь — разместите анкету волонтёра.\n"
        "🔹 <b>Если вам экстренно нужен оператор</b> — оставьте заявку на поиск.\n"
        "🔹 Мы автоматически анализируем новости и оповещаем, если где-то требуется помощь.",
        parse_mode="HTML",
        reply_markup=kb,
    )

@router.callback_query(F.data == "chp_ready_to_help")
async def chp_volunteer_init(callback: types.CallbackQuery, state: FSMContext):
    """Размещение анкеты волонтера (БЕСПЛАТНО)"""
    from bot.handlers.listing_create import start_listing_create
    await state.update_data(listing_type="volunteer", category_id=7)
    await start_listing_create(callback, state)
    await callback.answer()

@router.callback_query(F.data == "chp_need_operator")
async def chp_request_init(callback: types.CallbackQuery, state: FSMContext):
    """Размещение заявки на поиск оператора (БЕСПЛАТНО)"""
    from bot.handlers.listing_create import start_listing_create
    await state.update_data(listing_type="chp_request", category_id=7)
    await start_listing_create(callback, state)
    await callback.answer()

@router.callback_query(F.data == "chp_monitoring")
async def chp_monitoring_view(callback: types.CallbackQuery):
    """Просмотр последних сводок мониторинга"""
    await callback.message.answer(
        "📰 <b>Оперативный мониторинг ЧП</b>\n\n"
        "<i>На данный момент система анализирует открытые источники (МЧС, новости, соцсети)...</i>\n\n"
        "⚠️ Актуальных запросов на помощь операторов БПЛА пока нет.\n\n"
        "Мы оповестим всех волонтёров, если поступит подтвержденная информация.",
        parse_mode="HTML"
    )
    await callback.answer()
