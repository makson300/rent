import logging
import io
import re
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from bot.keyboards.main_menu import get_main_menu

router = Router()
logger = logging.getLogger(__name__)

class AIVisionStates(StatesGroup):
    waiting_for_photo = State()

@router.message(F.text == "👁‍🗨 AI-Инспекция")
async def ai_vision_start(message: types.Message, state: FSMContext):
    """Начало работы с модулем AI Vision"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "👁‍🗨 <b>Модуль AI-Инспекции (MoMoA Vision)</b>\n\n"
        "Отправьте мне <b>фотографию</b> (например, кадастровая аэросъемка, инспекция крыши, тепловизия труб).\n"
        "Пишите комментарий вместе с фото, если нужно сделать акцент на чем-то конкретном.\n\n"
        "<i>Наш ИИ проведет анализ, найдет дефекты/размеры и выдаст готовый рабочий отчет для вашего Заказчика.</i>",
        parse_mode="HTML",
        reply_markup=kb
    )
    await state.set_state(AIVisionStates.waiting_for_photo)

@router.message(F.text == "Отмена", AIVisionStates.waiting_for_photo)
async def ai_vision_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ AI-Инспекция отменена.", reply_markup=get_main_menu())

@router.message(AIVisionStates.waiting_for_photo, F.photo)
async def process_ai_vision_photo(message: types.Message, state: FSMContext):
    """Обработка фото мультимодальной моделью Gemini 1.5 Pro"""
    await state.clear()
    
    status_msg = await message.answer(
        "⏳ <i>MoMoA сканирует снимок и составляет инспекционный отчет...</i>",
        parse_mode="HTML"
    )
    
    try:
        from bot.config import GEMINI_API_KEY
        if not GEMINI_API_KEY:
            await status_msg.edit_text("❌ Сервис MoMoA Vision недоступен (не настроен API_KEY).")
            return
            
        from google import genai
        from google.genai import types as genai_types
        client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1alpha'})
        
        # Download highest resolution photo
        photo = message.photo[-1]
        file_io = io.BytesIO()
        await message.bot.download(photo, destination=file_io)
        file_data = file_io.getvalue()
        
        user_comment = message.caption or "Общий анализ объекта"
        
        prompt = (
            "SYSTEM ROLE: You are MoMoA Vision, an expert aviation data analyst and inspector. "
            "Examine this drone aerial photograph. "
            f"USER DIRECTIVE: {user_comment}\n\n"
            "TASK: Generate a professional, highly structured 'Aerial Inspection Report' in Russian. "
            "Included sections:\n"
            "1. Объект инспекции (описание того, что на фото)\n"
            "2. Выявленные аномалии / дефекты (трещины, ржавчина, скопления техники и т.д.)\n"
            "3. Количественная оценка (если применимо - количество машин, площадь крыши, etc.)\n"
            "4. Рекомендации для заказчика.\n"
            "Format the output elegantly using Telegram HTML styles (b, i, code)."
        )
        
        response = await client.aio.models.generate_content(
            model='gemini-1.5-pro',
            contents=[
                prompt,
                genai_types.Part.from_bytes(data=file_data, mime_type="image/jpeg")
            ]
        )
        
        report_text = response.text
        
        # Send back to user
        await status_msg.delete()
        await message.answer(
            f"📄 <b>ГОТОВЫЙ AI-ОТЧЕТ ИНСПЕКЦИИ</b>\n\n"
            f"{report_text}\n\n"
            f"<i>💡 Вы можете скопировать этот текст и переслать вашему B2B Заказчику!</i>",
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
        
    except Exception as e:
        logger.error(f"MoMoA Vision error: {e}")
        await status_msg.edit_text("❌ Произошла ошибка при анализе изображения.")
