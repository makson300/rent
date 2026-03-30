import aiohttp
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models.job import Job
from db.models.user import User
from db.models.listing import Listing
from db.models.category import Category
from aiogram import Bot

logger = logging.getLogger(__name__)

HH_API_URL = "https://api.hh.ru/vacancies"

async def fetch_hh_vacancies():
    async with aiohttp.ClientSession() as session:
        params = {
            "text": 'БПЛА OR "пилот дрона" OR "оператор дрона" OR "агропилот" OR "агродрон"',
            "area": "113", # Россия
            "per_page": 20,
            "order_by": "publication_time"
        }
        headers = {
            "User-Agent": "Gorizont-Bot/1.0 (admin@skyrent.pro)"
        }
        try:
            async with session.get(HH_API_URL, params=params, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("items", [])
                else:
                    logger.error(f"HH.ru API Error: {resp.status}")
                    return []
        except Exception as e:
            logger.error(f"Failed to fetch from HH: {e}")
            return []

async def process_and_save_vacancies(bot: Bot, db_session: AsyncSession):
    """Fetches HH vacancies, saves them to DB, and dispatches push notifications."""
    
    # Решение проблемы NOT NULL для employer_id в существующей SQLite базе:
    # Создадим или получим системного пользователя HeadHunter (id=0)
    hh_user = await db_session.scalar(select(User).where(User.telegram_id == 0))
    if not hh_user:
        try:
            hh_user = User(telegram_id=0, first_name="HeadHunter", username="hh_ru", role="admin")
            db_session.add(hh_user)
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            
    items = await fetch_hh_vacancies()
    if not items:
        return 0
        
    new_jobs_count = 0
    added_jobs = []
    
    for item in items:
        ext_id = f"hh_{item['id']}"
        # Проверка на существование в базе
        exists = await db_session.scalar(select(Job).where(Job.external_id == ext_id))
        if exists:
            continue
            
        title = item.get("name", "Без названия")
        area = item.get("area", {}).get("name", "Неизвестно")
        url = item.get("alternate_url", "")
        
        salary_dict = item.get("salary")
        if salary_dict:
            from_s = salary_dict.get("from")
            to_s = salary_dict.get("to")
            curr = salary_dict.get("currency", "RUR")
            if from_s and to_s:
                budget = f"От {from_s} до {to_s} {curr}"
            elif from_s:
                budget = f"От {from_s} {curr}"
            elif to_s:
                budget = f"До {to_s} {curr}"
            else:
                budget = "По результатам собеседования"
        else:
            budget = "По результатам собеседования"
            
        snippet = item.get("snippet", {})
        req = snippet.get("requirement", "") or ""
        resp = snippet.get("responsibility", "") or ""
        desc = (f"Требования: {req}\nЗадачи: {resp}").replace("<highlighttext>", "").replace("</highlighttext>", "")
        
        new_job = Job(
            employer_id=0, # Привязка к системному пользователю
            title=title,
            description=desc[:1000] if desc else "Смотрите подробности по ссылке",
            category="Операторы БПЛА",
            city=area,
            budget=budget,
            status="active",
            source_url=url,
            external_id=ext_id
        )
        db_session.add(new_job)
        added_jobs.append(new_job)
        new_jobs_count += 1
        
    await db_session.commit()
    
    # Рассылка 
    for job in added_jobs:
        await dispatch_hh_job(bot, db_session, job)
        
    return new_jobs_count

async def dispatch_hh_job(bot: Bot, session: AsyncSession, job: Job):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    stmt = (
        select(Listing)
        .join(Category)
        .where(Category.name == "Операторы")
        .where(Listing.status == "active")
    )
    if job.city and job.city != "Неизвестно":
        stmt = stmt.where(Listing.city.ilike(f"%{job.city}%"))
        
    result = await session.execute(stmt)
    listings = result.scalars().all()
    
    notified = set()
    for l in listings:
        notified.add(l.user_id)
        
    if not notified:
        return
        
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Откликнуться", callback_data=f"job_view_{job.id}")]
    ])
    
    text = (
        f"⚡️ <b>НОВАЯ ВАКАНСИЯ В Г. {job.city.upper()}!</b>\n\n"
        f"<b>Должность:</b> {job.title}\n"
        f"<b>Зарплата:</b> {job.budget}\n\n"
        f"<i>Агрегатор 'Горизонт' транслирует вакансию с hh.ru</i>"
    )
    
    for uid in notified:
        user = await session.get(User, uid)
        if user and user.telegram_id:
            try:
                await bot.send_message(user.telegram_id, text, parse_mode="HTML", reply_markup=kb)
            except Exception:
                pass
