import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from bot.config import BOT_TOKEN # Assuming we might want to check against an ADMIN_ID eventually
from db.base import async_session
from db.models.listing import Listing
from db.models.user import User
from db.models.education import EducationApplication
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, func
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
logger = logging.getLogger(__name__)

async def get_user_role(session, user_id: int, username: str | None = None) -> str:
    from bot.config import ADMIN_IDS
    if user_id in ADMIN_IDS:
        return "admin"
    from db.crud.user import get_user
    u = await get_user(session, user_id)
    if not u:
        return "user"
    if getattr(u, "is_admin", False):
        return "admin"
    if getattr(u, "is_moderator", False):
        return "moderator"
    return "user"

@router.message(Command("me"))
async def cmd_me(message: types.Message):
    """Диагностика ID и прав"""
    async with async_session() as session:
        role = await get_user_role(session, message.from_user.id, message.from_user.username)
        
    status = "✅ АДМИН" if role == "admin" else ("🔰 МОДЕРАТОР" if role == "moderator" else "❌ Пользователь")
    await message.answer(f"🆔 Ваш ID: <code>{message.from_user.id}</code>\n🔑 Роль: {status}", parse_mode="HTML")

@router.message(Command("ban"))
async def ban_user_cmd(message: types.Message):
    """Бан пользователя по Telegram ID. Использование: /ban 123456789"""
    async with async_session() as session:
        role = await get_user_role(session, message.from_user.id, message.from_user.username)
        if role != "admin":
            return
            
        args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("⚠️ Использование: `/ban <telegram_id>`", parse_mode="Markdown")
        return
        
    target_id = int(args[1])
    async with async_session() as session:
        from db.crud.user import set_user_ban_status
        success = await set_user_ban_status(session, target_id, True)
    
    if success:
        await message.answer(f"✅ Пользователь {target_id} ЗАБАНЕН. Его объявления скрыты из поиска.")
    else:
        await message.answer(f"❌ Пользователь {target_id} не найден в БД.")

@router.message(Command("unban"))
async def unban_user_cmd(message: types.Message):
    """Разбан пользователя по Telegram ID. Использование: /unban 123456789"""
    async with async_session() as session:
        role = await get_user_role(session, message.from_user.id, message.from_user.username)
        if role != "admin":
            return
            
        args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("⚠️ Использование: `/unban <telegram_id>`", parse_mode="Markdown")
        return
        
    target_id = int(args[1])
    async with async_session() as session:
        from db.crud.user import set_user_ban_status
        success = await set_user_ban_status(session, target_id, False)
    
    if success:
        await message.answer(f"✅ Пользователь {target_id} РАЗБАНЕН. Его объявления снова доступны.")
    else:
        await message.answer(f"❌ Пользователь {target_id} не найден в БД.")



@router.message(Command("add_mod"))
async def cmd_add_mod(message: types.Message):
    async with async_session() as session:
        role = await get_user_role(session, message.from_user.id, message.from_user.username)
        if role != "admin": return
        args = message.text.split()
        if len(args) < 2:
            await message.answer("Использование: /add_mod <@username или ID>")
            return
        
        target = args[1]
        t_id, t_user = (int(target), None) if target.isdigit() else (None, target)
        from db.crud.user import set_user_role
        succ, msg = await set_user_role(session, t_id, t_user, "moderator", True)
        await message.answer(msg)

@router.message(Command("del_mod"))
async def cmd_del_mod(message: types.Message):
    async with async_session() as session:
        role = await get_user_role(session, message.from_user.id, message.from_user.username)
        if role != "admin": return
        args = message.text.split()
        if len(args) < 2: return
        target = args[1]
        t_id, t_user = (int(target), None) if target.isdigit() else (None, target)
        from db.crud.user import set_user_role
        succ, msg = await set_user_role(session, t_id, t_user, "moderator", False)
        await message.answer(msg)

