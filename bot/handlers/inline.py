import logging
from aiogram import Router, types, F
from db.base import async_session
from db.crud.user import get_user
from typing import List

router = Router()
logger = logging.getLogger(__name__)


@router.inline_query()
async def inline_search(inline_query: types.InlineQuery):
    """
    Обработчик инлайн-запросов (когда пользователь вводит @BotName ...)
    Позволяет пилоту в любом чате поделиться карточкой своего профиля.
    """
    query = inline_query.query.strip().lower()
    
    async with async_session() as session:
        user = await get_user(session, inline_query.from_user.id)
        if not user:
            # Пользователь не зарегистрирован, показываем пустой результат
            await inline_query.answer([])
            return
            
        results: List[types.InlineQueryResultArticle] = []
        
        # 1. Личная карточка Пилота (B2B Профиль)
        title = "Вывести визитку Пилота"
        description = "Ваш рейтинг, часы налета и отзывы"
        thumb_url = "https://cdn-icons-png.flaticon.com/512/3665/3665971.png" # Иконка дрона
        
        company_badge = f"🏢 {user.company_name}" if getattr(user, 'company_name', None) else "💼 Частный пилот"
        rating = "⭐️" * int(getattr(user, 'rating', 5) or 5)
        
        # Содержание сообщения, которое будет отправлено в чат
        message_text = (
            f"👤 <b>Профиль пилота в экосистеме Горизонт</b>\n\n"
            f"Имя: <b>{user.first_name}</b>\n"
            f"Статус: {company_badge}\n"
            f"Рейтинг: {rating} (Налет: {getattr(user, 'verified_flight_hours', 0)} ч.)\n"
            f"Спасенных (ЧП): {getattr(user, 'volunteer_rescues', 0)}\n\n"
            f"<i>Для аренды оборудования и поиска тендеров перейдите в бота👇</i>"
        )
        
        # Кнопка для перехода инлайн
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🚁 Перейти в Горизонт", url="https://t.me/rent_equipment_bot")]
        ])
        
        item = types.InlineQueryResultArticle(
            id="profile_1",
            title=title,
            description=description,
            thumbnail_url=thumb_url,
            input_message_content=types.InputTextMessageContent(
                message_text=message_text,
                parse_mode="HTML"
            ),
            reply_markup=kb
        )
        
        results.append(item)
        
        # Отправляем результаты
        await inline_query.answer(
            results,
            cache_time=1,
            is_personal=True,
            switch_pm_text="Настроить профиль",
            switch_pm_parameter="profile"
        )
