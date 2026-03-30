import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.services.vision_moderator import analyze_emergency_photo

router = Router()
logger = logging.getLogger(__name__)

class AssessmentStates(StatesGroup):
    waiting_for_photo = State()

@router.message(Command("assess"))
async def start_assessment(message: types.Message, state: FSMContext):
    """Начало процесса оценки места ЧС оператором дрона."""
    await message.answer(
        "🚨 <b>Аналитика ЧС / Повреждений (MoMoA Vision)</b>\n\n"
        "Отправьте фотографию с дрона (или обычное фото с места), "
        "чтобы нейросеть Горизонт провела мгновенную оценку опасности и разрушений.",
        parse_mode="HTML"
    )
    await state.set_state(AssessmentStates.waiting_for_photo)

@router.message(AssessmentStates.waiting_for_photo, F.photo)
async def process_assessment_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id # Берем лучшее разрешение
    
    wait_msg = await message.answer("⏳ <i>MoMoA анализирует кадры... пожалуйста, подождите.</i>", parse_mode="HTML")
    
    # Отправляем фото в Gemini Vision
    analysis = await analyze_emergency_photo(message.bot, photo_id)
    
    await wait_msg.delete()
    
    danger_level = analysis.get("danger_level", "UNKNOWN")
    level_emoji = {
        "CRITICAL": "🔴",
        "HIGH": "🟠",
        "MEDIUM": "🟡",
        "LOW": "🟢",
        "ERROR": "❌"
    }.get(danger_level, "⚪")
    
    report = (
        f"📊 <b>Рапорт по ЧС (MoMoA Analytics)</b>\n\n"
        f"<b>Уровень опасности:</b> {level_emoji} {danger_level}\n\n"
        f"<b>Сводка:</b>\n{analysis.get('summary', 'Нет сводки')}\n\n"
        f"<b>Детальная оценка:</b>\n{analysis.get('details', 'Нет деталей')}\n\n"
        f"<b>Рекомендации:</b>\n<i>{analysis.get('recommendation', '-')}</i>"
    )
    
    await message.answer(report, parse_mode="HTML")
    await state.clear()

@router.message(AssessmentStates.waiting_for_photo)
async def process_invalid_assessment(message: types.Message):
    await message.answer("⚠️ Пожалуйста, отправьте именно *фотографию*, чтобы система могла провести анализ.", parse_mode="Markdown")
