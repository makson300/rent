import logging
from aiogram import Router, types, F
from db.base import async_session
from db.crud.listing import get_user_listings, delete_listing
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from db.models.user import User

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "📋 Мои объявления")
@router.callback_query(F.data == "my_listings_list")
async def show_my_listings(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    message = event if isinstance(event, types.Message) else event.message

    from db.crud.user import get_user
    async with async_session() as session:
        db_user = await get_user(session, user_id)
        if not db_user:
            await message.answer("⚠️ Сначала зарегистрируйтесь!")
            return
        listings = await get_user_listings(session, db_user.id)
        
    if not listings:
        await message.answer("📋 У вас пока нет созданных объявлений.")
        return

    await message.answer(f"📋 <b>Ваши объявления ({len(listings)}):</b>", parse_mode="HTML")
    
    for l in listings:
        status_map = {
            "moderation": "⏳ На модерации",
            "active": "✅ Активно",
            "rejected": "❌ Отклонено",
            "expired": "⌛️ Истекло"
        }
        status_text = status_map.get(l.status, l.status)
        
        text = (
            f"📦 <b>{l.title}</b>\n"
            f"🏙 Город: {l.city}\n"
            f"📊 Статус: {status_text}\n\n"
            f"💰 Цены: {l.price_list}"
        )
        
        vip_status = "💎 VIP" if l.is_vip else ""
        text = (
            f"{vip_status}\n"
            f"📦 <b>{l.title}</b>\n"
            f"🏙 Город: {l.city}\n"
            f"📊 Статус: {status_text}\n\n"
            f"💰 Цены: {l.price_list}"
        )

        kb_buttons = []
        if not l.is_vip and l.status == "active":
             kb_buttons.append([InlineKeyboardButton(text="💎 Стать VIP (700 ₽)", callback_data=f"my_vip_{l.id}")])

        kb_buttons.append([InlineKeyboardButton(text="🗑 Удалить", callback_data=f"my_delete_{l.id}")])

        kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
        
        if l.photos:
            await message.answer_photo(l.photos[0].photo_id, caption=text[:1024], reply_markup=kb, parse_mode="HTML")
        else:
            await message.answer(text, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data.startswith("my_vip_"))
async def process_vip_promotion(callback: types.CallbackQuery):
    listing_id = int(callback.data.split("_")[2])

    from bot.services.yookassa_service import create_payment
    bot_info = await callback.bot.get_me()
    return_url = f"https://t.me/{bot_info.username}"

    try:
        payment = await create_payment(700, f"VIP статус для объявления #{listing_id}", return_url)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Оплатить 700 ₽", url=payment.confirmation.confirmation_url)],
            [InlineKeyboardButton(text="✅ Проверить оплату", callback_data=f"check_pay_vip_{listing_id}:{payment.id}")]
        ])
        await callback.message.answer(
            f"💎 <b>Продвижение объявления</b>\n\n"
            f"VIP-статус поднимет ваше объявление в самый верх каталога на 30 дней.\n"
            f"Стоимость: 700 ₽",
            parse_mode="HTML",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"VIP payment error: {e}")
        await callback.message.answer("❌ Ошибка платежной системы.")
    await callback.answer()


@router.callback_query(F.data.startswith("check_pay_vip_"))
async def check_vip_payment(callback: types.CallbackQuery):
    data = callback.data.replace("check_pay_vip_", "").split(":")
    listing_id = int(data[0])
    payment_id = data[1]

    from bot.services.yookassa_service import get_payment_status
    status = await get_payment_status(payment_id)

    if status == "succeeded":
        from db.crud.listing import set_listing_vip
        async with async_session() as session:
            await set_listing_vip(session, listing_id)

        await callback.message.edit_text("✅ <b>Оплата прошла успешно!</b>\nВаше объявление теперь имеет статус 💎 VIP.", parse_mode="HTML")
    else:
        await callback.answer("⏳ Оплата еще не подтверждена.", show_alert=True)


@router.callback_query(F.data.startswith("my_delete_"))
async def process_delete_listing(callback: types.CallbackQuery):
    listing_id = int(callback.data.split("_")[2])
    
    async with async_session() as session:
        await delete_listing(session, listing_id)
        
    await callback.message.delete()
    await callback.answer("Объявление удалено", show_alert=True)
