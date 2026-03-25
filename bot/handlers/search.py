import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from db.base import async_session
from db.models.listing import Listing
from bot.keyboards import get_main_menu

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("search"))
async def cmd_search(message: types.Message):
    """Инструкция по поиску"""
    await message.answer(
        "🔍 <b>Умный поиск</b>\n\n"
        "Чтобы найти оборудование, введите запрос после команды. Например:\n"
        "<code>/search dji mavic</code>\n"
        "<code>/search софтбокс москва</code>",
        parse_mode="HTML"
    )

@router.message(F.text.startswith("/search "))
async def process_search(message: types.Message):
    """Выполнение поиска по ключевым словам"""
    query_text = message.text.replace("/search ", "").strip()
    if not query_text:
        await message.answer("⚠️ Введите запрос для поиска.")
        return

    async with async_session() as session:
        # Поиск по заголовку, описанию и городу
        stmt = (
            select(Listing)
            .options(selectinload(Listing.photos))
            .where(
                Listing.status == "active",
                or_(
                    Listing.title.icontains(query_text),
                    Listing.description.icontains(query_text),
                    Listing.city.icontains(query_text)
                )
            )
            .limit(10)
        )
        result = await session.execute(stmt)
        listings = result.scalars().all()

    if not listings:
        await message.answer(f"😔 По запросу «{query_text}» ничего не найдено.")
        return

    await message.answer(f"🔍 <b>Результаты поиска ({len(listings)}):</b>", parse_mode="HTML")

    for l in listings:
        text = (
            f"📦 <b>{l.title}</b>\n"
            f"🏙 {l.city}\n\n"
            f"💰 {l.price_list}\n"
            f"📞 {l.contacts}"
        )
        if l.photos:
            await message.answer_photo(l.photos[0].photo_id, caption=text[:1024], parse_mode="HTML")
        else:
            await message.answer(text, parse_mode="HTML")
