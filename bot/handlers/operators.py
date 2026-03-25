import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from db.base import async_session
from db.models.listing import Listing
from sqlalchemy import select
from sqlalchemy.orm import selectinload
router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "🎬 Операторы")
async def operators_menu(message: types.Message):
    """Меню раздела операторов"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Посмотреть операторов", callback_data="view_operators_0")],
        [InlineKeyboardButton(text="➕ Разместить анкету (1000 ₽/год)", callback_data="pay_operator_listing")]
    ])

    await message.answer(
        "🎬 <b>База операторов и специалистов</b>\n\n"
        "Здесь вы можете найти профессионалов для вашего проекта или разместить свою анкету.\n\n"
        "🔹 <i>Размещение анкеты стоит 1000 ₽ на 1 год.</i>",
        parse_mode="HTML",
        reply_markup=kb
    )

@router.callback_query(F.data.startswith("view_operators_"))
async def show_operators(callback: types.CallbackQuery):
    """Показ анкет операторов с пагинацией"""
    page = int(callback.data.split("_")[2])
    page_size = 1

    async with async_session() as session:
        # Для операторов используем отдельную категорию (например, id=4 или фильтр по типу)
        # Пока будем искать все активные листинги с типом 'operator'
        result = await session.execute(
            select(Listing)
            .options(selectinload(Listing.photos))
            .where(Listing.listing_type == "operator")
            .where(Listing.status == "active")
        )
        operators = result.scalars().all()

    if not operators:
        await callback.message.answer("😔 База операторов пока пуста. Будьте первым!")
        await callback.answer()
        return

    total = len(operators)
    start_idx = page * page_size
    operator = operators[start_idx]

    text = (
        f"🎬 <b>Оператор</b> ({page+1}/{total})\n\n"
        f"👤 <b>{operator.title}</b>\n\n"
        f"📝 <b>Услуги:</b>\n{operator.description}\n\n"
        f"🔗 <b>Портфолио:</b> {operator.contacts}\n"
    )

    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Пред.", callback_data=f"view_operators_{page-1}"))
    if (page + 1) * page_size < total:
        nav_buttons.append(InlineKeyboardButton(text="След. ➡️", callback_data=f"view_operators_{page+1}"))

    kb = InlineKeyboardMarkup(inline_keyboard=[
        nav_buttons,
        [InlineKeyboardButton(text="🔝 В главное меню", callback_data="back_to_main")]
    ])

    if operator.photos:
        photo_id = operator.photos[0].photo_id
        try:
            await callback.message.edit_media(
                media=InputMediaPhoto(media=photo_id, caption=text[:1024], parse_mode="HTML"),
                reply_markup=kb
            )
        except Exception:
            await callback.message.delete()
            await callback.message.answer_photo(photo_id, caption=text[:1024], parse_mode="HTML", reply_markup=kb)
    else:
        try:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            await callback.message.delete()
            await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)

    await callback.answer()

@router.callback_query(F.data == "pay_operator_listing")
async def pay_operator_init(callback: types.CallbackQuery):
    """Инициация оплаты для размещения анкеты оператора"""
    amount = 1000
    description = "Размещение анкеты оператора (1 год) в RentBot"

    from bot.payments import create_payment
    payment = await create_payment(amount, description, "https://t.me/rent_equipment_bot")

    if payment and payment.confirmation and payment.confirmation.confirmation_url:
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Перейти к оплате", url=payment.confirmation.confirmation_url)],
            [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"check_pay_op_{payment.id}")]
        ])
        await callback.message.answer(
            f"💳 <b>Оплата размещения анкеты</b>\n\n"
            f"Сумма: 1000 ₽\n"
            f"Срок: 1 год\n\n"
            f"После оплаты вы сможете заполнить анкету.",
            parse_mode="HTML",
            reply_markup=kb
        )
    else:
        await callback.answer("Ошибка при создании платежа. Попробуйте позже.", show_alert=True)
    await callback.answer()

@router.callback_query(F.data.startswith("check_pay_op_"))
async def check_operator_payment(callback: types.CallbackQuery, state: FSMContext):
    """Проверка оплаты анкеты оператора"""
    payment_id = callback.data.split("_")[3]
    from bot.payments import check_payment_status
    status = await check_payment_status(payment_id)

    if status == "succeeded":
        await callback.message.answer(
            "✅ <b>Оплата прошла успешно!</b>\n\n"
            "Приступим к заполнению вашей анкеты.",
            parse_mode="HTML"
        )
        # Настраиваем состояние для создания анкеты
        from bot.handlers.listing_create import start_listing_create
        # Category name in DB is 'Операторы' (mapped in constants.py and base.py)
        await state.update_data(listing_type="operator", category_id=6) # 6 - Операторы (см. db/base.py)
        await start_listing_create(callback, state)
    else:
        await callback.answer(f"Платеж еще не подтвержден. Статус: {status}", show_alert=True)
