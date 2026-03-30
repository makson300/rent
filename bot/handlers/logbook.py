import logging
import io
import re
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select

from db.base import async_session
from db.models.user import User

router = Router()
logger = logging.getLogger(__name__)

class LogbookStates(StatesGroup):
    waiting_for_file = State()

@router.callback_query(F.data == "logbook_menu")
async def logbook_menu(callback: types.CallbackQuery, state: FSMContext):
    """Меню Цифровой Летной Книжки (LogBook)"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📁 Загрузить файл телеметрии", callback_data="logbook_upload")],
        [InlineKeyboardButton(text="🔙 Назад в профиль", callback_data="back_to_profile")]
    ])
    
    await callback.message.edit_text(
        "✈️ <b>Цифровая Лётная Книжка (LogBook AI)</b>\n\n"
        "Загружайте сюда файлы телеметрии с пультов (DJI, Autel, etc. форматы <code>.txt</code> или <code>.csv</code>).\n"
        "Наш ИИ-агент <b>MoMoA</b> проверит оригинальность файла, чтобы отсеять накрутки, "
        "и автоматически зачислит летные часы в ваш Рейтинг Пилота.\n\n"
        "<i>Чем больше у вас подтвержденных часов, тем выше вы в выдаче у Заказчиков!</i>",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_profile")
async def back_to_profile_redirect(callback: types.CallbackQuery, state: FSMContext):
    # To return to profile we can just send the text '👤 Профиль' to trigger the handler
    await callback.message.delete()
    from bot.handlers.profile import show_profile
    await show_profile(callback.message)
    await callback.answer()

@router.callback_query(F.data == "logbook_upload")
async def start_logbook_upload(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📎 Пожалуйста, отправьте полётный лог в формате <b>.TXT</b> или <b>.CSV</b> как документ.\n\n"
        "<i>Убедитесь, что файл является оригинальным экспортом из приложения (например, DJI Fly или Airdata).</i>",
        parse_mode="HTML"
    )
    await state.set_state(LogbookStates.waiting_for_file)
    await callback.answer()

@router.message(LogbookStates.waiting_for_file, F.document)
async def process_logbook_file(message: types.Message, state: FSMContext):
    doc = message.document
    
    if not doc.file_name.lower().endswith(('.txt', '.csv')):
        await message.answer("❌ Поддерживаются только форматы <b>.txt</b> и <b>.csv</b>.", parse_mode="HTML")
        return
        
    await message.answer("⏳ <i>MoMoA AI анализирует файл на подлинность и высчитывает налет...</i>", parse_mode="HTML")
    await state.clear()
    
    try:
        # Download file
        file_io = io.BytesIO()
        await message.bot.download(doc, destination=file_io)
        file_io.seek(0)
        file_content = file_io.read().decode('utf-8', errors='ignore')
        
        # Analyze using MoMoA
        from bot.config import GEMINI_API_KEY
        if not GEMINI_API_KEY:
            await message.answer("❌ Сервис MoMoA недоступен (не настроен API_KEY).")
            return
            
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1alpha'})
        
        # Taking a chunk of the file if it's too large to save tokens
        chunk = file_content[:15000]
        
        prompt = (
            "SYSTEM ROLE: You are an anti-fraud agent & flight data parser for a drone marketplace (MoMoA). "
            "Analyze the following chunk of a drone flight log (TXT/CSV). "
            "Determine the total flight time in HOURS (e.g., 0.5 for 30 mins). "
            "Also look for signs of manual text manipulation (fake logs). If the log looks completely synthetic and fake, reject it.\n\n"
            f"FILE NAME: {doc.file_name}\n"
            f"CONTENT CHUNK:\n\n{chunk}\n\n"
            "OUTPUT strictly a JSON format: "
            '{"is_authentic": true/false, "flight_hours": float, "reason": "brief explanation"}'
        )
        
        response = await client.aio.models.generate_content(
            model='gemini-1.5-pro',
            contents=prompt,
        )
        
        text = response.text.strip()
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        
        import json
        result = json.loads(text)
        
        if not result.get("is_authentic", False):
            await message.answer(
                f"🚨 <b>ОТКЛОНЕНО (Анти-Фрод MoMoA)</b>\n\n"
                f"Мы обнаружили признаки подделки файла или некорректный формат:\n"
                f"<i>{result.get('reason', 'Не удалось верифицировать оригинальность.')}</i>",
                parse_mode="HTML"
            )
            return
            
        detected_hours = float(result.get("flight_hours", 0.0))
        if detected_hours <= 0:
            await message.answer("❌ Файл прошел проверку, но летное время оказалось равно 0 или не найдено.")
            return
            
        # Update user
        async with async_session() as session:
            user = await session.get(User, message.from_user.id)
            if getattr(user, "is_deleted", False): # just a safe check
                return
                
            current = user.verified_flight_hours or 0.0
            user.verified_flight_hours = current + detected_hours
            
            # Fleet wear and tear logic
            from db.models.fleet import FleetDrone, FleetBattery
            
            drones_res = await session.execute(select(FleetDrone).where(FleetDrone.user_id == user.id))
            first_drone = drones_res.scalars().first()
            if first_drone:
                first_drone.total_flight_hours += detected_hours
                
            bats_res = await session.execute(select(FleetBattery).where(FleetBattery.user_id == user.id))
            first_battery = bats_res.scalars().first()
            if first_battery:
                # 1 flight log file roughly equals 1 battery cycle for MVP
                first_battery.charge_cycles += 1
                
            await session.commit()
            new_total = user.verified_flight_hours
            
            drone_text = f"\n🔧 <b>Обновлен Ангар:</b>\n"
            if first_drone:
                drone_text += f"Дрон '{first_drone.name}' износ: +{detected_hours:.2f} ч.\n"
            if first_battery:
                drone_text += f"АКБ '{first_battery.name}' циклы: +1\n"
                
        await message.answer(
            f"✅ <b>ФАЙЛ ВЕРИФИЦИРОВАН!</b>\n\n"
            f"Найдено время: <b>{detected_hours:.2f} ч.</b>\n"
            f"Общий подтвержденный налет: <b>{new_total:.2f} ч.</b>\n"
            f"{drone_text if (first_drone or first_battery) else ''}\n"
            f"Ваш рейтинг доверия в каталоге автоматически повышен 📈.",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"MoMoA LogBook error: {e}")
        await message.answer("❌ Произошла ошибка при анализе файла. Попробуйте еще раз.")
