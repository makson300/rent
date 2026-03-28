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
        
        buttons = [
            [InlineKeyboardButton(text="🚀 В топ (200 ₽)", callback_data=f"promote_init_{l.id}"),
             InlineKeyboardButton(text="⭐️ В топ (100 ⭐️)", callback_data=f"promote_xtr_{l.id}")]
        ]
        if getattr(db_user, 'referral_bonus', 0) > 0:
            buttons.append([InlineKeyboardButton(text="🎁 Бесплатно в ТОП (Бонус)", callback_data=f"promote_bonus_{l.id}")])
            
        buttons.append([InlineKeyboardButton(text="🗑 Удалить", callback_data=f"my_delete_{l.id}")])
        kb = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        if l.photos:
            await message.answer_photo(l.photos[0].photo_id, caption=text[:1024], reply_markup=kb, parse_mode="HTML")
        else:
            await message.answer(text, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data.startswith("my_delete_"))
async def process_delete_listing(callback: types.CallbackQuery):
    listing_id = int(callback.data.split("_")[2])
    
    async with async_session() as session:
        await delete_listing(session, listing_id)
        
    await callback.message.delete()
    await callback.answer("Объявление удалено", show_alert=True)

@router.callback_query(F.data.startswith("promote_init_"))
async def promote_init(callback: types.CallbackQuery):
    listing_id = int(callback.data.split("_")[2])
    amount = 200
    description = f"VIP-продвижение объявления #{listing_id}"
    
    from bot.payments import create_payment
    payment = await create_payment(amount, description, "https://t.me/rent_equipment_bot")
    
    if payment and payment.confirmation and payment.confirmation.confirmation_url:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Оплатить (ЮKassa)", url=payment.confirmation.confirmation_url)],
            [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"check_promote_{payment.id}_{listing_id}")]
        ])
        await callback.message.answer(
            f"🚀 <b>Продвижение объявления (VIP-статус)</b>\n\n"
            f"Стоимость: <b>200 ₽</b>\n"
            f"Ваше объявление будет показываться выше остальных в каталоге и поиске.\n\n"
            f"Для оплаты перейдите по ссылке ниже.",
            reply_markup=kb, parse_mode="HTML"
        )
    else:
        await callback.answer("Ошибка при создании платежа.", show_alert=True)
    await callback.answer()

@router.callback_query(F.data.startswith("check_promote_"))
async def check_promote_payment(callback: types.CallbackQuery):
    parts = callback.data.split("_", 3)
    payment_id = parts[2]
    listing_id = int(parts[3])
    
    from bot.payments import check_payment_status
    status = await check_payment_status(payment_id)
    
    if status == "succeeded":
        from sqlalchemy import update
        from db.models.listing import Listing
        async with async_session() as session:
            await session.execute(
                update(Listing).where(Listing.id == listing_id).values(is_promoted=True)
            )
            await session.commit()
            
        await callback.message.edit_text("✅ <b>Успешно!</b> Ваше объявление поднято в топ.", parse_mode="HTML")
    else:
        await callback.answer(f"Платеж еще не подтвержден. Статус: {status}", show_alert=True)

@router.callback_query(F.data.startswith("promote_xtr_"))
async def promote_init_xtr(callback: types.CallbackQuery):
    listing_id = int(callback.data.split("_")[2])
    amount = 100
    from aiogram.types import LabeledPrice
    
    await callback.message.answer_invoice(
        title="VIP-продвижение объявления",
        description=f"Размещение вашего объявления в топе поиска и каталога.",
        payload=f"promote_xtr_{listing_id}_{callback.from_user.id}",
        provider_token="",  # Пустой токен для Telegram Stars
        currency="XTR",
        prices=[LabeledPrice(label="VIP продвижение", amount=amount)]
    )
    await callback.answer()

@router.pre_checkout_query(lambda query: query.invoice_payload.startswith("promote_xtr_"))
async def pre_checkout_xtr(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment, lambda message: message.successful_payment.invoice_payload.startswith("promote_xtr_"))
async def process_successful_payment_xtr(message: types.Message):
    payload_parts = message.successful_payment.invoice_payload.split("_")
    listing_id = int(payload_parts[2])
    
    from sqlalchemy import update
    from db.models.listing import Listing
    async with async_session() as session:
        await session.execute(
            update(Listing).where(Listing.id == listing_id).values(is_promoted=True)
        )
        await session.commit()
        
    await message.answer("✅ <b>Успешно оплачено Stars!</b> Ваше объявление поднято в топ.", parse_mode="HTML")

@router.callback_query(F.data.startswith("promote_bonus_"))
async def promote_bonus(callback: types.CallbackQuery):
    listing_id = int(callback.data.split("_")[2])
    
    from sqlalchemy import update
    from db.models.listing import Listing
    from db.models.user import User
    from db.crud.user import get_user
    
    async with async_session() as session:
        user = await get_user(session, callback.from_user.id)
        if not user or getattr(user, 'referral_bonus', 0) <= 0:
            await callback.answer("У вас нет доступных бонусов", show_alert=True)
            return
            
        # Уменьшаем бонус
        await session.execute(
            update(User).where(User.id == user.id).values(referral_bonus=User.referral_bonus - 1)
        )
        
        # Продвигаем листинг
        await session.execute(
            update(Listing).where(Listing.id == listing_id).values(is_promoted=True)
        )
        await session.commit()
        
    await callback.message.edit_text("🎁 <b>Успешно!</b> Вы использовали бонус. Ваше объявление поднято в топ.", parse_mode="HTML")
    await callback.answer()
