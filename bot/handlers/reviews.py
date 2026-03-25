import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.base import async_session
from db.models.review import Review
from db.crud.listing import get_listing_by_id

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data.startswith("rate_listing_"))
async def start_review(callback: types.CallbackQuery, state: FSMContext):
    listing_id = int(callback.data.split("_")[2])

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐️"*i, callback_data=f"set_rating_{listing_id}_{i}")] for i in range(5, 0, -1)
    ])

    await callback.message.edit_text(
        "✨ <b>Оставьте отзыв</b>\n\nОцените ваше впечатление от аренды:",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data.startswith("set_rating_"))
async def process_rating(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    listing_id = int(parts[2])
    rating = int(parts[3])

    async with async_session() as session:
        listing = await get_listing_by_id(session, listing_id)
        if not listing:
            await callback.answer("Ошибка: объявление не найдено.")
            return

        from db.crud.user import get_user
        db_user = await get_user(session, callback.from_user.id)
        if not db_user:
            await callback.answer("Ошибка: пользователь не найден.")
            return

        new_review = Review(
            listing_id=listing_id,
            from_user_id=db_user.id,
            to_user_id=listing.user_id,
            rating=rating,
            comment="Без комментария"
        )
        session.add(new_review)
        await session.commit()

    await callback.message.edit_text(
        f"✅ <b>Спасибо за вашу оценку ({rating}⭐)!</b>\n\nВаш отзыв помогает другим пользователям делать правильный выбор.",
        parse_mode="HTML"
    )
    await callback.answer()