@router.message(Command("admin"))
async def admin_main(message: types.Message):
    """Главный вход в админку"""
    async with async_session() as session:
        role = await get_user_role(session, message.from_user.id, message.from_user.username)
        
    if role not in ("admin", "moderator"):
        await message.answer("⛔️ У вас нет прав доступа.")
        return

    import secrets
    magic_token = secrets.token_urlsafe(32)
    # Идемпотентно сохраняем через API-вызов в Веб Дашборде (так как бот и веб в одном процессе если запущены вместе 
    # Но подождите: бот и веб запущены вместе в одном процессе `dashboard.py`? 
    # В `main.py` или `dashboard.py` они делят память. Можно импортировать magic_tokens!)
    from web.dashboard import magic_tokens
    magic_tokens[magic_token] = {"user_id": message.from_user.id, "role": role}

    kb_buttons = [
        [InlineKeyboardButton(text="🏢 Открыть Веб-Панель", url=f"https://45.12.5.177.nip.io/auth/magic?token={magic_token}")],
        [InlineKeyboardButton(text="👁 Объявления (Модерация)", callback_data="admin_moderation_list")],
        [InlineKeyboardButton(text="📝 Заявки на обучение", callback_data="admin_education_list")],
    ]
    
    if role == "admin":
        kb_buttons.append([InlineKeyboardButton(text="📈 Радар (Арбитраж)", callback_data="admin_radar_menu")])
        kb_buttons.append([InlineKeyboardButton(text="📊 Живая статистика", callback_data="admin_stats")])
        kb_buttons.append([InlineKeyboardButton(text="📢 Массовая рассылка", callback_data="admin_broadcast_init")])
        
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    await message.answer(f"🛠 <b>Панель {'Администратора' if role == 'admin' else 'Модератора'}</b>", parse_mode="HTML", reply_markup=kb)

@router.callback_query(F.data == "admin_moderation_list")
async def moderation_list(callback: types.CallbackQuery):
    async with async_session() as session:
        result = await session.execute(
            select(Listing).options(selectinload(Listing.photos)).where(Listing.status == "moderation")
        )
        listings = result.scalars().all()
    
    if not listings:
        await callback.message.answer("✅ Новых объявлений на модерации нет.")
        await callback.answer()
        return

    await callback.message.answer(f"📋 Найдено объявлений: {len(listings)}")
    
    for l in listings:
        type_str = "💰 ПРОДАЖА" if l.listing_type == "sale" else "📦 АРЕНДА"
        text = (
            f"<b>{type_str}</b> (ID: {l.id})\n"
            f"👤 Юзер ID: {l.user_id}\n"
            f"🏘 Город: {l.city}\n"
            f"📝 <b>{l.title}</b>\n\n"
            f"{l.description}\n\n"
            f"💰 <b>Цена/Условия:</b>\n{l.price_list}"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Одобрить", callback_data=f"admin_approve_{l.id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_{l.id}")
            ]
        ])
        
        if l.photos:
            photo_id = l.photos[0].photo_id
            await callback.message.answer_photo(photo_id, caption=text[:1024], reply_markup=kb, parse_mode="HTML")

            # Если фото больше одного, уведомляем админа
            if len(l.photos) > 1:
                await callback.message.answer(f"📸 У этого объявления еще {len(l.photos)-1} фото.")
        else:
            await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
            
    await callback.answer()

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class AdminBroadcastStates(StatesGroup):
    waiting_for_message = State()

@router.callback_query(F.data == "admin_broadcast_init")
async def broadcast_init(callback: types.CallbackQuery, state: FSMContext):
    async with async_session() as session:
        role = await get_user_role(session, callback.from_user.id, callback.from_user.username)
        if role != "admin":
            await callback.answer("Только для админов", show_alert=True)
            return
            
    await state.set_state(AdminBroadcastStates.waiting_for_message)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")]])
    await callback.message.answer(
        "📝 <b>Режим рассылки</b>\n\nОтправьте сообщение (текст, фото/видео с подписью), которое нужно разослать всем пользователям бота.",
        reply_markup=kb, parse_mode="HTML"
    )
    await callback.answer()

