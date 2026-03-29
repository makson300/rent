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
    
    from db.models.review import Review
    from sqlalchemy import select, func
    async with async_session() as session:
        rating_res = await session.execute(
            select(func.avg(Review.rating), func.count(Review.id))
            .where(Review.target_user_id == listing.user_id)
        )
        avg_rating, review_count = rating_res.fetchone()
        
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    seller_badges = ""
    user = listing.user
    if getattr(user, 'volunteer_rescues', 0) > 0:
        seller_badges += " 🏅"
    if review_count >= 3 and avg_rating >= 4.8:
        seller_badges += " ⭐️ Топ-Владелец"

    availability = "✅ Свободно" if not listing.booked_dates else f"📅 Занято: {listing.booked_dates}"
    text = (
        f"🔍 <b>{city_name} | {cat_name}</b> ({page+1}/{total})\n\n"
        f"📦 <b>{listing.title}</b>\n"
        f"👤 <b>Владелец:</b> {user.first_name}{seller_badges} (⭐ {avg_rating})\n\n"
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
        [types.InlineKeyboardButton(text="📅 Оформить аренду", callback_data=f"book_listing_{listing.id}")],
        [types.InlineKeyboardButton(text="👤 Профиль продавца", callback_data=f"view_seller_{listing.user_id}")],
        [types.InlineKeyboardButton(text="💬 Написать владельцу", url=f"tg://user?id={listing.user.telegram_id}" if getattr(listing, 'user', None) else f"https://t.me/share/url?url={listing.contacts}")],
        nav_buttons,
        [types.InlineKeyboardButton(text="🚨 Пожаловаться", callback_data=f"report_listing_{listing.id}")],
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

from bot.config import ADMIN_IDS

@router.callback_query(F.data.startswith("report_listing_"))
async def report_listing(callback: types.CallbackQuery):
    listing_id = int(callback.data.split("_")[2])
    
    # Send report to admins
    if ADMIN_IDS:
        target_admin = ADMIN_IDS[0]
        text = (
            f"🚨 <b>Жалоба на объявление!</b>\n\n"
            f"Пользователь ID <code>{callback.from_user.id}</code> (@{callback.from_user.username}) "
            f"пожаловался на объявление ID {listing_id}.\n\n"
            f"Проверьте объявление через панель или БД."
        )
        try:
            await callback.bot.send_message(chat_id=target_admin, text=text, parse_mode="HTML")
            await callback.answer("✅ Ваша жалоба отправлена модераторам.", show_alert=True)
        except Exception:
            await callback.answer("⚠️ Ошибка отправки жалобы. Попробуйте позже.", show_alert=True)
    else:
        await callback.answer("⚠️ Модераторы временно недоступны.", show_alert=True)

import json

@router.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    """Обработка данных, возвращаемых из WebApp (TMA)"""
    data_str = message.web_app_data.data
    try:
        data = json.loads(data_str)
        action = data.get("action")
        listing_id = data.get("id")
        
        if action == "view" and listing_id:
            from db.crud.listing import get_listing
            async with async_session() as session:
                listing = await get_listing(session, int(listing_id))
                
            if not listing:
                await message.answer("⚠️ Объявление не найдено или удалено.")
                return
                
            cat_map = {1: "Аренда", 2: "Продажа", 6: "Оператор"}
            cat_name = cat_map.get(listing.category_id, "Оборудование")
            city_name = listing.city
            
            from db.models.review import Review
            from sqlalchemy import select, func
            async with async_session() as session:
                rating_res = await session.execute(
                    select(func.avg(Review.rating), func.count(Review.id))
                    .where(Review.target_user_id == listing.user_id)
                )
                avg_rating, review_count = rating_res.fetchone()
                
            avg_rating = round(avg_rating, 1) if avg_rating else 0
            seller_badges = ""
            user = listing.user
            if getattr(user, 'volunteer_rescues', 0) > 0:
                seller_badges += " 🏅"
            if review_count >= 3 and avg_rating >= 4.8:
                seller_badges += " ⭐️ Топ-Владелец"
        
            availability = "✅ Свободно" if not listing.booked_dates else f"📅 Занято: {listing.booked_dates}"
            text = (
                f"🔍 <b>{city_name} | {cat_name}</b>\n\n"
                f"📦 <b>{listing.title}</b>\n"
                f"👤 <b>Владелец:</b> {user.first_name}{seller_badges} (⭐ {avg_rating})\n\n"
                f"📝 {listing.description}\n\n"
                f"📊 <b>Статус:</b> {availability}\n\n"
                f"💰 <b>Цены:</b>\n{listing.price_list}\n\n"
                f"🚚 <b>Доставка:</b> {listing.delivery_terms}\n"
                f"🛡 <b>Залог:</b> {listing.deposit_terms}\n\n"
                f"📞 <b>Контакты:</b> {listing.contacts}"
            )
            
            kb = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="📅 Оформить", callback_data=f"book_listing_{listing.id}")],
                [types.InlineKeyboardButton(text="👤 Профиль продавца", callback_data=f"view_seller_{listing.user_id}")],
                [types.InlineKeyboardButton(text="💬 Написать владельцу", url=f"tg://user?id={listing.user.telegram_id}" if getattr(listing, 'user', None) else f"https://t.me/share/url?url={listing.contacts}")]
            ])
        
            if listing.photos:
                photo_id = listing.photos[0].photo_id
                await message.answer_photo(photo_id, caption=text[:1024], parse_mode="HTML", reply_markup=kb)
            else:
                await message.answer(text, parse_mode="HTML", reply_markup=kb)
                
        elif action == "apply_job":
            job_id = data.get("id")
            if not job_id:
                return
            
            from db.models.job import Job
            from db.models.job_response import JobResponse
            from sqlalchemy import select
            
            async with async_session() as session:
                job = await session.scalar(select(Job).where(Job.id == int(job_id)))
                if not job:
                    await message.answer("⚠️ Вакансия / заказ не найдена.")
                    return
                if job.status != "active":
                    await message.answer("⚠️ Заказ больше не актуален.")
                    return
                
                # Check if already applied
                existing = await session.scalar(
                    select(JobResponse).where(
                        JobResponse.job_id == job.id, JobResponse.pilot_id == message.from_user.id
                    )
                )
                if existing:
                    await message.answer("⚠️ Вы уже откликались на этот заказ.")
                    return
                
                # Retrieve pilot info
                from db.crud.user import get_user_profile
                pilot = await get_user_profile(session, message.from_user.id)
                
                # Save response
                resp = JobResponse(job_id=job.id, pilot_id=message.from_user.id)
                session.add(resp)
                await session.commit()
                
            # Send message to employer
            pilot_username = f"@{message.from_user.username}" if message.from_user.username else f"<a href='tg://user?id={message.from_user.id}'>Ссылка</a>"
            pilot_name = message.from_user.first_name
            pilot_info = (
                f"Внешний пилот: <b>{'Да' if pilot.has_license else 'Нет'}</b>\n"
                f"Наличие медкнижки (ВЛЭК): <b>{'Да' if pilot.has_medical else 'Нет'}</b>\n"
                f"Часы налета: <b>{pilot.flight_hours} ч.</b>"
            ) if pilot else "<i>Профиль пилота пока не заполнен.</i>"
            
            employer_msg = (
                f"🔥 <b>Новый отклик на ваш заказ!</b>\n\n"
                f"<b>Задача:</b> {job.title}\n"
                f"<b>Откликнулся пилот:</b> {pilot_name} ({pilot_username})\n\n"
                f"<b>Справка о кандидате:</b>\n{pilot_info}\n\n"
                f"Свяжитесь с пилотом для обсуждения подробностей!"
            )
            try:
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💬 Написать пилоту", url=f"tg://user?id={message.from_user.id}")],
                    [InlineKeyboardButton(text="🤝 Выбрать Исполнителем (Договор)", callback_data=f"hire_pilot_{job.id}_{message.from_user.id}")]
                ])
                await message.bot.send_message(chat_id=job.employer_id, text=employer_msg, parse_mode="HTML", reply_markup=kb)
                await message.answer("✅ <b>Ваш отклик успешно отправлен заказчику!</b> Ожидайте сообщения от работодателя.", parse_mode="HTML")
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Error sending job response to employer {job.employer_id}: {e}")
                await message.answer("❌ Не удалось доставить отклик заказчику. Возможно, он заблокировал бота.")
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error handling web_app_data: {e}")
        await message.answer("⚠️ Ошибка обработки запроса из каталога.")
