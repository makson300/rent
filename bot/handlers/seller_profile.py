import logging
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.base import async_session
from sqlalchemy import select, func
from db.models.user import User
from db.models.review import Review
from db.crud.user import get_user

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data.startswith("view_seller_"))
async def view_seller_profile(callback: types.CallbackQuery):
    seller_id = int(callback.data.split("_")[2])
    
    async with async_session() as session:
        # Получаем данные продавца
        result = await session.execute(select(User).where(User.id == seller_id))
        seller = result.scalar_one_or_none()
        
        if not seller:
            await callback.answer("Продавец не найден.")
            return
            
        # Считаем рейтинг
        rating_res = await session.execute(
            select(func.avg(Review.rating), func.count(Review.id))
            .where(Review.target_user_id == seller_id)
        )
        avg_rating, review_count = rating_res.fetchone()
        
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    stars = "⭐" * int(avg_rating) if avg_rating else "Новый продавец"
    
    u_type_display = "🏢 Компания / Прокат" if seller.user_type == "company" else "👤 Частное лицо"
    if getattr(seller, 'volunteer_rescues', 0) > 0:
        u_type_display += f"\n🏅 <b>Проверенный Волонтер</b> ({seller.volunteer_rescues} выездов на ЧП)"
    if review_count >= 3 and avg_rating >= 4.8:
        u_type_display += "\n⭐️ <b>Надежный Арендодатель</b>"
    
    text = (
        f"👤 <b>Профиль продавца</b>\n\n"
        f"Тип: {u_type_display}\n"
        f"Имя: {seller.first_name}\n"
        f"Рейтинг: {stars} ({avg_rating})\n"
        f"Отзывов: {review_count}\n"
        f"Объявлений: {len(seller.listings)}\n"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Оставить отзыв", callback_data=f"rate_user_{seller_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_catalog")]
    ])
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("rate_user_"))
async def start_rating(callback: types.CallbackQuery):
    seller_id = int(callback.data.split("_")[2])
    
    # Чтобы не голосовать за себя
    async with async_session() as session:
        me = await get_user(session, callback.from_user.id)
        if me and me.id == seller_id:
            await callback.answer("Вы не можете оценивать сами себя!", show_alert=True)
            return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ 1", callback_data=f"set_rate_{seller_id}_1"),
         InlineKeyboardButton(text="⭐ 2", callback_data=f"set_rate_{seller_id}_2"),
         InlineKeyboardButton(text="⭐ 3", callback_data=f"set_rate_{seller_id}_3"),
         InlineKeyboardButton(text="⭐ 4", callback_data=f"set_rate_{seller_id}_4"),
         InlineKeyboardButton(text="⭐ 5", callback_data=f"set_rate_{seller_id}_5")]
    ])
    
    await callback.message.answer("Выберите оценку для продавца:", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("set_rate_"))
async def process_rating(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    seller_id = int(parts[2])
    rating = int(parts[3])
    
    async with async_session() as session:
        me = await get_user(session, callback.from_user.id)
        if not me:
            await callback.answer("Сначала зарегистрируйтесь!")
            return
            
        new_review = Review(
            target_user_id=seller_id,
            author_id=me.id,
            rating=float(rating)
        )
        session.add(new_review)
        await session.commit()
    
    await callback.message.edit_text(f"✅ Спасибо! Вы поставили оценку {rating} ⭐.")
    await callback.answer()
