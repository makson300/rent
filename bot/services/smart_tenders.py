import logging
import json
import re
from sqlalchemy import select
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db.base import async_session
from db.models.user import User
from db.models.listing import Listing
from bot.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

MOCK_GOV_TENDER = {
    "title": "Оказание услуг по аэрофотосъемке объектов электросетевого хозяйства (ЛЭП-110кВ)",
    "description": "Исполнитель должен провести тепловизионное обследование 500 км воздушных линий. "
                   "Требуется беспилотное воздушное судно с подвешенным тепловизором (тепловизионной камерой) "
                   "и модулем RTK для точного позиционирования.",
    "budget": "1 500 000 ₽",
    "link": "https://zakupki.gov.ru/epz/order/notice/mock/12345"
}

async def extract_requirements(tender_text: str) -> list[str]:
    """Используем MoMoA для извлечения ключевых технических требований (железо) из ТЗ тендера."""
    if not GEMINI_API_KEY:
        # Fallback keyword logic
        return ["тепловизор", "rtk"]
        
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1alpha'})
        
        prompt = (
            "SYSTEM ROLE: You are MoMoA, an expert B2B drone tender analyst.\n"
            f"TENDER TEXT:\n{tender_text}\n\n"
            "TASK: Identify the mandatory drone equipment or technology required. "
            "Output ONLY a raw JSON list of simple Russian keywords (e.g. ['тепловизор', 'rtk', 'лидар']). "
            "Do not include markdown or explanations."
        )
        
        response = await client.aio.models.generate_content(
            model='gemini-1.5-pro',
            contents=prompt,
        )
        
        text = response.text.strip()
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        
        keywords = json.loads(text)
        if isinstance(keywords, list):
            return [str(k).lower() for k in keywords]
            
    except Exception as e:
        logger.error(f"MoMoA Tender Parsing Error: {e}")
        
    return ["тепловизор", "rtk"]

async def run_b2g_matching(bot: Bot, tender_id: int):
    """
    Симуляция кросс-матчинга: берем новый тендер, извлекаем требования,
    ищем пилотов с таким железом и делаем Push-уведомление (Smart Dispatch).
    """
    logger.info(f"Running B2G Smart Matching task for tender {tender_id}...")
    
    async with async_session() as session:
        from db.models.tender import Tender
        tender_res = await session.execute(select(Tender).where(Tender.id == tender_id))
        tender = tender_res.scalar_one_or_none()
        
        if not tender:
            return 0
            
        tender_full_text = f"{tender.title} {tender.description}"
        requirements = await extract_requirements(tender_full_text)
        
        logger.info(f"Tender requires: {requirements}")
        
        # 2. Ищем пилотов, чьи Listings содержат данные ключевые слова
        users_res = await session.execute(select(User))
        all_users = users_res.scalars().all()
        
        matched_users = []
        for user in all_users:
            if not user.telegram_id: continue
            
            # Получаем флот пилота
            listings_res = await session.execute(select(Listing).where(Listing.user_id == user.id))
            listings = listings_res.scalars().all()
            
            user_text = " ".join([f"{L.title} {L.description}".lower() for L in listings])
            
            # Ищем совпадения извлеченных ИИ требований и текста объявлений юзера
            match_score = sum(1 for req in requirements if req in user_text)
            
            if match_score > 0:
                matched_users.append(user)

        # 3. Отправляем пуши
        for user in matched_users:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎯 Подать отклик", url="https://45.12.5.177.nip.io/dashboard/tenders")]
            ])
            text = (
                f"🚨 <b>SMART B2G TENDER MATCH</b> 🚨\n\n"
                f"Вышел крупный Госконтракт, который <b>подходит</b> под ваше оборудование!\n\n"
                f"📌 <b>Заказ:</b> {tender.title}\n"
                f"💰 <b>Бюджет:</b> {tender.budget:,} ₽\n\n"
                f"<i>Срочно перейдите в Панель Управления и подайте отклик первым!</i>"
            )
            try:
                await bot.send_message(user.telegram_id, text, parse_mode="HTML", reply_markup=kb)
                logger.info(f"Sent B2G Tender Alert to {user.telegram_id}")
            except Exception as e:
                logger.warning(f"Failed to send alert to {user.telegram_id}: {e}")
                
    return len(matched_users)
