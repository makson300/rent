import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, func
from db.models.review import Review

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "👤 Профиль")
async def show_profile(message: types.Message):
    """Показать профиль пользователя"""
    async with async_session() as session:
        user = await get_user(session, message.from_user.id)
        
        if not user:
            await message.answer("⚠️ Вы не зарегистрированы. Введите /start")
            return
            
        # Считаем рейтинг
        rating_res = await session.execute(
            select(func.avg(Review.rating), func.count(Review.id))
            .where(Review.target_user_id == user.id)
        )
        avg_rating, review_count = rating_res.fetchone()

    phone_display = user.phone or "не указан"
    created = user.created_at.strftime("%d.%m.%Y") if user.created_at else "—"
    u_type_display = "🏢 Компания / Прокат" if user.user_type == "company" else "👤 Частное лицо"
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    stars = "⭐" * int(avg_rating) if avg_rating else "Нет оценок"

    kb_list = [
        [InlineKeyboardButton(text="📋 Мои объявления", callback_data="my_listings_list")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")]
    ]
    
    if user.user_type == "company":
        kb_list.insert(0, [InlineKeyboardButton(text="💎 Пополнить пакет объявлений", callback_data="buy_slots_menu")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)

    slots_text = f"Доступно лимитов: <b>{user.ad_slots}</b>\n" if user.user_type == "company" else ""

    await message.answer(
        f"👤 <b>Ваш профиль</b>\n\n"
        f"Статус: <b>{u_type_display}</b>\n"
        f"Рейтинг: {stars} ({avg_rating} / {review_count} отз.)\n"
        f"Имя: {user.first_name or '—'}\n"
        f"Телефон: {phone_display}\n"
        f"Регистрация: {created}\n\n"
        f"{slots_text}",
        parse_mode="HTML",
        reply_markup=kb,
    )

@router.callback_query(F.data == "buy_slots_menu")
@router.callback_query(F.data == "buy_slots_from_create")
async def buy_slots_redirect(callback: types.CallbackQuery):
    from bot.handlers.packages import show_packages
    await show_packages(callback.message)
    await callback.answer()
