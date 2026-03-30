import io
import logging
from db.crud.listing import get_listings_by_filter
from bot.config import GEMINI_API_KEY
import asyncio

try:
    from google import genai
    from google.genai import types
    has_genai = True
except ImportError:
    has_genai = False

logger = logging.getLogger(__name__)

async def create_b2b_proposal(session, tender_title: str, tender_desc: str) -> tuple[str, io.BytesIO]:
    """
    Ищет "По запросу (B2B)" объявления в базе, фильтрует их ИИ (опционально) 
    и генерирует красивое Коммерческое Предложение в текстовом файле.
    """
    # 1. Запрашиваем последние объявления B2B (можно фильтровать по категории)
    listings = await get_listings_by_filter(session)
    listings = listings[:20]
    b2b_listings = [lst for lst in listings if lst.price_list and "По запросу" in lst.price_list]
    
    if not b2b_listings:
        return "В базе Горизонт пока нет актуальных B2B-предложений для этого тендера.", None
        
    # Форматируем выборку для ИИ
    catalog_dump = ""
    for idx, l in enumerate(b2b_listings[:10], start=1):
        catalog_dump += f"Лот {idx}: {l.title}\nОписание: {l.description[:200]}...\nЛокация: {l.city}\nПродавец: {'Магазин' if l.seller_type == 'store' else 'Частное лицо'}\n---\n"
        
    if not has_genai or not GEMINI_API_KEY:
        # Fallback без AI
        report_text = f"ТЕНДЕРНОЕ ПРЕДЛОЖЕНИЕ\nПод: {tender_title}\n\nНайдено оборудования:\n{catalog_dump}"
        file_io = io.BytesIO(report_text.encode('utf-8'))
        file_io.name = "B2B_Commercial_Proposal.txt"
        return f"✅ Найдено {len(b2b_listings)} предложений. (AI-генерация недоступна)", file_io
        
    # 3. Интеграция Gemini
    try:
        client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1alpha'})
        model_name = 'gemini-1.5-pro'
        
        prompt = (
            "Сгенерируй профессиональное Коммерческое Предложение (КП) от лица Национальной Экосистемы 'Горизонт'.\n"
            f"Тема тендера заказчика: {tender_title}\n"
            f"Описание требований: {tender_desc}\n\n"
            "Доступное оборудование в базе 'Горизонт':\n"
            f"{catalog_dump}\n\n"
            "Твоя задача:\n"
            "Выбери наиболее подходящее оборудование из списка. "
            "Составь официальное, строго структурированное коммерческое предложение, используя деловой стиль и формат (Кому, От кого, Суть предложения, Список оборудования с комментариями почему оно подходит, и Заключение). "
            "Цены не указывай, пиши 'Согласно корпоративному прайсу' или 'По запросу'."
        )
        
        response = await client.aio.models.generate_content(
            model=model_name,
            contents=prompt
        )
        
        final_text = response.text
        
        file_io = io.BytesIO(final_text.encode('utf-8'))
        file_io.name = f"Коммерческое_Предложение_{tender_title[:10]}.txt"
        
        return f"✅ Подготовлено AI-коммерческое предложение на основе {len(b2b_listings)} доступных единиц техники по запросу.", file_io
        
    except Exception as e:
        logger.error(f"Error generating proposal: {e}")
        report_text = f"ТЕНДЕРНОЕ ПРЕДЛОЖЕНИЕ\nПод: {tender_title}\n\nНайдено оборудования:\n{catalog_dump}"
        file_io = io.BytesIO(report_text.encode('utf-8'))
        file_io.name = "B2B_Commercial_Proposal_Error.txt"
        return "⚠️ Произошла ошибка генерации ИИ, отправляем сырую выгрузку.", file_io
