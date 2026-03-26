from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.base import async_session
from db.crud.listing import get_listings_by_filter
from bot.constants import CITY_MAP, CATEGORY_MAP, CITY_REVERSE_MAP, CATEGORY_REVERSE_MAP

router = Router()


@router.callback_query(F.data.startswith("view_city_"))
async def show_city_categories(callback: types.CallbackQuery):
    """Выбор категории после выбора города в каталоге"""
    city_id = callback.data.split("_")[2]
    city_name = CITY_MAP.get(city_id, city_id)
    
    # Создаем клавиатуру с категориями
    # Используем компактный формат view_cat:city_id:cat_id:page
    # Но для совместимости со старым кодом пока оставим похожий формат, но с ID
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"view_cat:{city_id}:{cid}:0")]
        for cid, name in CATEGORY_MAP.items() if int(cid) < 6
    ])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад к городам", callback_data="back_to_cities")])
    
    await callback.message.edit_text(
        f"🏙 <b>Город: {city_name}</b>\n\nВыберите категорию оборудования:",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_cities")
async def back_to_cities(callback: types.CallbackQuery):
    """Возврат к выбору города"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"view_city_{cid}")] for cid, name in CITY_MAP.items()
    ])
    await callback.message.edit_text(
        "🔍 <b>Раздел «Аренда»</b>\n\nВыберите город из списка ниже 🏙",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()


import os

@router.callback_query(F.data.startswith("gen_contract_"))
async def gen_contract(callback: types.CallbackQuery):
    listing_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        from db.models.user import User
        from db.models.listing import Listing

        result = await session.execute(
            select(Listing).options(selectinload(Listing.user)).where(Listing.id == listing_id)
        )
        listing = result.scalar_one_or_none()

        if not listing:
            await callback.answer("Ошибка: объявление не найдено.")
            return

        db_user_res = await session.execute(select(User).where(User.telegram_id == callback.from_user.id))
        tenant = db_user_res.scalar_one_or_none()
        if not tenant:
             await callback.answer("Зарегистрируйтесь в профиле!")
             return

    from bot.services.pdf_service import generate_rental_contract
    from aiogram.types import FSInputFile

    file_path = f"contract_{listing_id}_{callback.from_user.id}.pdf"
    generate_rental_contract(listing, listing.user, tenant, file_path)

    await callback.message.answer_document(
        FSInputFile(file_path),
        caption="📜 <b>Ваш договор аренды готов!</b>\n\nЭтот файл содержит данные об оборудовании и сторонах. Пожалуйста, распечатайте и подпишите его при встрече.",
        parse_mode="HTML"
    )
    if os.path.exists(file_path):
        os.remove(file_path)
    await callback.answer()

@router.callback_query(F.data.startswith("view_cat:"))
async def show_category_listings(callback: types.CallbackQuery):
    """Показ объявлений для выбранного города и категории"""
    parts = callback.data.split(":")
    city_id = parts[1]
    cat_id = parts[2]
    page = int(parts[3])

    city_name = CITY_MAP.get(city_id, "Неизвестно")
    cat_name = CATEGORY_MAP.get(cat_id, "Неизвестно")
    
    async with async_session() as session:
        # Поиск по city_name и cat_id
        listings = await get_listings_by_filter(session, city=city_name, category=cat_name)
        
    if not listings:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к категориям", callback_data=f"view_city_{city_id}")]
        ])
        await callback.message.edit_text(
            f"😔 В городе <b>{city_name}</b> в категории <b>{cat_name}</b> пока нет объявлений.",
            parse_mode="HTML",
            reply_markup=kb
        )
        await callback.answer()
        return
        
    await callback.message.answer(
        f"🔍 <b>{city_name} | {cat_name}</b>\nНайдено объявлений: {len(listings)}",
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
            [InlineKeyboardButton(text="📜 Сгенерировать договор (PDF)", callback_data=f"gen_contract_{listing.id}")]
        ])

        if listing.photos:
            photo_id = listing.photos[0].photo_id
            await callback.message.answer_photo(photo_id, caption=text[:1024], reply_markup=kb, parse_mode="HTML")
        else:
            await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
            
    await callback.answer()
