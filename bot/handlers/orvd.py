import logging
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from db.base import async_session
from db.crud.user import get_user
from db.models.flight_plan import FlightPlan

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data == "legal_hub")
async def legal_hub_menu(callback: types.CallbackQuery):
    """Главное меню Правового Хаба"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Учет БВС (Росавиация)", callback_data="legal_rosaviatsiya")],
        [InlineKeyboardButton(text="🛩 Моя Аэронавигация (ИВП)", callback_data="my_orvd")],
        [InlineKeyboardButton(text="📖 База Законов и Карты", web_app=types.WebAppInfo(url="https://skyrent.pro/dashboard/legal"))],
        [InlineKeyboardButton(text="🔙 В профиль", callback_data="back_to_profile")]
    ])
    
    await callback.message.edit_text(
        "⚖️ <b>Правовой Хаб Пилота</b>\n\nЗдесь вы можете подготовить документы для Росавиации, подать заявки на ИВП (Местный Режим) и следить за их статусом.",
        parse_mode="HTML",
        reply_markup=kb
    )

@router.callback_query(F.data == "legal_rosaviatsiya")
async def legal_rosaviatsiya_menu(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Открыть Генератор Заявления", web_app=types.WebAppInfo(url="https://skyrent.pro/dashboard/legal"))],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="legal_hub")]
    ])
    
    await callback.message.edit_text(
        "🇷🇺 <b>Учет БВС в Росавиации</b>\n\nВсе дроны от 150 грамм подлежат учету. Мы подготовили бесплатный инструмент, который прямо в вашем смартфоне/на ПК сгенерирует правильное Заявление."
        "\n\nПросто нажмите кнопку ниже, заполните данные, распечатайте готовый PDF и отправьте почтой в Росавиацию!",
        parse_mode="HTML",
        reply_markup=kb
    )

@router.callback_query(F.data == "my_orvd")
async def my_orvd_menu(callback: types.CallbackQuery):
    """Меню управления аэронавигацией и заявками"""
    async with async_session() as session:
        user = await get_user(session, callback.from_user.id)
        if not user:
            return
            
        result = await session.execute(
            select(FlightPlan).where(FlightPlan.user_id == user.id).order_by(FlightPlan.created_at.desc()).limit(5)
        )
        plans = result.scalars().all()
        
    text = "🛩 <b>АЭРОНАВИГАЦИЯ (СППИ ОрВД)</b>\n\nЗдесь вы можете контролировать статусы ваших планов полетов (ИВП), сформированных на нашем веб-портале.\n\n"
    
    if not plans:
        text += "<i>У вас пока нет поданных планов полета.</i>"
    else:
        text += "<b>Ваши последние заявки:</b>\n"
        status_map = {
            "pending": "⏳ На согласовании",
            "approved": "✅ Разрешено!",
            "rejected": "❌ Отказано",
            "draft": "📝 Черновик"
        }
        
        for p in plans:
            emoji = "🚨" if p.is_emergency else "📡"
            p_status = status_map.get(p.status, p.status)
            date_str = p.created_at.strftime("%d.%m %H:%M")
            text += f"\n{emoji} <b>[{date_str}] Зона {p.coords}</b>\n└ Статус: {p_status}"
            
    kb_list = [
        [InlineKeyboardButton(text="🚨 ЭКСТРЕННАЯ SAR ЗАЯВКА", callback_data="orvd_emergency")],
        [InlineKeyboardButton(text="Сформировать новый план (Web)", web_app=types.WebAppInfo(url="https://skyrent.pro/dashboard/legal"))],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="legal_hub")]
    ]
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_list)
    )

@router.callback_query(F.data == "orvd_emergency")
async def orvd_emergency_start(callback: types.CallbackQuery):
    """Запуск создания экстренной короткой заявки SAR"""
    # В рамках ТЗ создаем заглушку, либо просим скинуть геопозицию. 
    # Это можно развить в FSM машину состояний.
    await callback.answer("🚨 Режим экстренной подачи SAR-кода", show_alert=True)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отмена", callback_data="my_orvd")]
    ])
    
    await callback.message.edit_text(
        "🚨 <b>ЭКСТРЕННАЯ ЗАЯВКА НА ИВП (SAR)</b>\n\nФункция используется <b>ТОЛЬКО</b> при поиске пропавших людей и устранении ЧС!\n\nДля автоматического формирования экстренного МР ИВП, отправьте геопозицию центра проведения работ (через скрепку 📎 -> Геопозиция).",
        parse_mode="HTML",
        reply_markup=kb
    )
