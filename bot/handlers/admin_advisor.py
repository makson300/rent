import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, func
from datetime import datetime, timedelta

from db.base import async_session
from db.models.user import User
from db.models.listing import Listing
from db.models.category import Category
from db.models.emergency import EmergencyAlert
from bot.services.advisor import advisor_service
from bot.config import ADMIN_IDS

router = Router()
logger = logging.getLogger(__name__)

class AdvisorStates(StatesGroup):
    waiting_for_prompt = State()

async def fetch_platform_stats() -> dict:
    """Собирает статистику для MoMoA Advisor'а"""
    stats = {}
    async with async_session() as session:
        # Всего юзеров
        users_count = await session.scalar(select(func.count(User.id)))
        stats['total_users'] = users_count or 0
        
        # Юзеров за месяц
        month_ago = datetime.utcnow() - timedelta(days=30)
        new_users = await session.scalar(select(func.count(User.id)).where(User.created_at >= month_ago))
        stats['new_users_month'] = new_users or 0
        
        # Листинги: Аренда (id=1)
        r_listings = await session.scalar(select(func.count(Listing.id)).where(Listing.category_id == 1, Listing.status == "active"))
        stats['rent_listings'] = r_listings or 0
        
        # Листинги: Продажа (id=2)
        s_listings = await session.scalar(select(func.count(Listing.id)).where(Listing.category_id == 2, Listing.status == "active"))
        stats['sale_listings'] = s_listings or 0
        
        # Операторы (id=6)
        o_listings = await session.scalar(select(func.count(Listing.id)).where(Listing.category_id == 6, Listing.status == "active"))
        stats['operators_count'] = o_listings or 0 # approximate revenue = operators * 1000
        stats['revenue'] = (o_listings or 0) * 1000
        
        # Заявки на ЧП
        emergencies = await session.scalar(select(func.count(EmergencyAlert.id)))
        stats['total_emergencies'] = emergencies or 0
        
    return stats


@router.callback_query(F.data == "admin_momoa_advisor")
async def start_advisor(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет прав", show_alert=True)
        return
        
    await callback.message.edit_text("⏳ MoMoA-Сoветник собирает статистику и анализирует проект... Пожалуйста, подождите.")
    
    # 1. Сбор статы
    stats = await fetch_platform_stats()
    
    # 2. Вызов MoMoA-DailyPlan
    daily_plan = await advisor_service.generate_daily_plan(stats)
    
    text = (
        f"🧠 <b>MoMoA Главный Советник</b>\n\n"
        f"{daily_plan}\n\n"
        f"<i>Вы вошли в режим диалога с ИИ. Напишите мне любой вопрос о проекте, стратегиях или маркетинге.</i>"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚪 Выйти из режима диалога", callback_data="exit_advisor")]
    ])
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    
    # Сохраняем стату в state, чтобы не дергать БД на каждый вопрос
    await state.update_data(platform_stats=stats, chat_history="")
    await state.set_state(AdvisorStates.waiting_for_prompt)


@router.message(AdvisorStates.waiting_for_prompt, F.text)
async def advisor_chat_handler(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
        
    # Показываем статус "печатает"
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    data = await state.get_data()
    stats = data.get("platform_stats", {})
    history = data.get("chat_history", "")
    
    # Задаем ИИ вопрос
    answer = await advisor_service.answer_question(message.text, stats, history)
    
    # Обновляем простую историю в state
    new_history = history + f"\nAdmin: {message.text}\nAdvisor: {answer}\n"
    # Ограничиваем длинную историю (последние ~2000 символов)
    new_history = new_history[-2000:]
    await state.update_data(chat_history=new_history)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚪 Завершить диалог", callback_data="exit_advisor")]
    ])
    
    await message.answer(f"🧠 <b>MoMoA:</b>\n{answer}", parse_mode="HTML", reply_markup=kb)

@router.callback_query(F.data == "exit_advisor")
async def exit_advisor(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🤖 Диалог с Главным Советником завершен. Для вызова главного меню админки введите /admin")
