import logging
from aiogram import Router, types, F
from db.base import async_session
from db.models.subscription import SearchSubscription
from sqlalchemy import select, delete

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data == "search_wishlist")
async def show_wishlist_menu(callback: types.CallbackQuery):
    """Меню подписок на поиск"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать подписку", callback_data="wishlist_create")],
        [InlineKeyboardButton(text="📋 Мои подписки", callback_data="wishlist_list")],
        [InlineKeyboardButton(text="🔙 Назад к поиску", callback_data="back_to_search")]
    ])

    await callback.message.edit_text(
        "🔔 <b>Лист ожидания (Wishlist)</b>\n\n"
        "Вы можете подписаться на поиск определенного оборудования. Как только оно появится в базе, бот пришлет вам уведомление.\n\n"
        "Например: «DJI Mavic 3 Москва»",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_search")
async def back_to_search(callback: types.CallbackQuery):
    from bot.handlers.search import cmd_search
    await cmd_search(callback.message)
    await callback.message.delete()
    await callback.answer()

@router.callback_query(F.data == "wishlist_list")
async def list_subscriptions(callback: types.CallbackQuery):
    async with async_session() as session:
        from db.crud.user import get_user
        db_user = await get_user(session, callback.from_user.id)
        if not db_user:
            await callback.answer("Сначала зарегистрируйтесь!")
            return

        result = await session.execute(
            select(SearchSubscription).where(SearchSubscription.user_id == db_user.id)
        )
        subs = result.scalars().all()

    if not subs:
        await callback.message.answer("У вас пока нет активных подписок.")
        await callback.answer()
        return

    text = "📋 <b>Ваши подписки:</b>\n\n"
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    for s in subs:
        text += f"🔹 «{s.query}»\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Очистить всё", callback_data="wishlist_clear_all")]
    ])

    await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "wishlist_clear_all")
async def clear_subscriptions(callback: types.CallbackQuery):
    async with async_session() as session:
        from db.crud.user import get_user
        db_user = await get_user(session, callback.from_user.id)
        if db_user:
            await session.execute(delete(SearchSubscription).where(SearchSubscription.user_id == db_user.id))
            await session.commit()

    await callback.message.edit_text("✅ Все подписки удалены.")
    await callback.answer()

from bot.states.wishlist import WishlistStates
from aiogram.fsm.context import FSMContext
from bot.keyboards.main_menu import get_main_menu

@router.callback_query(F.data == "wishlist_create")
async def wishlist_create_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📝 <b>Создание подписки</b>\n\n"
        "Введите поисковый запрос (например: <i>Mavic 3</i> или <i>Объектив Canon</i>).\n\n"
        "Как только в системе появится активное объявление с таким названием, мы сообщим вам!",
        parse_mode="HTML"
    )
    await state.set_state(WishlistStates.waiting_for_query)
    await callback.answer()

@router.message(WishlistStates.waiting_for_query, F.text)
async def process_wishlist_query(message: types.Message, state: FSMContext):
    query = message.text.strip()
    if len(query) < 3:
        await message.answer("⚠️ Запрос слишком короткий. Попробуйте более точное название.")
        return

    async with async_session() as session:
        from db.crud.user import get_user
        db_user = await get_user(session, message.from_user.id)
        if not db_user:
            await message.answer("⚠️ Сначала зарегистрируйтесь!")
            await state.clear()
            return

        new_sub = SearchSubscription(
            user_id=db_user.id,
            query=query,
            is_active=True
        )
        session.add(new_sub)
        await session.commit()

    await state.clear()
    await message.answer(
        f"✅ <b>Подписка оформлена!</b>\n\n"
        f"Мы сообщим вам, как только «{query}» появится в базе.",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )
