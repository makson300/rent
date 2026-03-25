import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from bot.config import BOT_TOKEN # Assuming we might want to check against an ADMIN_ID eventually
from db.base import async_session
from sqlalchemy import select, update
from db.models.listing import Listing
from sqlalchemy.orm import selectinload
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
logger = logging.getLogger(__name__)

# Whitelist of administrators
ADMIN_USERNAMES = ["vmandco"] # Use lowercase here
ADMIN_IDS = [] # Can be populated with numeric IDs later

def is_admin(message: types.Message) -> bool:
    username = (message.from_user.username or "").lower()
    return (username in ADMIN_USERNAMES) or (message.from_user.id in ADMIN_IDS)

@router.message(Command("admin"))
async def admin_main(message: types.Message):
    """Главный вход в админку"""
    if not is_admin(message):
        await message.answer("⛔️ У вас нет прав доступа к этой команде.")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👁 На модерации", callback_data="admin_moderation_list")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")]
    ])
    await message.answer("🛠 <b>Панель администратора</b>", parse_mode="HTML", reply_markup=kb)

@router.callback_query(F.data == "admin_moderation_list")
async def moderation_list(callback: types.CallbackQuery):
    async with async_session() as session:
        result = await session.execute(
            select(Listing).options(selectinload(Listing.photos)).where(Listing.status == "moderation")
        )
        listings = result.scalars().all()
    
    if not listings:
        await callback.message.answer("✅ Новых объявлений на модерации нет.")
        await callback.answer()
        return

    await callback.message.answer(f"📋 Найдено объявлений: {len(listings)}")
    
    for l in listings:
        text = (
            f"ID: {l.id}\n"
            f"👤 Юзер ID: {l.user_id}\n"
            f"🏘 Город: {l.city}\n"
            f"📦 {l.title}\n\n"
            f"{l.description}"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Одобрить", callback_data=f"admin_approve_{l.id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_{l.id}")
            ]
        ])
        
        if l.photos:
            await callback.message.answer_photo(l.photos[0].photo_id, caption=text[:1024], reply_markup=kb)
        else:
            await callback.message.answer(text, reply_markup=kb)
            
    await callback.answer()

@router.callback_query(F.data.startswith("admin_approve_"))
async def approve_listing(callback: types.CallbackQuery):
    listing_id = int(callback.data.split("_")[2])
    async with async_session() as session:
        await session.execute(
            update(Listing).where(Listing.id == listing_id).values(status="active")
        )
        await session.commit()
    
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ <b>ОДОБРЕНО</b>", parse_mode="HTML")
    await callback.answer("Объявление одобрено!")

@router.callback_query(F.data.startswith("admin_reject_"))
async def reject_listing(callback: types.CallbackQuery):
    listing_id = int(callback.data.split("_")[2])
    async with async_session() as session:
        await session.execute(
            update(Listing).where(Listing.id == listing_id).values(status="rejected")
        )
        await session.commit()
    
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ <b>ОТКЛОНЕНО</b>", parse_mode="HTML")
    await callback.answer("Объявление отклонено!")
