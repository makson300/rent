from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.base import async_session
from db.crud.listing import get_listings_by_filter
from bot.constants import CITIES, CATEGORIES

router = Router()


from bot.constants import CITY_MAP, CATEGORY_MAP

@router.callback_query(F.data.startswith("view_city_"))
async def show_city_categories(callback: types.CallbackQuery):
    """Выбор категории после выбора города в каталоге"""
    city_id = int(callback.data.split("_")[2])
    city_name = CITY_MAP.get(city_id, "Москва")
    
    # Use IDs in callback data to avoid 64-byte limit
    # Rental categories are 0 (Drones), 1 (Filming), 2 (Other)
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=CATEGORY_MAP[i], callback_data=f"vcat:{city_id}:{i}:0")]
        for i in range(3)
    ])
    kb.inline_keyboard.append([types.InlineKeyboardButton(text="🔙 Назад к городам", callback_data="back_to_cities")])
    
    await callback.message.edit_text(
        f"🏙 <b>Город: {city_name}</b>\n\nВыберите категорию оборудования:",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_cities")
async def back_to_cities(callback: types.CallbackQuery):
    """Возврат к выбору города"""
    from bot.handlers.menu import rental_menu
    # rental_menu ожидает Message, но мы можем вызвать его вручную или просто отправить заново
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=city, callback_data=f"view_city_{city}")] for city in CITIES
    ])
    await callback.message.edit_text(
        "🔍 <b>Раздел «Аренда»</b>\n\nВыберите город из списка ниже 🏙",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()


CAT_PAGE_SIZE = 1 # Showing one item per card is better for mobile navigation

@router.callback_query(F.data.startswith("vcat:"))
async def show_category_listings(callback: types.CallbackQuery):
    """Показ объявлений для выбранного города и категории с пагинацией"""
    parts = callback.data.split(":")
    city_id = int(parts[1])
    cat_id = int(parts[2])
    page = int(parts[3]) if len(parts) > 3 else 0

    city_name = CITY_MAP.get(city_id, "Москва")
    cat_name = CATEGORY_MAP.get(cat_id, "Дроны")
    
    async with async_session() as session:
        listings = await get_listings_by_filter(session, city=city_name, category=cat_name)
        
    if not listings:
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🔙 Назад к категориям", callback_data=f"view_city_{city_id}")]
        ])
        await callback.message.edit_text(
            f"😔 В городе <b>{city_name}</b> в категории <b>{cat_name}</b> пока нет объявлений.",
            parse_mode="HTML",
            reply_markup=kb
        )
        await callback.answer()
        return

    total = len(listings)
    start_idx = page * CAT_PAGE_SIZE
    end_idx = start_idx + CAT_PAGE_SIZE
    current_listings = listings[start_idx:end_idx]

    if not current_listings:
        await callback.answer("Больше нет объявлений.", show_alert=True)
        return
        
    listing = current_listings[0] # Display one card
    availability = "✅ Свободно" if not listing.booked_dates else f"📅 Занято: {listing.booked_dates}"
    text = (
        f"🔍 <b>{city_name} | {cat_name}</b> ({page+1}/{total})\n\n"
        f"📦 <b>{listing.title}</b>\n\n"
        f"📝 {listing.description}\n\n"
        f"📊 <b>Статус:</b> {availability}\n\n"
        f"💰 <b>Цены:</b>\n{listing.price_list}\n\n"
        f"🚚 <b>Доставка:</b> {listing.delivery_terms}\n"
        f"🛡 <b>Залог:</b> {listing.deposit_terms}\n\n"
        f"📞 <b>Контакты:</b> {listing.contacts}"
    )
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text="⬅️ Пред.", callback_data=f"vcat:{city_id}:{cat_id}:{page-1}"))
    if end_idx < total:
        nav_buttons.append(types.InlineKeyboardButton(text="След. ➡️", callback_data=f"vcat:{city_id}:{cat_id}:{page+1}"))
        
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="👤 Профиль продавца", callback_data=f"view_seller_{listing.user_id}")],
        [types.InlineKeyboardButton(text="💬 Написать владельцу", url=f"tg://user?id={listing.user.telegram_id}" if getattr(listing, 'user', None) else f"https://t.me/share/url?url={listing.contacts}")],
        nav_buttons,
        [types.InlineKeyboardButton(text="🔙 К категориям", callback_data=f"view_city_{city_id}")]
    ])

    if listing.photos:
        photo_id = listing.photos[0].photo_id
        try:
            await callback.message.edit_media(
                media=types.InputMediaPhoto(media=photo_id, caption=text[:1024], parse_mode="HTML"),
                reply_markup=kb
            )
        except Exception:
            await callback.message.delete()
            await callback.message.answer_photo(photo_id, caption=text[:1024], parse_mode="HTML", reply_markup=kb)
    else:
        try:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            await callback.message.delete()
            await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
            
    await callback.answer()
