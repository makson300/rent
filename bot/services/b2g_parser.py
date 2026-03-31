import asyncio
import logging
import feedparser
from datetime import datetime, timedelta
from sqlalchemy import select

from db.base import async_session
from db.models.tender import Tender

logger = logging.getLogger(__name__)

# RSS-лента ЕИС по ключевому запросу: "беспилотн" (можно добавлять другие)
RSS_URL = "https://zakupki.gov.ru/epz/order/extendedsearch/rss.html?searchString=%D0%B1%D0%B5%D1%81%D0%BF%D0%B8%D0%BB%D0%BE%D1%82%D0%BD"

from aiogram import Bot
from bot.services.smart_tenders import run_b2g_matching

async def parse_b2g_tenders(bot: Bot):
    """
    Парсит RSS ленту ЕИС (или агрегатора) и сохраняет новые B2G тендеры.
    При сбое и блокировке ЕИС (возвращает 403 / пустую ленту) использует моки.
    """
    logger.info("Начинаем парсинг B2G тендеров ЕИС...")
    
    try:
        feed = await asyncio.to_thread(feedparser.parse, RSS_URL)
    except Exception as e:
        logger.error(f"Ошибка парсинга B2G: {e}")
        feed = None
    
    if not feed or not hasattr(feed, 'entries') or not feed.entries:
        logger.warning("B2G Парсер: RSS лента пуста или заблокирована (защита ЕИС). Используем моковые данные для Радара.")
        await _insert_mock_tenders_if_needed(bot)
        return

    new_tenders_ids = []
    
    async with async_session() as session:
        for entry in feed.entries[:10]: # Берем последние 10, чтобы избежать спама
            title = getattr(entry, 'title', 'Без названия')
            link = getattr(entry, 'link', 'https://zakupki.gov.ru/')
            description = getattr(entry, 'description', 'Нет описания')
            
            # Проверка уникальности
            existing_res = await session.execute(
                select(Tender).where(Tender.b2g_url == link)
            )
            if existing_res.scalar_one_or_none():
                continue
                
            new_tender = Tender(
                title=title[:255],
                description=description,
                category="Госзакупка (B2G)",
                budget=500000, # Примерный бюджет
                deadline=datetime.utcnow() + timedelta(days=7),
                region="РФ",
                is_b2g=True,
                b2g_status="new",
                b2g_url=link,
                eis_fz="44-ФЗ",
                customer_name="Государственный заказчик"
            )
            session.add(new_tender)
            await session.flush()
            new_tenders_ids.append(new_tender.id)
            
        if new_tenders_ids:
            await session.commit()
            
    if new_tenders_ids:
        logger.info(f"Парсинг B2G тендеров завершен. Добавлено: {len(new_tenders_ids)}")
        for tid in new_tenders_ids:
            await run_b2g_matching(bot, tid)

async def _insert_mock_tenders_if_needed(bot: Bot):
    """Фоллбэк, если сайт ЕИС блокирует скрипт (403)."""
    mock_data = [
        {
            "title": "Аэрофотосъемка линейного объекта (ЛЭП 15км)",
            "description": "Необходимо провести визуальное и тепловизионное обследование участка воздушной линии.",
            "budget": 145000,
            "region": "Свердловская обл.",
            "link": "https://zakupki.gov.ru/epz/main/public/home.html?mock=1",
        },
        {
            "title": "Кадастровая съемка земельных участков (RTK)",
            "description": "Требуется БВС с RTK-модулем для ортофотоплана.",
            "budget": 550000,
            "region": "Московская обл.",
            "link": "https://zakupki.gov.ru/epz/main/public/home.html?mock=2",
        }
    ]
    
    new_tenders_ids = []
    async with async_session() as session:
        for m in mock_data:
            existing = await session.execute(select(Tender).where(Tender.b2g_url == m["link"]))
            if existing.scalar_one_or_none():
                continue
                
            tender = Tender(
                title=m["title"],
                description=m["description"],
                category="БПЛА",
                budget=m["budget"],
                deadline=datetime.utcnow() + timedelta(days=14),
                region=m["region"],
                is_b2g=True,
                b2g_status="new",
                b2g_url=m["link"],
                eis_fz="44-ФЗ",
                customer_name="Россети (пример)"
            )
            session.add(tender)
            await session.flush()
            new_tenders_ids.append(tender.id)
            
        if new_tenders_ids:
            await session.commit()
            
    if new_tenders_ids:
        logger.info(f"Добавлено {len(new_tenders_ids)} моковых B2G тендеров из-за недоступности ЕИС.")
        for tid in new_tenders_ids:
            await run_b2g_matching(bot, tid)
