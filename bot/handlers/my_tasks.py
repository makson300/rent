import logging
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, or_
from db.base import async_session
from db.models.job import Job
from db.models.user import User

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "🚁 Мои задачи")
async def show_my_tasks(message: types.Message):
    """Отображение текущих активных задач (где пользователь - пилот или заказчик)"""
    user_id = message.from_user.id
    
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == user_id))
        if not user:
            await message.answer("Пользователь не найден.")
            return

        # Найти все In Progress задачи, где юзер = пилот ИЛИ заказчик
        jobs = await session.scalars(
            select(Job).where(
                (Job.status == "in_progress") & 
                ((Job.pilot_id == user.id) | (Job.employer_id == user_id))
            ).order_by(Job.id.desc())
        )
        jobs = jobs.all()

        if not jobs:
            await message.answer(
                "📋 <b>Ваши текущие задачи:</b>\n\nУ вас пока нет активных задач в работе.",
                parse_mode="HTML"
            )
            return

        await message.answer("📋 <b>Ваши активные задачи в работе:</b>", parse_mode="HTML")

        for job in jobs:
            is_pilot = (job.pilot_id == user.id)
            role = "Исполнитель (Пилот)" if is_pilot else "Заказчик"
            
            text = (
                f"🔹 <b>Задача #{job.id}:</b> {job.title}\n"
                f"<b>Ваша роль:</b> {role}\n"
                f"<b>Город:</b> {job.city}\n"
                f"<b>Бюджет:</b> {job.budget}\n"
            )
            
            kb_buttons = []
            if is_pilot:
                kb_buttons.append([InlineKeyboardButton(text="📄 Генерация заявки ОрВД (ИВП)", callback_data=f"generate_orvd_{job.id}")])
                kb_buttons.append([InlineKeyboardButton(text="✅ Завершить работу", callback_data=f"finish_job_{job.id}")])
                if job.employer_id:
                    kb_buttons.append([InlineKeyboardButton(text="💬 Написать Заказчику", url=f"tg://user?id={job.employer_id}")])
            else:
                kb_buttons.append([InlineKeyboardButton(text="✅ Принять результат", callback_data=f"accept_job_{job.id}")])

            kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
            await message.answer(text, parse_mode="HTML", reply_markup=kb)

@router.callback_query(F.data.startswith("generate_orvd_"))
async def process_generate_orvd(callback: types.CallbackQuery):
    """Сборка шаблона заявления на Местный режим для ЕС ОрВД"""
    job_id = int(callback.data.split("_")[2])
    
    async with async_session() as session:
        job = await session.scalar(select(Job).where(Job.id == job_id))
        if not job:
            await callback.answer("Заказ не найден.", show_alert=True)
            return

    template = (
        f"📝 <b>Шаблон Заявки на Местный Режим (ИВП)</b>\n\n"
        f"<i>Скопируйте этот текст для отправки через систему SPPI (ЗЦ ЕС ОрВД):</i>\n\n"
        f"<code>"
        f"(SHR-UAS\n"
        f"-ZZZZ0000\n"
        f"-M0000/M000\n"
        f"-Z {job.city.upper()} РАДИУС 1 КМ\n"
        f"-0000/0000\n"
        f"-ПОЛЕТЫ БПЛА ДЛЯ {job.title.upper()}\n"
        f"В ЦЕЛЯХ АЭРОФОТОСЪЕМКИ.\n"
        f"ВЫСОТА ДО 150М АГЛ.\n"
        f"ОПЕРАТОР: {callback.from_user.first_name.upper()}\n"
        f"ТЕЛ: [Укажите Ваш Телефон])"
        f"</code>\n\n"
        f"ℹ️ Укажите точные координаты вместо ZZZZ и время по UTC."
    )
    
    await callback.message.answer(template, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("finish_job_") | F.data.startswith("accept_job_"))
async def process_job_completion(callback: types.CallbackQuery):
    """Завершение работы (имитация)"""
    action = callback.data.split("_")[0]
    job_id = int(callback.data.split("_")[2])
    
    async with async_session() as session:
        job = await session.scalar(select(Job).where(Job.id == job_id))
        if not job:
            await callback.answer("Заказ не найден.", show_alert=True)
            return

        # Просто закрываем задачу для демо-стенда MVP
        job.status = "completed"
        
        employer_id = job.employer_id
        await session.commit()
    
    if action == "finish_job":
        try:
            await callback.message.edit_text(callback.message.html_text + "\n\n✅ <b>Статус:</b> Завершена пилотом.", parse_mode="HTML")
        except Exception:
            pass
        await callback.answer("Работа сдана. Ожидайте подтверждения заказчика.", show_alert=True)
        try:
            await callback.bot.send_message(
                chat_id=employer_id, 
                text=f"✅ <b>Пилот сдал работу по заказу #{job_id}!</b>\nПожалуйста, проверьте и примите результаты в разделе «Мои задачи».", 
                parse_mode="HTML"
            )
        except Exception:
            pass
    else:
        try:
            await callback.message.edit_text(callback.message.html_text + "\n\n✅ <b>Статус:</b> Принята заказчиком.", parse_mode="HTML")
        except Exception:
            pass
        await callback.answer("Работа принята. Средства (Безопасная сделка) переведены пилоту.", show_alert=True)
