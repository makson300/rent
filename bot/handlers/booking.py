import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.states.booking import BookingState
from db.base import async_session
from sqlalchemy import select
from db.models.listing import Listing

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data.startswith("book_listing_"))
async def start_booking(callback: types.CallbackQuery, state: FSMContext):
    listing_id = int(callback.data.split("_")[2])
    await state.update_data(listing_id=listing_id)
    
    await callback.message.answer(
        "📅 <b>Бронирование оборудования</b>\n\n"
        "Пожалуйста, укажите желаемые даты аренды.\n"
        "<i>Например: 10.05.2024 - 15.05.2024</i>",
        parse_mode="HTML"
    )
    await state.set_state(BookingState.waiting_for_dates)
    await callback.answer()

@router.message(BookingState.waiting_for_dates)
async def process_booking_dates(message: types.Message, state: FSMContext):
    dates = message.text.strip()
    data = await state.get_data()
    listing_id = data.get("listing_id")
    
    async with async_session() as session:
        from sqlalchemy.orm import selectinload
        result = await session.execute(
            select(Listing).where(Listing.id == listing_id).options(selectinload(Listing.user))
        )
        listing = result.scalar_one_or_none()
        
        if not listing:
            await message.answer("Объявление не найдено.")
            await state.clear()
            return
            
        owner_id = listing.user.telegram_id if listing.user else None
        
        # Обновляем даты в БД
        current_dates = listing.booked_dates or ""
        listing.booked_dates = f"{current_dates} | {dates}".strip(" |")
        await session.commit()
        
    await message.answer(
        "✅ <b>Запрос на бронирование отправлен!</b>\n\n"
        f"Даты: {dates}\nВладелец свяжется с вами в ближайшее время.",
        parse_mode="HTML"
    )
    
    # Отправляем уведомление владельцу
    if owner_id:
        try:
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            kb = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="💬 Написать арендатору", url=f"tg://user?id={message.from_user.id}")
            ]])
            await message.bot.send_message(
                chat_id=owner_id,
                text=f"🔔 <b>Новый запрос на аренду!</b>\n\n"
                     f"Пользователь @{message.from_user.username or message.from_user.first_name} хочет арендовать <b>{listing.title}</b>.\n"
                     f"📅 Даты: {dates}\n\nСвяжитесь с ним для подтверждения брони.",
                parse_mode="HTML",
                reply_markup=kb
            )
        except Exception as e:
            logger.error(f"Failed to notify owner: {e}")
        
    await state.clear()
