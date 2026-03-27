from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.base import async_session
from db.crud.listing import get_listings_by_filter
from bot.handlers.listing_create import CITIES, CATEGORIES

router = Router()


@router.callback_query(F.data.startswith("view_city_"))
async def show_city_categories(callback: types.CallbackQuery):
    """Выбор категории после выбора города в каталоге"""
    city = callback.data.split("_")[2]
    
    # Создаем клавиатуру с категориями
    # В callback_data передаем и город, и категорию
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cat, callback_data=f"view_cat_{city}_{cat}")] for cat in CATEGORIES
    ])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад к городам", callback_data="back_to_cities")])
    
    await callback.message.edit_text(
        f"🏙 <b>Город: {city}</b>\n\nВыберите категорию оборудования:",
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


@router.callback_query(F.data.startswith("view_cat_"))
async def show_category_listings(callback: types.CallbackQuery):
    """Показ объявлений для выбранного города и категории"""
    parts = callback.data.split("_")
    city = parts[2]
    category = parts[3]
    
    async with async_session() as session:
        # Для простоты пока ищем по имени категории. 
        # В идеале в БД должны быть записи категорий с такими именами.
        # Пока в crud.listing мы захардкодили join по имени.
        listings = await get_listings_by_filter(session, city=city, category=category)
        
    if not listings:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к категориям", callback_data=f"view_city_{city}")]
        ])
        await callback.message.edit_text(
            f"😔 В городе <b>{city}</b> в категории <b>{category}</b> пока нет объявлений.",
            parse_mode="HTML",
            reply_markup=kb
        )
        await callback.answer()
        return
        
    await callback.message.answer(
        f"🔍 <b>{city} | {category}</b>\nНайдено объявлений: {len(listings)}",
        parse_mode="HTML"
    )
    
    for listing in listings:
        text = (
            f"📦 <b>{listing.title}</b>\n\n"
            f"📝 {listing.description}\n\n"
            f"💰 <b>Цены:</b>\n{listing.price_list}\n\n"
            f"🚚 <b>Доставка/Самовывоз:</b>\n{listing.delivery_terms}\n\n"
            f"🛡 <b>Залог:</b>\n{listing.deposit_terms}\n\n"
            f"📞 <b>Контакты:</b> {listing.contacts}"
        )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👤 Профиль продавца", callback_data=f"view_seller_{listing.user_id}")],
            [InlineKeyboardButton(text="💬 Написать владельцу", url=f"tg://user?id={listing.user.telegram_id}" if listing.user else f"https://t.me/share/url?url={listing.contacts}")]
        ])
        
        if listing.photos:
            photo_id = listing.photos[0].photo_id
            await callback.message.answer_photo(photo_id, caption=text[:1024], parse_mode="HTML", reply_markup=kb)
        else:
            await callback.message.answer(text, parse_mode="HTML", reply_markup=kb)
            
    await callback.answer()
