import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards import get_main_menu
from bot.services.yookassa_service import create_payment, get_payment_status

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data.startswith("view_cat:") & F.data.contains(":6:"))
async def operators_section(callback: types.CallbackQuery):
    """Специальная обработка для категории Операторы"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Стать верифицированным оператором", callback_data="op_registration")],
        [InlineKeyboardButton(text="🔍 Найти специалиста", callback_data="op_browse")],
        [InlineKeyboardButton(text="🔙 Назад к категориям", callback_data=f"view_city_{callback.data.split(':')[1]}")]
    ])

    await callback.message.edit_text(
        "💼 <b>Раздел «Операторы»</b>\n\n"
        "Здесь вы можете найти профессиональных пилотов дронов для ваших задач или разместить свое портфолио.\n\n"
        "<i>Размещение портфолио в этом разделе является платным (верификация специалиста).</i>",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data == "op_registration")
async def op_registration_payment(callback: types.CallbackQuery):
    """Предложение оплаты для регистрации оператора"""
    amount = 1000
    bot_info = await callback.bot.get_me()
    return_url = f"https://t.me/{bot_info.username}"

    try:
        payment = await create_payment(amount, "Верификация оператора (1 год)", return_url)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Оплатить 1 000 ₽", url=payment.confirmation.confirmation_url)],
            [InlineKeyboardButton(text="✅ Проверить статус", callback_data=f"check_pay_op_{payment.id}")]
        ])

        await callback.message.answer(
            "💎 <b>Верификация оператора</b>\n\n"
            "Стоимость размещения портфолио: 1 000 ₽ / год.\n"
            "После оплаты вам станет доступна форма заполнения данных специалиста.",
            parse_mode="HTML",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Op payment error: {e}")
        await callback.message.answer("❌ Ошибка платежной системы.")

    await callback.answer()

@router.callback_query(F.data.startswith("check_pay_op_"))
async def check_op_payment(callback: types.CallbackQuery, state: FSMContext):
    payment_id = callback.data.replace("check_pay_op_", "")
    status = await get_payment_status(payment_id)

    if status == "succeeded":
        await callback.message.answer("✅ Оплата подтверждена! Теперь опишите ваш опыт и оборудование для портфолио:")
        from bot.states.listing import ListingCreateStates
        await state.set_state(ListingCreateStates.waiting_for_description) # Реюз стейта
    else:
        await callback.answer("⏳ Оплата не найдена.", show_alert=True)

@router.callback_query(F.data == "op_browse")
async def op_browse(callback: types.CallbackQuery):
    """Просмотр списка операторов"""
    await callback.message.answer("🔍 <b>Список верифицированных операторов:</b>\n\nРаздел наполняется...", parse_mode="HTML")
    await callback.answer()
