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
    from sqlalchemy.orm import selectinload
    from db.models.user import User
    
    async with async_session() as session:
        user = await session.scalar(
            select(User).options(selectinload(User.rewards))
            .where(User.telegram_id == message.from_user.id)
        )
        
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
    rescues = getattr(user, 'volunteer_rescues', 0)
    
    # Расчет ранга волонтера
    rank = "Новичок"
    if rescues >= 1: rank = "Скаут"
    if rescues >= 5: rank = "Спасатель"
    if rescues >= 10: rank = "Ветеран"
    if rescues >= 50: rank = "Герой Горизонта"
    
    if rescues > 0:
        u_type_display += f"\n🏅 <b>Волонтер ({rank})</b> — {rescues} выездов на ЧП"
        
    if getattr(user, 'has_license', False) and getattr(user, 'has_medical', False):
        u_type_display += "\n✅ <b>Проверенный Пилот</b> (Лицензия + ВЛЭК подтверждены)"
        
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    stars = "⭐" * int(avg_rating) if avg_rating else "Нет оценок"

    kb_list = [
        [InlineKeyboardButton(text="📋 Мои объявления", callback_data="my_listings_list")],
        [InlineKeyboardButton(text="🔧 Мой Ангар (ТО)", callback_data="fleet_menu")],
        [InlineKeyboardButton(text="✈️ Цифровая Лётная Книжка (LogBook)", callback_data="logbook_menu")],
        [InlineKeyboardButton(text="⚖️ Легальные Полеты и Учет", callback_data="legal_hub")],
        [InlineKeyboardButton(text="🎁 Пригласить друга", callback_data="invite_friend")]
    ]
    
    if not (getattr(user, 'has_license', False) and getattr(user, 'has_medical', False)):
        kb_list.append([InlineKeyboardButton(text="🏅 Получить статус 'Проверен'", callback_data="verify_pilot_status")])
        
    kb_list.append([InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")])
    
    if user.user_type == "company":
        inn_text = getattr(user, 'inn', 'Не указан')
        kb_list.insert(0, [InlineKeyboardButton(text=f"🏢 Моя Компания (ИНН {inn_text})", callback_data="setup_company")])
        kb_list.insert(1, [InlineKeyboardButton(text="💎 Пополнить пакет", callback_data="buy_slots_menu")])
    else:
        kb_list.insert(0, [InlineKeyboardButton(text="🏢 Сделать Компанией (B2B/B2G)", callback_data="setup_company")])
        
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)

    slots_text = f"Доступно лимитов: <b>{getattr(user, 'ad_slots', 0)}</b>\n" if user.user_type == "company" else ""
    
    # Блок наград (NFT 메дали)
    rewards_text = ""
    if user.rewards:
        rewards_text = "\n🏆 <b>ВАШИ НАГРАДЫ (NFT-Медали):</b>\n"
        for r in user.rewards:
            rewards_text += f"{r.emoji} <b>{r.title}</b> — <i>{r.description or ''}</i>\n"
        rewards_text += "\n"

    await message.answer(
        f"👤 <b>Ваш профиль</b>\n\n"
        f"Статус: <b>{u_type_display}</b>\n"
        f"Рейтинг: {stars} ({avg_rating} / {review_count} отз.)\n"
        f"Имя: {user.first_name or '—'}\n"
        f"Телефон: {phone_display}\n"
        f"Налет (ИИ-Подтвержден): <b>{getattr(user, 'verified_flight_hours', 0.0):.1f} ч.</b>\n"
        f"Регистрация: {created}\n\n"
        f"{rewards_text}"
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
