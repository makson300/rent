import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db.base import async_session
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from db.models.listing import Listing
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

router = Router()
logger = logging.getLogger(__name__)

class SearchStates(StatesGroup):
    waiting_for_query = State()

@router.message(F.text == "🔍 Поиск")
@router.message(Command("search"))
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
        from db.models.user import User
        # Поиск по заголовку, описанию и городу
        stmt = (
            select(Listing)
            .join(User, Listing.user_id == User.id)
            .options(selectinload(Listing.photos), selectinload(Listing.user))
            .where(
                Listing.status == "active",
                User.is_banned == False
            )
            .where(
                or_(
                    Listing.title.icontains(query),
                    Listing.description.icontains(query),
                    Listing.city.icontains(query)
                )
            )
            .order_by(Listing.is_promoted.desc(), Listing.created_at.desc())
            .limit(10)
        )
        
        result = await session.execute(stmt)
        listings = result.scalars().all()

    if not listings:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔔 Подписаться на поиск", callback_data=f"subscribe_search_{query}")]
        ])
        await message.answer(
            f"🤷‍♂️ По запросу «{query}» ничего не найдено.\n\n"
            f"Хотите получать уведомления, когда такие дроны появятся в базе?",
            reply_markup=kb
        )
    else:
        await message.answer(f"✅ Найдено {len(listings)} объявлений:")
        for l in listings[:5]:
            text = f"📦 <b>{l.title}</b>\n🏙 {l.city}\n💰 {l.price_list[:50] if l.price_list else 'Нет'}..."
            
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👤 Профиль продавца", callback_data=f"view_seller_{l.user_id}")],
                [InlineKeyboardButton(text="💬 Написать владельцу", url=f"tg://user?id={l.user.telegram_id}" if getattr(l, 'user', None) else f"https://t.me/share/url?url={l.contacts}")],
                [InlineKeyboardButton(text="🚨 Пожаловаться", callback_data=f"report_listing_{l.id}")]
            ])
            
            await message.answer(
                text,
                parse_mode="HTML",
                reply_markup=kb
            )

        if len(listings) > 5:
            await message.answer(f"<i>...и еще {len(listings) - 5} объявлений.</i>", parse_mode="HTML")
            
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔔 Следить за новыми", callback_data=f"subscribe_search_{query}")]
        ])
        await message.answer(f"Хотите получать уведомления о новых объявлениях по запросу «{query}»?", reply_markup=kb)
    
    await state.clear()

@router.callback_query(F.data.startswith("subscribe_search_"))
async def process_search_subscription(callback: types.CallbackQuery):
    query = callback.data.split("_", 2)[2]
    
    from db.base import async_session
    from db.models.search_sub import SearchSubscription
    from db.crud.user import get_user
    
    async with async_session() as session:
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Ошибка: пользователь не найден.", show_alert=True)
            return
            
        new_sub = SearchSubscription(
            user_id=user.id,
            keyword=query
        )
        session.add(new_sub)
        await session.commit()
        
    await callback.answer()
    
    text = callback.message.text or ""
    await callback.message.edit_text(
        text + f"\n\n✅ <b>Вы подписались на поиск:</b> «{query}»\n"
        f"Как только появится новое объявление, мы пришлем вам уведомление!",
        parse_mode="HTML",
        reply_markup=None
    )
