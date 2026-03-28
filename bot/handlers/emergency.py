import logging
import asyncio
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.keyboards.main_menu import get_main_menu
from db.base import async_session
from db.models.emergency import EmergencyAlert

router = Router()
logger = logging.getLogger(__name__)

class EmergencyReportStates(StatesGroup):
    waiting_for_description = State()

@router.message(F.text == "🆘 ЧП")
async def start_emergency_report(message: types.Message, state: FSMContext):
    text = (
        "🚨 <b>Экстренный вызов операторов БПЛА (ЧП)</b>\n\n"
        "Этот раздел предназначен только для реальных экстренных ситуаций "
        "(поиск людей, пожары, МЧС).\n\n"
        "Пожалуйста, <b>максимально подробно</b> опишите ситуацию в одном сообщении:\n"
        "📍 Город/Локация\n"
        "🚁 Какой дрон нужен (напр., тепловизор)\n"
        "ℹ️ Суть происшествия"
    )
    kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )
    await state.set_state(EmergencyReportStates.waiting_for_description)
    await message.answer(text, parse_mode="HTML", reply_markup=kb)

@router.message(F.text == "❌ Отмена", EmergencyReportStates.waiting_for_description)
async def cancel_emergency(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=get_main_menu())

@router.message(EmergencyReportStates.waiting_for_description)
async def process_emergency_text(message: types.Message, state: FSMContext):
    raw_text = message.text
    if len(raw_text) < 15:
        await message.answer("⚠️ Описание слишком короткое. Пожалуйста, опишите ситуацию подробнее.")
        return
        
    wait_msg = await message.answer(
        "⏳ Заявка принята. Нейросеть (MoMoA) анализирует данные перед отправкой дежурному модератору...",
        reply_markup=get_main_menu()
    )
    await state.clear()
    
    # Асинхронно запускаем процесс анализа, чтобы не блокировать юзера
    asyncio.create_task(process_alert_via_momoa(message.from_user.id, raw_text, wait_msg))

async def process_alert_via_momoa(user_id: int, raw_text: str, wait_msg: types.Message):
    from bot.services.emergency_monitor import EmergencyMonitor
    # Нам потребуется инициализированный монитор
    monitor = EmergencyMonitor()
    
    try:
        # Аналитик извлекает структуру
        analyst_result = await monitor.act_as_analyst(raw_text)
        
        # Скептик проверяет
        is_valid = await monitor.act_as_skeptic(raw_text, str(analyst_result))
        
        if not is_valid:
            await wait_msg.edit_text("❌ Заявка отклонена ИИ: Текст не похож на запрос реальной помощи БПЛА.")
            return

        # Сохраняем в БД в статусе pending
        async with async_session() as session:
            alert = EmergencyAlert(
                reporter_id=user_id,
                city=analyst_result.get("location", "Неизвестно"),
                problem_type=analyst_result.get("incident_type", "Другое"),
                required_equipment=analyst_result.get("required_drone_type", "Любой БПЛА"),
                raw_text=raw_text,
                ai_summary=str(analyst_result),
                status="pending"
            )
            session.add(alert)
            await session.commit()
            await session.refresh(alert)
            alert_id = alert.id

        await wait_msg.edit_text(
            f"✅ Ваша заявка #{alert_id} успешно обработана ИИ и передана модератору на проверку.\n\n"
            f"📍 Локация: {analyst_result.get('location')}\n"
            f"🚁 Оборудование: {analyst_result.get('required_drone_type')}"
        )
        
        # Уведомляем админов (эту часть доделаем позже)
        # from bot.handlers.admin import notify_admins_about_alert
        # await notify_admins_about_alert(wait_msg.bot, alert_id)
        
    except Exception as e:
        logger.error(f"MoMoA Error: {e}")
        await wait_msg.edit_text("⚠️ Ошибка сервера при анализе ИИ. Попробуйте позже.")