import asyncio
from aiogram.exceptions import TelegramRetryAfter

@router.message(AdminBroadcastStates.waiting_for_message)
async def process_broadcast_message(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("⏳ Начинаю рассылку... Пожалуйста, подождите.")
    
    from db.crud.user import get_all_users
    async with async_session() as session:
        users = await get_all_users(session)
        
    success_count = 0
    fail_count = 0
    
    for u in users:
        # Не отправляем самому себе системного юзера с id 0
        if u.telegram_id == 0:
            continue
            
        try:
            await message.copy_to(chat_id=u.telegram_id)
            success_count += 1
            await asyncio.sleep(0.05) # Защита от FloodLimit
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            try:
                await message.copy_to(chat_id=u.telegram_id)
                success_count += 1
            except Exception:
                fail_count += 1
        except Exception:
            fail_count += 1
            
    await message.answer(f"✅ <b>Рассылка завершена!</b>\nУспешно: {success_count}\nОшибок: {fail_count}", parse_mode="HTML")

import io
from collections import Counter
from datetime import datetime
from aiogram.types import BufferedInputFile

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    async with async_session() as session:
        role = await get_user_role(session, callback.from_user.id, callback.from_user.username)
        if role != "admin":
            await callback.answer("Только для админов", show_alert=True)
            return
        users_count = await session.scalar(select(func.count()).select_from(User))
        listings_count = await session.scalar(select(func.count()).select_from(Listing).where(Listing.status == "active"))
        apps_count = await session.scalar(select(func.count()).select_from(EducationApplication))
        
        # Подсчет примерного дохода (Операторы платят 1000 руб/год)
        operators_count = await session.scalar(
            select(func.count()).select_from(Listing).where(Listing.listing_type == "operator", Listing.status == "active")
        )
        income = (operators_count or 0) * 1000
        
        # Получаем данные для графика (рост юзеров)
        result = await session.execute(select(User.created_at))
        dates = result.scalars().all()
        
    text = (
        "📊 <b>Живая статистика</b>\n\n"
        f"👤 Всего пользователей: {users_count or 0}\n"
        f"📦 Активных объявлений: {listings_count or 0}\n"
        f"📝 Заявок на обучение: {apps_count or 0}\n\n"
        f"💰 <b>Доход платформы:</b> {income} ₽"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back_to_main")]
    ])
    
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg') # Для работы без GUI сервера
        
        # Группируем по датам
        safe_dates = []
        for d in dates:
            if not d: continue
            if isinstance(d, str):
                try: 
                    d = datetime.fromisoformat(d.split('.')[0])
                except Exception: 
                    continue
            if hasattr(d, 'date'):
                safe_dates.append(d.date())
                
        date_counts = Counter(safe_dates)
        sorted_dates = sorted(date_counts.keys())
        
        if sorted_dates:
            cumulative = []
            total = 0
            for d in sorted_dates:
                total += date_counts[d]
                cumulative.append(total)
                
            plt.figure(figsize=(8, 4))
            # d is datetime.date object now
            x_labels = [d.strftime("%m-%d") for d in sorted_dates]
            plt.plot(x_labels, cumulative, marker='o', linestyle='-', color='b')
            plt.fill_between(x_labels, cumulative, color='b', alpha=0.1)
            plt.title("Рост пользователей")
            plt.xlabel("Дата")
            plt.ylabel("Всего пользователей")
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            plt.close()
            
            photo = BufferedInputFile(buf.getvalue(), filename="stats.png")
            await callback.message.delete()
            await callback.message.answer_photo(photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
            await callback.answer()
            return
            
    except Exception as e:
        logger.error(f"Graph generation failed: {e}")
        
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "admin_back_to_main")
async def admin_back_to_main(callback: types.CallbackQuery):
    await callback.message.delete()
    async with async_session() as session:
        role = await get_user_role(session, callback.from_user.id, callback.from_user.username)
    
    import secrets
    magic_token = secrets.token_urlsafe(32)
    from web.dashboard import magic_tokens
    magic_tokens[magic_token] = {"user_id": callback.from_user.id, "role": role}
    
    kb_buttons = [
        [InlineKeyboardButton(text="🏢 Открыть Веб-Панель", url=f"https://45.12.5.177.nip.io/auth/magic?token={magic_token}")],
        [InlineKeyboardButton(text="👁 Объявления (Модерация)", callback_data="admin_moderation_list")],
        [InlineKeyboardButton(text="📝 Заявки на обучение", callback_data="admin_education_list")],
    ]
    if role == "admin":
        kb_buttons.append([InlineKeyboardButton(text="📈 Радар (Арбитраж)", callback_data="admin_radar_menu")])
        kb_buttons.append([InlineKeyboardButton(text="📊 Живая статистика", callback_data="admin_stats")])
        kb_buttons.append([InlineKeyboardButton(text="📢 Массовая рассылка", callback_data="admin_broadcast_init")])
        
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)
    await callback.message.answer(f"🛠 <b>Панель {'Администратора' if role == 'admin' else 'Модератора'}</b>", parse_mode="HTML", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "admin_education_list")
