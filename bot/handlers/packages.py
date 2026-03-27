import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from db.base import async_session
from db.crud.user import get_user
from bot.utils.payment import create_payment, check_payment_status
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import update

router = Router()
logger = logging.getLogger(__name__)

PACKAGES = {
    "pack_5": {"slots": 5, "price": 500, "name": "Пакет 5 объявлений"},
    "pack_10": {"slots": 10, "price": 900, "name": "Пакет 10 объявлений"},
    "pack_20": {"slots": 20, "price": 1600, "name": "Пакет 20 объявлений"},
}

@router.message(F.text == "💎 Купить пакет")
async def show_packages(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 5 объявлений - 500₽", callback_data="buy_pack_5")],
        [InlineKeyboardButton(text="📦 10 объявлений - 900₽", callback_data="buy_pack_10")],
        [InlineKeyboardButton(text="📦 20 объявлений - 1600₽", callback_data="buy_pack_20")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile")]
    ])
    await message.answer(
        "💎 <b>Пакеты объявлений для Компаний</b>\n\n"
        "Выберите подходящий пакет для размещения ваших предложений в каталоге аренды.",
        parse_mode="HTML",
        reply_markup=kb
    )

@router.callback_query(F.data.startswith("buy_pack_"))
async def process_buy_pack(callback: types.CallbackQuery):
    pack_id = callback.data.replace("buy_", "")
    pack = PACKAGES.get(pack_id)
    if not pack:
        await callback.answer("Ошибка: пакет не найден.")
        return

    async with async_session() as session:
        db_user = await get_user(session, callback.from_user.id)
        if not db_user:
            await callback.answer("Сначала зарегистрируйтесь!")
            return

        pay_id, pay_url = await create_payment(
            amount=pack["price"],
            description=f"Оплата: {pack['name']}",
            user_id=db_user.id
        )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", url=pay_url)],
        [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data=f"check_pay_{pay_id}_{pack_id}")]
    ])

    await callback.message.answer(
        f"💳 <b>Оплата пакета: {pack['name']}</b>\n\n"
        f"Сумма: <b>{pack['price']}₽</b>\n"
        "Нажмите кнопку ниже для перехода к оплате. После оплаты вернитесь и нажмите «Проверить».",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data == "buy_slots_menu")
async def buy_slots_callback(callback: types.CallbackQuery):
    await show_packages(callback.message)
    await callback.answer()

@router.callback_query(F.data.startswith("check_pay_"))
async def verify_payment(callback: types.CallbackQuery):
    # Пытаемся распарсить: check_pay_PAYID_PACKID
    parts = callback.data.split("_")
    if len(parts) < 4:
        await callback.answer("Ошибка данных платежа.")
        return
        
    pay_id = parts[2]
    pack_id = "_".join(parts[3:]) # На случай если pack_id содержит underscore (например pack_5)
    
    status = await check_payment_status(pay_id)
    
    if status == "succeeded":
        pack = PACKAGES.get(pack_id)
        if not pack:
            await callback.answer("Пакет не найден.")
            return
            
        slots_to_add = pack["slots"]
        
        async with async_session() as session:
            db_user = await get_user(session, callback.from_user.id)
            if not db_user:
                await callback.answer("Пользователь не найден.")
                return
                
            new_slots = db_user.ad_slots + slots_to_add
            # Используем прямое обновление для надежности
            from db.models.user import User
            await session.execute(
                update(User).where(User.id == db_user.id).values(ad_slots=new_slots)
            )
            await session.commit()
            
        await callback.message.edit_text(
            f"✅ <b>Оплата получена!</b>\n\n"
            f"Вам начислено: <b>{slots_to_add}</b> лимитов на объявления.\n"
            f"Текущий баланс: <b>{new_slots}</b>.",
            parse_mode="HTML"
        )
    elif status == "pending":
        await callback.answer("⏳ Оплата еще обрабатывается. Попробуйте через минуту.", show_alert=True)
    else:
        await callback.answer(f"❌ Платеж не найден или отменен. (Статус: {status})", show_alert=True)
