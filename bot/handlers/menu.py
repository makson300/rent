from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.keyboards import get_main_menu
from bot.states.feedback import FeedbackStates

router = Router()


@router.message(F.text == "🔍 Арендовать")
async def rental_menu(message: types.Message):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from bot.handlers.listing_create import CITIES
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=city, callback_data=f"view_city_{city}")] for city in CITIES
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
        [InlineKeyboardButton(text="💳 Выбрать тариф и оплатить", callback_data="start_listing_create")]
    ])
    await message.answer(text, parse_mode="HTML", reply_markup=kb)


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
            status="new"
        )
        session.add(new_feedback)
        await session.commit()
    
    await state.clear()
    await message.answer(
        "✅ <b>Спасибо за обратную связь!</b>\n"
        "Ваше сообщение отправлено администрации и будет рассмотрено в ближайшее время.",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data == "cancel_feedback")
async def cancel_feedback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Отправка обратной связи отменена.")
    await callback.answer()

@router.message(F.text.in_({"🆘 ЧП", "🎧 Поддержка"}))
async def stub_menu(message: types.Message):
    """Заглушки для старых или тестовых кнопок"""
    await message.answer(
        f"🚧 Раздел <b>«{message.text.strip('🎓🆘📜🎧 ')}»</b> находится в разработке.",
        parse_mode="HTML",
        reply_markup=get_main_menu(),
    )
