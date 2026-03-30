import logging
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, func

from db.base import async_session
from db.models.listing import Listing
from bot.handlers.admin import get_user_role

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data == "admin_radar_menu")
async def radar_menu(callback: types.CallbackQuery):
    async with async_session() as session:
        role = await get_user_role(session, callback.from_user.id, callback.from_user.username)
        if role != "admin":
            await callback.answer("Только для админов", show_alert=True)
            return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Мониторинг Госзакупок (услуги)", callback_data="admin_b2g_scan")],
        [InlineKeyboardButton(text="📉 Анализ цен (Ниже Рынка)", callback_data="admin_market_scan")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back_to_main")]
    ])
    
    text = (
        "📈 <b>Радар (Арбитраж и Госзакупки)</b>\n\n"
        "Этот модуль позволяет администратору:\n"
        "1. Находить недооцененные дроны в каталоге (Ниже Рынка).\n"
        "2. Находить Государственные Тендеры на Услуги (Малые закупки до 600к), \n"
        "подходящие для Самозанятых.\n\n"
        "<i>Идеальный воркфлоу: Найдите выгодный тендер на услуги, затем найдите дешевый дрон на маркете для выполнения этого тендера.</i>"
    )
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "admin_b2g_scan")
async def b2g_scan(callback: types.CallbackQuery):
    async with async_session() as session:
        role = await get_user_role(session, callback.from_user.id, callback.from_user.username)
        if role != "admin": return
        
    wait_msg = await callback.message.answer("⏳ <i>Анализирую ЕИС (Закупки Малого Объема)...</i>", parse_mode="HTML")
    
    # Моковое подключение к ЕИС (FZ-44)
    # В реальности здесь HTTP запрос к API ЕИС или RSS лентам СберА.
    mock_tenders = [
        {"id": "0373100000124000055", "title": "Аэрофотосъемка линейного объекта (ЛЭП 15км)", "price": 145000, "region": "Свердловская обл."},
        {"id": "32413480112", "title": "Мониторинг теплосетей с БПЛА (Тепловизор)", "price": 380000, "region": "Новосибирск"},
        {"id": "0173200001424000112", "title": "Кадастровая съемка земельных участков (RTK)", "price": 550000, "region": "Московская обл."}
    ]
    
    await wait_msg.delete()
    
    text = "💼 <b>Тендеры для Самозанятых (B2G Радар)</b>\n\n"
    text += "<i>Найдено закупок малого объема (до 600к руб):</i>\n\n"
    
    kb_list = []
    for t in mock_tenders:
        text += f"▪️ <b>Контракт №{t['id']}</b>\n"
        text += f"📌 {t['title']} ({t['region']})\n"
        text += f"💰 Бюджет: {t['price']:,} ₽\n\n"
        
        kb_list.append([InlineKeyboardButton(text=f"Смотреть №{t['id'][-5:]}", url="https://zakupki.gov.ru/epz/main/public/home.html")])
        
    kb_list.append([InlineKeyboardButton(text="🔙 Назад в Радар", callback_data="admin_radar_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "admin_market_scan")
async def market_scan(callback: types.CallbackQuery):
    async with async_session() as session:
        role = await get_user_role(session, callback.from_user.id, callback.from_user.username)
        if role != "admin": return

    wait_msg = await callback.message.answer("📉 <i>Сканирую каталог платформы на арбитражные сделки...</i>", parse_mode="HTML")
    
    # Logic: Group all sale listings by TITLE (fuzzy/exact) and find avg price
    # For MVP we will extract basic numbers if parseable
    import re
    
    async with async_session() as db:
        # Get all sales
        sales_res = await db.execute(select(Listing).where(Listing.listing_type == "sale", Listing.status == "active"))
        sales = sales_res.scalars().all()
        
    # extract raw integer prices
    def extract_price(plist):
        nums = re.findall(r'\d+', str(plist).replace(" ", ""))
        if nums:
            return int(nums[0])
        return 0
        
    models_prices = {}
    
    for s in sales:
        clean_title = s.title.strip().lower()
        price = extract_price(s.price_list)
        if price > 5000: # ignore accessories temporarily
            if clean_title not in models_prices:
                models_prices[clean_title] = []
            models_prices[clean_title].append({"id": s.id, "price": price, "title": s.title})
            
    arbitrage_deals = []
    
    for model, items in models_prices.items():
        if len(items) >= 2: # need at least 2 to calculate an average
            avg_price = sum([i["price"] for i in items]) / len(items)
            # Find deals that are 20% below average
            for i in items:
                if i["price"] < avg_price * 0.8: # 20% cheaper
                    arbitrage_deals.append({
                        "id": i["id"],
                        "title": i["title"],
                        "price": i["price"],
                        "avg": avg_price,
                        "discount_percent": round(100 - (i["price"] / avg_price)*100)
                    })
                    
    await wait_msg.delete()
    
    if not arbitrage_deals:
        # Mock deal if nothing found to show functionality
        text = (
            "📉 <b>Анализ Цен (Арбитраж)</b>\n\n"
            "К сожалению, сейчас в каталоге нет дронов, которые продавались бы значительно дешевле рынка (от 20% дисконта).\n\n"
            "<i>(Демо-вариант:)</i>\n"
            "🚨 <b>DJI Mavic 3 Enterprise</b>\n"
            "Цена: 160 000 ₽ <i>(Рынок: ~205 000 ₽)</i>\n"
            "🔥 Ниже рынка на <b>22%</b>"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад в Радар", callback_data="admin_radar_menu")]])
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await callback.answer()
        return

    text = "📉 <b>Найдены Арбитражные Сделки!</b>\n\n"
    
    kb_list = []
    for d in arbitrage_deals:
        text += f"🚨 <b>{d['title']}</b>\n"
        text += f"Цена: {d['price']:,} ₽ <i>(В среднем: ~{int(d['avg']):,} ₽)</i>\n"
        text += f"🔥 Выгода: <b>{d['discount_percent']}%</b>\n\n"
        
        kb_list.append([InlineKeyboardButton(text=f"Смотреть {d['title'][:15]}...", url=f"https://t.me/{callback.bot._me.username}?start=listing_{d['id']}")])
        
    kb_list.append([InlineKeyboardButton(text="🔙 Назад в Радар", callback_data="admin_radar_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()
