import logging
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, func
from db.models.review import Review
from db.base import async_session
from db.crud.user import get_user

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
    if getattr(user, 'volunteer_rescues', 0) > 0:
        u_type_display += f"\n🏅 <b>Проверенный Волонтер</b> ({user.volunteer_rescues} выездов на ЧП)"
        
    if getattr(user, 'has_license', False) and getattr(user, 'has_medical', False):
        u_type_display += "\n✅ <b>Проверенный Пилот</b> (Лицензия + ВЛЭК подтверждены)"
        
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    stars = "⭐" * int(avg_rating) if avg_rating else "Нет оценок"

    kb_list = [
        [InlineKeyboardButton(text="📋 Мои объявления", callback_data="my_listings_list")],
        [InlineKeyboardButton(text="🛩 Моя Аэронавигация (ИВП)", callback_data="my_orvd")],
        [InlineKeyboardButton(text="🎁 Пригласить друга", callback_data="invite_friend")]
    ]
    
    if not (getattr(user, 'has_license', False) and getattr(user, 'has_medical', False)):
        kb_list.append([InlineKeyboardButton(text="🏅 Получить статус 'Проверен'", callback_data="verify_pilot_status")])
        
    kb_list.append([InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")])
    
    if user.user_type == "company":
        kb_list.insert(0, [InlineKeyboardButton(text="💎 Пополнить пакет", callback_data="buy_slots_menu")])
    
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

@router.callback_query(F.data == "invite_friend")
async def invite_friend(callback: types.CallbackQuery):
    async with async_session() as session:
        user = await get_user(session, callback.from_user.id)
        if not user:
            return
            
    bot_info = await callback.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user.id}"
    
    await callback.message.answer(
        f"🎁 <b>Приглашайте друзей и получайте бонусы!</b>\n\n"
        f"Отправьте эту ссылку друзьям. Когда они зарегистрируются и разместят своё первое объявление, вы получите <b>+1 Бесплатное поднятие в ТОП</b> (VIP-размещение) для вашего оборудования!\n\n"
        f"Ваша ссылка:\n<code>{ref_link}</code>",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "verify_pilot_status")
async def verify_pilot_status(callback: types.CallbackQuery):
    await callback.message.answer(
        "🏅 <b>Верификация Пилота</b>\n\n"
        "Статус «Проверенный Пилот» повышает доверие заказчиков и продвигает ваши услуги в ТОП.\n\n"
        "Для получения статуса необходимо предоставить:\n"
        "1. Действующее Свидетельство внешнего пилота.\n"
        "2. Медицинское заключение (ВЛЭК/ОМО).\n"
        "3. Подтвержденный налет от 20 часов.\n\n"
        "Пожалуйста, отправьте сканы документов нашему модератору: @SkyRent_Support",
        parse_mode="HTML"
    )
    await callback.answer()
