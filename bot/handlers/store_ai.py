import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.keyboards.main_menu import get_main_menu
from db.base import async_session
from db.crud.listing import get_listings_by_filter
import os

try:
    from google import genai
    has_genai = True
except ImportError:
    has_genai = False

router = Router()
logger = logging.getLogger(__name__)

class StoreAIStates(StatesGroup):
    waiting_for_query = State()

@router.message(F.text == "🛍 Магазин")
async def store_main(message: types.Message, state: FSMContext):
    """Вход в Умный Магазин с ИИ-консультантом"""
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Полный каталог", web_app=types.WebAppInfo(url="https://skyrent.pro/webapp/catalog"))]
    ])
    
    await message.answer(
        "🛍 <b>Умный Магазин оборудования</b>\n\n"
        "Я — ваш ИИ-ассистент Горизонта. Напишите мне свободным текстом, что вы ищете?\n\n"
        "<i>Например: «Нужен тепловизор для поиска людей от 50 тыс руб» или «Подберите дрон для облета ЛЭП»</i>",
        parse_mode="HTML",
        reply_markup=kb
    )
    await state.set_state(StoreAIStates.waiting_for_query)

@router.message(StoreAIStates.waiting_for_query, F.text)
async def process_store_query(message: types.Message, state: FSMContext):
    
    # Cancel if user presses another menu button
    if message.text in ["🔍 Поиск", "🔍 Арендовать", "🛍 Магазин", "🎓 Обучение", "📋 Мои объявления", "🚁 Мои задачи", "📄 Договор ИИ", "👤 Профиль", "🆘 ЧП", "🎬 Операторы", "📩 Обратная связь", "📝 Разместить Вакансию"]:
        await state.clear()
        return
        
    wait_msg = await message.answer("⏳ <i>Изучаю базу B2B/B2C складов... подбираю для вас лучшие варианты...</i>", parse_mode="HTML")
    
    # Загружаем базу объявлений
    async with async_session() as session:
        all_listings = await get_listings_by_filter(session)
        all_listings = all_listings[:50]
        
    if not all_listings:
        await wait_msg.delete()
        await message.answer("Извините, база товаров пока пуста.", reply_markup=get_main_menu())
        await state.clear()
        return

    # Готовим каталог
    catalog_dump = ""
    for idx, l in enumerate(all_listings[:30], start=1):
        price = l.price_list if l.price_list else f"{l.price_per_day} ₽/день"
        catalog_dump += f"Лот [{idx}]: {l.title}\nЦена: {price}\nОп: {l.description[:100]}\nГород: {l.city}\n---\n"

    api_key = os.getenv("GEMINI_API_KEY")
    if not has_genai or not api_key:
        await wait_msg.delete()
        await message.answer("ИИ-консультант временно недоступен. Воспользуйтесь Полным каталогом.")
        await state.clear()
        return
        
    try:
        client = genai.Client(api_key=api_key)
        prompt = (
            "Ты — ИИ-продавец консультант платформы Горизонт.\n"
            f"Запрос клиента: {message.text}\n\n"
            "Доступные товары из базы:\n"
            f"{catalog_dump}\n\n"
            "Выбери 1-3 самых подходящих лота, опиши почему они подходят клиенту, "
            "укажи их Цену и Город. Будь вежлив. Обращайся к клиенту на Вы. "
            "Отформатируй текст красиво для Telegram (без markdown-кода, используй эмодзи)."
        )
        
        # Async call
        response = await client.aio.models.generate_content(
            model='gemini-1.5-pro',
            contents=prompt
        )
        
        await wait_msg.delete()
        await message.answer(
            f"🤖 <b>Ответ Консультанта:</b>\n\n{response.text}",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"AI Store error: {e}")
        await wait_msg.delete()
        await message.answer("Произошла ошибка при обращении к базе знаний. Попробуйте переформулировать запрос.")
        
    await state.clear()
