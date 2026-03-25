from aiogram import Router, types, F
from db.base import async_session
from db.crud.listing import get_active_listings_by_city

router = Router()

@router.callback_query(F.data.startswith("view_city_"))
async def show_city_listings(callback: types.CallbackQuery):
    city = callback.data.split("_")[2]
    async with async_session() as session:
        listings = await get_active_listings_by_city(session, city)
        
    if not listings:
        await callback.message.answer(f"😔 В городе {city} пока нет доступного оборудования.", parse_mode="HTML")
        await callback.answer()
        return
        
    await callback.message.answer(f"🔍 <b>Каталог: {city}</b>\nНайдено объявлений: {len(listings)}", parse_mode="HTML")
    
    for listing in listings:
        text = (
            f"📦 <b>{listing.title}</b>\n\n"
            f"📝 {listing.description}\n\n"
            f"💰 <b>Цены:</b>\n{listing.price_list}\n\n"
            f"🚚 <b>Доставка/Самовывоз:</b>\n{listing.delivery_terms}\n\n"
            f"🛡 <b>Залог:</b>\n{listing.deposit_terms}\n\n"
            f"📞 <b>Контакты:</b> {listing.contacts}"
        )
        # Отправляем первое фото с текстом, если оно есть (у телеграма лимит 1024 символа на caption)
        if listing.photos:
            photo_id = listing.photos[0].photo_id
            await callback.message.answer_photo(photo_id, caption=text[:1024], parse_mode="HTML")
        else:
            await callback.message.answer(text, parse_mode="HTML")
            
    await callback.answer()
