import logging
from aiogram import Router, types, F
from db.base import async_session
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from db.models.listing import Listing

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text.startswith("/search"))
async def search_listings(message: types.Message):
    """Поиск объявлений по ключевым словам"""
    query_text = message.text.replace("/search", "").strip()

    if not query_text:
        await message.answer("🔍 Введите поисковый запрос после команды /search.\nПример: `/search Mavic 3`", parse_mode="Markdown")
        return

    async with async_session() as session:
        # Поиск по заголовку или описанию
        stmt = (
            select(Listing)
            .options(selectinload(Listing.photos))
            .where(Listing.status == "active")
            .where(
                or_(
                    Listing.title.ilike(f"%{query_text}%"),
                    Listing.description.ilike(f"%{query_text}%")
                )
            )
            .order_by(Listing.created_at.desc())
        )
        result = await session.execute(stmt)
        listings = result.scalars().all()

    if not listings:
        await message.answer(f"😔 По запросу «{query_text}» ничего не найдено.")
        return

    await message.answer(f"🔍 Результаты поиска по запросу «{query_text}» ({len(listings)}):")

    # Показываем результаты (здесь можно добавить пагинацию, но для начала выведем список)
    for l in listings[:5]: # Ограничим до 5 для начала
        text = f"📦 <b>{l.title}</b>\n🏙 {l.city}\n💰 {l.price_list[:50]}..."
        await message.answer(text, parse_mode="HTML")

    if len(listings) > 5:
        await message.answer(f"<i>...и еще {len(listings) - 5} объявлений.</i>", parse_mode="HTML")