async def admin_education_list(callback: types.CallbackQuery):
    async with async_session() as session:
        result = await session.execute(
            select(EducationApplication).where(EducationApplication.status == "new")
        )
        apps = result.scalars().all()
        
    if not apps:
        await callback.message.answer("✅ Новых заявок на обучение нет.")
        await callback.answer()
        return

    for app in apps:
        text = (
            f"📝 <b>Заявка №{app.id}</b>\n"
            f"👶 Ребенок: {app.child_name}\n"
            f"🎂 Возраст: {app.age}\n"
            f"📞 Телефон: {app.phone}\n"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Обработано", callback_data=f"admin_edu_done_{app.id}")]
        ])
        await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
    
    await callback.answer()

@router.callback_query(F.data.startswith("admin_edu_done_"))
async def admin_edu_done(callback: types.CallbackQuery):
    app_id = int(callback.data.split("_")[3])
    async with async_session() as session:
        await session.execute(
            update(EducationApplication).where(EducationApplication.id == app_id).values(status="processed")
        )
        await session.commit()
    
    current_text = callback.message.text or ""
    await callback.message.edit_text(current_text + "\n\n✅ <b>ОБРАБОТАНО</b>", parse_mode="HTML")
    await callback.answer("Заявка отмечена как обработанная")

async def send_search_alerts(bot, listing):
    from db.base import async_session
    import asyncio
    from aiogram.exceptions import TelegramRetryAfter
    from sqlalchemy import select
    from db.models.search_sub import SearchSubscription
    from db.crud.user import get_user
    
    async with async_session() as session:
        search_text = f"{listing.title} {listing.description} {listing.city}".lower()
        subs = await session.execute(select(SearchSubscription))
        all_subs = subs.scalars().all()
        notified_users = set()
        
        for sub in all_subs:
            if sub.keyword.lower() in search_text and sub.user_id not in notified_users:
                notified_users.add(sub.user_id)
                u = await get_user(session, sub.user_id)
                if u and u.telegram_id:
                    try:
                        await bot.send_message(
                            u.telegram_id,
                            f"🔔 <b>Срочное уведомление!</b>\nПоявилось новое объявление по вашему запросу «{sub.keyword}»:\n\n"
                            f"📦 <b>{listing.title}</b> ({listing.city})\n\n"
                            f"Скорее проверьте раздел Поиск на <b>Аренду</b> или <b>Покупку</b>!",
                            parse_mode="HTML"
                        )
                        await asyncio.sleep(0.05)
                    except TelegramRetryAfter as e:
                        await asyncio.sleep(e.retry_after)
                    except Exception:
                        pass

