import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.keyboards import get_main_menu
from sqlalchemy.ext.asyncio import AsyncSession
from db.base import async_session
from db.models.listing import Listing

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "🛍 Магазин")
async def sales_catalog(message: types.Message):
    """Показ товаров от партнеров (drone_IT_Shop)"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Посмотреть объявления", callback_data="view_sales_list")],
        [InlineKeyboardButton(text="➕ Разместить объявление", callback_data="start_sale_listing")]
    ])
    
    await message.answer(
        "📢 <b>Доска объявлений о продаже</b>\n\n"
        "Здесь вы можете купить или продать оборудование.\n\n"
        "🔹 Публикация объявлений разделена для Магазинов (новое) и Частных лиц (б/у).",
        parse_mode="HTML",
        reply_markup=kb
    )

@router.callback_query(F.data == "view_sales_list")
async def show_sales_list_cats(callback: types.CallbackQuery):
    """Показ выбора категории продавца"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏢 От магазинов (Новое)", callback_data="sales_cat_store")],
        [InlineKeyboardButton(text="👤 От собственников (Б/У)", callback_data="sales_cat_individual")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_sales_main")]
    ])
    await callback.message.edit_text(
        "🛒 <b>Выберите категорию товаров:</b>",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data.startswith("sales_cat_"))
async def show_sales_items(callback: types.CallbackQuery):
    """Показ объявлений по типу продавца"""
    seller_type = callback.data.split("_")[2] # "store" or "individual"
    from sqlalchemy import select
    from db.base import async_session
    from db.models.listing import Listing
    from sqlalchemy.orm import selectinload
    
    async with async_session() as session:
        result = await session.execute(
            select(Listing)
            .options(selectinload(Listing.photos))
            .where(Listing.listing_type == "sale")
            .where(Listing.status == "active")
            .where(Listing.seller_type == seller_type)
        )
        listings = result.scalars().all()
        
    title = "Магазины (Новое)" if seller_type == "store" else "Частные лица (Б/У)"
    
    if not listings:
        await callback.message.answer(f"😔 В категории <b>{title}</b> пока нет объявлений.")
        await callback.answer()
        return
        
    await callback.message.answer(f"🛍 <b>{title}</b>\nНайдено: {len(listings)}", parse_mode="HTML")
    
    for l in listings:
        text = (
            f"💰 <b>{l.title}</b>\n\n"
            f"📝 {l.description}\n\n"
            f"💵 <b>Цена:</b> {l.price_list}\n"
            f"📞 <b>Контакты:</b> {l.contacts}"
        )
        if l.photos:
            await callback.message.answer_photo(l.photos[0].photo_id, caption=text[:1024], parse_mode="HTML")
        else:
            await callback.message.answer(text, parse_mode="HTML")
            
    await callback.answer()

@router.callback_query(F.data == "back_to_sales_main")
async def back_to_sales_main(callback: types.CallbackQuery):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Посмотреть объявления", callback_data="view_sales_list")],
        [InlineKeyboardButton(text="➕ Разместить объявление", callback_data="start_sale_listing")]
    ])
    await callback.message.edit_text(
        "📢 <b>Доска объявлений о продаже</b>\n\n"
        "Здесь вы можете купить или продать оборудование.\n\n"
        "🔹 Публикация объявлений разделена для Магазинов (новое) и Частных лиц (б/у).",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer()


@router.callback_query(F.data == "start_sale_listing")
async def start_sale_listing(callback: types.CallbackQuery, state: FSMContext):
    """Начало создания объявления о ПРОДАЖЕ (бесплатно)"""
    from bot.handlers.listing_create import start_listing_create
    await state.update_data(listing_type="sale", category_id=2) # 2 - Продажа
    await start_listing_create(callback, state)

@router.message(F.forward_from_chat & (F.forward_from_chat.username == "drone_IT_Shop"))
@router.channel_post(F.chat.username == "drone_IT_Shop")
def parse_partner_post(text: str) -> dict:
    """Парсинг текста поста для извлечения цены и заголовка"""
    import re
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return {"title": "Товар от партнера", "price": "По запросу", "desc": text}
        
    title = lines[0][:100]
    price = "По запросу"
    
    # Регулярка для поиска цены (числа с валютой)
    price_pattern = r'(\d[\d\s.,]*)\s*(?:руб|р|₽|\$|€|usd|eur)'
    match = re.search(price_pattern, text.lower())
    if match:
        price = match.group(0).strip()
    else:
        # Поиск по ключевым словам
        for line in lines:
            if any(kw in line.lower() for kw in ["цена:", "стоимость:", "прайс:"]):
                price = line.split(":")[-1].strip()
                break
                
    return {"title": title, "price": price, "desc": text}


@router.message(F.forward_from_chat & (F.forward_from_chat.username == "drone_IT_Shop"))
@router.channel_post(F.chat.username == "drone_IT_Shop")
async def import_partner_post(message: types.Message):
    """Автоматический импорт постов от партнера (@drone_IT_Shop) без модерации"""
    from bot.handlers.admin import is_admin
    
    is_from_channel = message.chat.type == "channel"
    if not is_from_channel and not is_admin(message.from_user.id, message.from_user.username):
        return

    text = message.text or message.caption or ""
    if not text:
        return

    parsed = parse_partner_post(text)

    # Сохраняем в БД
    from db.base import async_session
    from db.models.listing import Listing, ListingPhoto
    from db.crud.user import get_user
    
    async with async_session() as session:
        db_user = await get_user(session, 0) # Используем системного юзера (telegram_id=0)
        user_db_id = db_user.id if db_user else 1

        new_listing = Listing(
            user_id=user_db_id,
            category_id=2, # Продажа
            city="Москва",
            title=parsed["title"],
            description=parsed["desc"],
            price_list=parsed["price"],
            listing_type="sale",
            partner_id="drone_IT_Shop",
            status="active",
            deposit_terms="Не требуется",
            delivery_terms="Уточняйте у продавца",
            contacts="@drone_IT_Shop"
        )
        session.add(new_listing)
        await session.flush()
        
        # Обработка фото (если это медиагруппа, aiogram пришлет несколько сообщений, 
        # но мы пока обрабатываем текущее)
        if message.photo:
            photo = ListingPhoto(
                listing_id=new_listing.id,
                photo_id=message.photo[-1].file_id
            )
            session.add(photo)
            
        await session.commit()

    if not is_from_channel:
        await message.answer(
            f"✅ <b>Пост распознан как «Продажа»!</b>\n"
            f"Товар: {parsed['title']}\n"
            f"Цена: {parsed['price']}\n\n"
            f"Статус: Опубликовано в Магазине.",
            parse_mode="HTML"
        )
