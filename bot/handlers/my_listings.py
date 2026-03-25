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
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"my_delete_{l.id}")]
        ])
        
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