@router.callback_query(F.data.startswith("admin_approve_"))
async def approve_listing(callback: types.CallbackQuery):
    listing_id = int(callback.data.split("_")[2])
    listing = None
    async with async_session() as session:
        listing = await session.scalar(select(Listing).where(Listing.id == listing_id))
        
        await session.execute(
            update(Listing).where(Listing.id == listing_id).values(status="active")
        )
        from db.crud.log import create_moderation_log
        await create_moderation_log(session, callback.from_user.id, "approve_listing", "listing", listing_id)
        
        await session.commit()
    
    if listing:
        import asyncio
        asyncio.create_task(send_search_alerts(callback.bot, listing))
    
    current_caption = callback.message.caption or ""
    await callback.message.edit_caption(caption=current_caption[:1000] + "\n\n✅ <b>ОДОБРЕНО</b>", parse_mode="HTML")
    await callback.answer("Объявление одобрено!")

@router.callback_query(F.data.startswith("admin_reject_"))
async def reject_listing(callback: types.CallbackQuery):
    listing_id = int(callback.data.split("_")[2])
    async with async_session() as session:
        await session.execute(
            update(Listing).where(Listing.id == listing_id).values(status="rejected")
        )
        from db.crud.log import create_moderation_log
        await create_moderation_log(session, callback.from_user.id, "reject_listing", "listing", listing_id)
        await session.commit()
    
    current_caption = callback.message.caption or ""
    await callback.message.edit_caption(caption=current_caption[:1000] + "\n\n❌ <b>ОТКЛОНЕНО</b>", parse_mode="HTML")
    await callback.answer("Объявление отклонено!")

@router.message(F.forward_from_chat | F.forward_from | F.forward_origin)
async def process_forwarded_post(message: types.Message):
    """Обработка пересланного сообщения из канала партнера"""
    async with async_session() as session:
        role = await get_user_role(session, message.from_user.id, message.from_user.username)
        if role != "admin":
            return
        
    logger.info(f"Admin {message.from_user.id} forwarded a post")
    
    # Пытаемся извлечь текст (из сообщения или подписи к фото)
    text = message.text or message.caption or ""
    
    if not text:
        await message.answer("⚠️ Не удалось извлечь текст из сообщения.")
        return
        
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Добавить в МАГАЗИН", callback_data="add_partner_sale")],
        [InlineKeyboardButton(text="❌ Игнорировать", callback_data="admin_cancel")]
    ])
    
    await message.answer(
        f"📩 <b>Обнаружен пост для импорта:</b>\n\n{text[:200]}...\n\nЖелаете добавить его в магазин?",
        parse_mode="HTML",
        reply_markup=kb
    )

@router.callback_query(F.data == "admin_cancel")
async def admin_cancel(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer("Действие отменено")


@router.callback_query(F.data == "add_partner_sale")
async def add_partner_sale(callback: types.CallbackQuery):
    if not callback.message.reply_to_message:
        await callback.answer("Ошибка: исходное сообщение не найдено (reply).", show_alert=True)
        return

    listing_text = callback.message.reply_to_message.text or callback.message.reply_to_message.caption or ""
    if not listing_text:
        await callback.answer("Ошибка: текст не найден.", show_alert=True)
        return

    from bot.handlers.sales import parse_partner_post
    parsed = parse_partner_post(listing_text)
    
    async with async_session() as session:
        # Получаем системного юзера
        db_user = await session.execute(select(User).where(User.telegram_id == 0))
        user_db_id = db_user.scalar().id if db_user.scalar() else 1
        
        new_listing = Listing(
            user_id=user_db_id,
            category_id=2,
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
        
        orig_msg = callback.message.reply_to_message
        if orig_msg.photo:
            from db.models.listing import ListingPhoto
            session.add(ListingPhoto(listing_id=new_listing.id, photo_id=orig_msg.photo[-1].file_id))
            
        await session.commit()
        
    await callback.message.edit_text(
        f"✅ <b>Импортировано в Магазин!</b>\n\n"
        f"Товар: {parsed['title']}\n"
        f"Цена: {parsed['price']}",
        parse_mode="HTML"
    )
    await callback.answer("Импорт завершен")

