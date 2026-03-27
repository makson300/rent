import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db.base import async_session
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from db.models.listing import Listing
from bot.keyboards.catalog import get_listing_detail_kb

router = Router()
logger = logging.getLogger(__name__)

class SearchStates(StatesGroup):
    waiting_for_query = State()

@router.message(F.text == "🔍 Поиск")
@router.message(commands=["search"])
async def start_search(message: types.Message, state: FSMContext):
    await state.set_state(SearchStates.waiting_for_query)
    await message.answer("🔎 Введите ключевое слово для поиска (например, модель дрона или город):")

@router.message(SearchStates.waiting_for_query)
async def process_search(message: types.Message, state: FSMContext):
    query = message.text.strip()
    if len(query) < 2:
        await message.answer("⚠️ Запрос слишком короткий. Введите хотя бы 2 символа.")
        return

    async with async_session() as session:
        # Поиск по заголовку, описанию и городу
        stmt = (
            select(Listing)
            .options(selectinload(Listing.photos))
            .where(
                or_(
                    Listing.is_approved == True,
                    Listing.status == "active"
                )
            )
            .where(
                or_(
                    Listing.title.icontains(query),
                    Listing.description.icontains(query),
                    Listing.city.icontains(query)
                )
            )
            .order_by(Listing.created_at.desc())
            .limit(10)
        )
        
        result = await session.execute(stmt)
        listings = result.scalars().all()

    if not listings:
        await message.answer(f"🤷‍♂️ По запросу «{query}» ничего не найдено.")
    else:
        await message.answer(f"✅ Найдено {len(listings)} объявлений:")
        for l in listings[:5]:
            text = f"📦 <b>{l.title}</b>\n🏙 {l.city}\n💰 {l.price_list[:50] if l.price_list else 'Нет'}..."
            await message.answer(
                text,
                parse_mode="HTML",
                reply_markup=get_listing_detail_kb(l.id)
            )

        if len(listings) > 5:
            await message.answer(f"<i>...и еще {len(listings) - 5} объявлений.</i>", parse_mode="HTML")
    
    await state.clear()
