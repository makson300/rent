import logging
import re
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import ADMIN_IDS

router = Router()
logger = logging.getLogger(__name__)

class SupportStates(StatesGroup):
    waiting_for_message = State()

@router.message(F.text == "📩 Обратная связь")
async def support_init(message: types.Message, state: FSMContext):
    """Начало создания тикета в техподдержку"""
    await state.set_state(SupportStates.waiting_for_message)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="support_cancel")]
    ])
    
    await message.answer(
        "🎧 <b>Служба поддержки</b>\n\n"
        "Пожалуйста, подробно опишите ваш вопрос или проблему. "
        "Вы можете прикрепить фото или видео к сообщению.\n\n"
        "Администраторы ответят вам здесь же.",
        parse_mode="HTML",
        reply_markup=kb
    )

@router.callback_query(F.data.startswith("escalate_"))
async def process_escalate_feedback(callback: types.CallbackQuery):
    """Эскалация тикета к админу после ответа ИИ"""
    feedback_id = int(callback.data.split("_")[1])
    await callback.message.edit_reply_markup(reply_markup=None)
    
    from db.base import async_session
    from db.models.feedback import Feedback
    from sqlalchemy import select
    
    async with async_session() as session:
        feedback = await session.scalar(select(Feedback).where(Feedback.id == feedback_id))
        if feedback:
            feedback.status = "escalated"
            await session.commit()
            
    target_admin = ADMIN_IDS[0] if ADMIN_IDS else None
    if not target_admin or not feedback:
        await callback.answer("⚠️ Не настроены контакты администраторов или тикет не найден.", show_alert=True)
        return
        
    username = f"@{callback.from_user.username}" if callback.from_user.username else "Нет юзернейма"
    info_msg = (
        f"📩 <b>Эскалация тикета #{feedback_id}!</b>\n"
        f"От: {callback.from_user.first_name} ({username})\n"
        f"Тип: {feedback.type}\n"
        f"Текст:\n<i>{feedback.message}</i>\n\n"
        f"<code>#ticket_{callback.from_user.id}</code>\n"
        f"<i>Сделайте Reply (Ответить) на сообщение ниже, чтобы ответить юзеру.</i>"
    )
    
    try:
        await callback.message.bot.send_message(chat_id=target_admin, text=info_msg, parse_mode="HTML")
        await callback.answer("✅ Тикет передан администратору.", show_alert=True)
        await callback.message.answer("Ожидайте ответа администратора в этом чате.")
    except Exception as e:
        logger.error(f"Failed to send escalated ticket: {e}")
        await callback.answer("⚠️ Ошибка при отправке.", show_alert=True)


@router.message(F.reply_to_message)
async def admin_support_reply(message: types.Message):
    """Перехват ответа админа на пересланное сообщение юзера и отправка ответа юзеру"""
    # Проверяем, что отвечает админ
    if message.from_user.id not in ADMIN_IDS:
        return
    
    import math
    reply_msg = message.reply_to_message
    
    # Ищем тег #ticket_123456 в ближайших 2-3 сообщениях админа или в самом reply, 
    # но самый надежный способ - если админ делает реплай на оригинальный текст/фото юзера,
    # мы тут не видим ID напрямую без FSM. Для упрощения:
    # мы будем анализировать пересланное от пользователя сообщение 
    # (если forward_from включен) или просто извлекать ID из текста, 
    # но Aiogram copy_to не сохраняет forward_from.
    # Поэтому мы используем простое решение:
    # Сначала пытаемся вытащить forward_origin ID. Если его нет (приватность),
    # просим админов отвечать ИМЕННО на служебное сообщение с тегом #ticket_.
    
    target_user_id = None
    
    # Вариант 1: Админ ответил на служебное сообщение с тегом
    if reply_msg.text and "#ticket_" in reply_msg.text:
        match = re.search(r"#ticket_(\d+)", reply_msg.text)
        if match:
            target_user_id = int(match.group(1))
            
    # Если ID не найден - выходим (скорее всего это просто общение между админами или случайный реплай)
    if not target_user_id:
        return
        
    try:
        await message.copy_to(chat_id=target_user_id)
        # Отправляем дополнительную плашку
        # await message.bot.send_message(target_user_id, "<i>Сообщение от службы поддержки</i>", parse_mode="HTML")
        await message.answer("✅ <b>Ответ отправлен пользователю!</b>", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to pass admin reply to user {target_user_id}: {e}")
        await message.answer(f"⚠️ Ошибка при отправке ответа пользователю: {e}")
