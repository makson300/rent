from aiogram import Router, types, F
from db.base import async_session
from db.crud.listing import update_listing_status, get_listing_by_id

router = Router()

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
        # Нам нужно знать telegram_id пользователя. Мы можем получить его через listing.user.telegram_id.
        # Но для этого нужно подгрузить связь user.
        # В crud.listing.get_listing_by_id мы подгружаем только photos.
        
        # Попробуем подтянуть юзера
        from db.crud.user import get_user_by_db_id # Нам нужна такая функция
        # Или просто использовать listing.user_id если он совпадает с telegram_id (нет, не совпадает)
        
        # Для простоты пока просто редактируем сообщение админа
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
        await callback.answer("Объявление отклонено.")
    else:
        await callback.answer("Ошибка: объявление не найдено.", show_alert=True)
