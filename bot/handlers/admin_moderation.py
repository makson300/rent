from aiogram import Router, types, F
from db.base import async_session
from db.crud.listing import update_listing_status, get_listing_by_id
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data.startswith("mod_approve_"))
async def approve_listing(callback: types.CallbackQuery):
    listing_id = int(callback.data.split("_")[2])
    
    async with async_session() as session:
        listing = await update_listing_status(session, listing_id, "active")
        
    if listing:
        await callback.message.edit_caption(
            caption=callback.message.caption + "\n\n✅ <b>ОДОБРЕНО</b>",
            parse_mode="HTML"
        )
        # Уведомляем пользователя
        from db.crud.user import get_user_by_db_id
        async with async_session() as session:
            user = await get_user_by_db_id(session, listing.user_id)
            if user:
                try:
                    await callback.bot.send_message(
                        chat_id=user.telegram_id,
                        text=f"✅ <b>Ваше объявление одобрено!</b>\n\nТовар: <b>{listing.title}</b>\nТеперь оно доступно в каталоге.",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Error notifying user: {e}")
                    
        await callback.answer("Объявление одобрено!")
    else:
        await callback.answer("Ошибка: объявление не найдено.", show_alert=True)


@router.callback_query(F.data.startswith("mod_reject_"))
async def reject_listing(callback: types.CallbackQuery):
    listing_id = int(callback.data.split("_")[2])
    
    async with async_session() as session:
        listing = await update_listing_status(session, listing_id, "rejected")
        
    if listing:
        await callback.message.edit_caption(
            caption=callback.message.caption + "\n\n❌ <b>ОТКЛОНЕНО</b>",
            parse_mode="HTML"
        )
        # Уведомляем пользователя
        from db.crud.user import get_user_by_db_id
        async with async_session() as session:
            user = await get_user_by_db_id(session, listing.user_id)
            if user:
                try:
                    await callback.bot.send_message(
                        chat_id=user.telegram_id,
                        text=f"❌ <b>Ваше объявление отклонено модератором.</b>\n\nТовар: <b>{listing.title}</b>\nПожалуйста, проверьте соответствие правилам и попробуйте снова.",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Error notifying user: {e}")
                    
        await callback.answer("Объявление отклонено.")
    else:
        await callback.answer("Ошибка: объявление не найдено.", show_alert=True)
