import logging
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, func

from db.base import async_session
from db.models.tender import Tender
from db.models.listing import Listing
from bot.handlers.admin import get_user_role
from sqlalchemy import select, func, update

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
        [InlineKeyboardButton(text="💼 Мониторинг Госзакупок (Новые)", callback_data="admin_b2g_scan")],
        [InlineKeyboardButton(text="💼 Закупки В Работе", callback_data="admin_b2g_approved")],
        [InlineKeyboardButton(text="📉 Анализ цен (Ниже Рынка)", callback_data="admin_market_scan")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back_to_main")]
    ])
    
    text = (
        "📈 <b>Радар (Арбитраж и Госзакупки)</b>\n\n"
        "Этот модуль позволяет:\n"
        "1. Находить недооцененные дроны.\n"
        "2. Парсить Государственные Тендеры из ЕИС, фильтровать их и брать в работу.\n\n"
    )
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "admin_b2g_scan")
async def b2g_scan(callback: types.CallbackQuery):
    async with async_session() as session:
        role = await get_user_role(session, callback.from_user.id, callback.from_user.username)
        if role != "admin": return
        
        wait_msg = await callback.message.answer("⏳ <i>Читаю базу новых тендеров ЕИС...</i>", parse_mode="HTML")
        
        tenders_res = await session.execute(
            select(Tender).where(Tender.is_b2g == True, Tender.b2g_status == "new").order_by(Tender.id.desc()).limit(3)
        )
        tenders = tenders_res.scalars().all()
        
    await wait_msg.delete()
    
    if not tenders:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад в Радар", callback_data="admin_radar_menu")]])
        await callback.message.edit_text("💼 <b>Новых B2G тендеров не найдено.</b>\n\nПарсер скоро обновит базу.", parse_mode="HTML", reply_markup=kb)
        return

    text = "💼 <b>Новые Госзакупки (B2G Радар)</b>\n\n"
    
    kb_list = []
    
    for t in tenders:
        text += f"▪️ <b>Контракт ЕИС #{t.id}</b> ({t.eis_fz or '44-ФЗ'})\n"
        text += f"📌 {t.title}\n"
        text += f"🏢 Заказчик: {t.customer_name}\n"
        budget = f"{t.budget:,}" if t.budget else "Не указан"
        text += f"💰 Бюджет: {budget} ₽\n\n"
        
        url = t.b2g_url if t.b2g_url else "https://zakupki.gov.ru"
        kb_list.append([
            InlineKeyboardButton(text=f"✅ В работу #{t.id}", callback_data=f"b2g_appr_{t.id}"),
            InlineKeyboardButton(text=f"❌ Отклон #{t.id}", callback_data=f"b2g_rej_{t.id}")
        ])
        kb_list.append([
            InlineKeyboardButton(text=f"🔗 Ссылка ЕИС #{t.id}", url=url)
        ])
        
    kb_list.append([InlineKeyboardButton(text="🔙 Назад в Радар", callback_data="admin_radar_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("b2g_appr_"))
async def b2g_approve(callback: types.CallbackQuery):
    tender_id = int(callback.data.split("_")[2])
    async with async_session() as session:
        role = await get_user_role(session, callback.from_user.id, callback.from_user.username)
        if role != "admin": return
        await session.execute(update(Tender).where(Tender.id == tender_id).values(b2g_status="approved"))
        await session.commit()
        
    try:
        from bot.services.smart_tenders import run_b2g_matching
        await run_b2g_matching(callback.bot, tender_id)
    except Exception as e:
        logger.error(f"Failed to run smart matching for {tender_id}: {e}")
        
    await callback.answer(f"Тендер #{tender_id} взят в работу и разослан пилотам!", show_alert=True)
    await b2g_scan(callback)
    
@router.callback_query(F.data.startswith("b2g_rej_"))
async def b2g_reject(callback: types.CallbackQuery):
    tender_id = int(callback.data.split("_")[2])
    async with async_session() as session:
        role = await get_user_role(session, callback.from_user.id, callback.from_user.username)
        if role != "admin": return
        await session.execute(update(Tender).where(Tender.id == tender_id).values(b2g_status="rejected"))
        await session.commit()
    await callback.answer(f"Тендер #{tender_id} отклонен.")
    await b2g_scan(callback)

@router.callback_query(F.data == "admin_b2g_approved")
async def b2g_approved_list(callback: types.CallbackQuery):
    async with async_session() as session:
        role = await get_user_role(session, callback.from_user.id, callback.from_user.username)
        if role != "admin": return
        tenders_res = await session.execute(
            select(Tender).where(Tender.is_b2g == True, Tender.b2g_status == "approved").order_by(Tender.id.desc()).limit(5)
        )
        tenders = tenders_res.scalars().all()
        
    if not tenders:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад в Радар", callback_data="admin_radar_menu")]])
        await callback.message.edit_text("💼 <b>Нет тендеров в работе.</b>", parse_mode="HTML", reply_markup=kb)
        return
        
    text = "💼 <b>Госзакупки В Работе (Топ-5)</b>\n\n"
    kb_list = []
    for t in tenders:
        text += f"▪️ <b>#{t.id}</b> {t.title}\n"
        url = t.b2g_url if t.b2g_url else "https://zakupki.gov.ru"
        kb_list.append([InlineKeyboardButton(text=f"Смотреть #{t.id}", url=url)])
        
    kb_list.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_radar_menu")])
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
