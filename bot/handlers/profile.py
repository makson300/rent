import logging
from aiogram import Router, types, F
from db.base import async_session
from db.crud.user import get_user
from bot.keyboards import get_main_menu

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

    phone_display = user.phone or "не указан"
    created = user.created_at.strftime("%d.%m.%Y") if user.created_at else "—"

    await message.answer(
        f"👤 <b>Ваш профиль</b>\n\n"
        f"Имя: {user.first_name or '—'} {user.last_name or ''}\n"
        f"Телефон: {phone_display}\n"
        f"Дата регистрации: {created}\n",
        parse_mode="HTML",
        reply_markup=get_main_menu(),
    )
