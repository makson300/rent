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

# Список ID администраторов (из конфига и жестко заданные)
ADMIN_IDS = [150190533, 506450098] 

def is_admin(user_id: int) -> bool:
    from bot.config import ADMIN_IDS as CONFIG_ADMIN_IDS
    return user_id in ADMIN_IDS or user_id in CONFIG_ADMIN_IDS

@router.message(Command("me"))
async def cmd_me(message: types.Message):
    """Диагностика ID и прав"""
    status = "✅ АДМИН" if is_admin(message.from_user.id) else "❌ Покупатель"
    await message.answer(f"🆔 Ваш ID: <code>{message.from_user.id}</code>\n🔑 Статус: {status}", parse_mode="HTML")



@router.message(Command("admin"))
async def admin_main(message: types.Message):
    """Главный вход в админку"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ У вас нет прав доступа к этой команде.")
        return

    
    # Auto-add admin ID if not present
    if message.from_user.id not in ADMIN_IDS:
        ADMIN_IDS.append(message.from_user.id)
        logger.info(f"Added new administrator ID: {message.from_user.id} (@{message.from_user.username})")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏢 Открыть Веб-Панель", url="http://127.0.0.1:8000")],
        [InlineKeyboardButton(text="📊 Живая статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👁 Объявления (Модерация)", callback_data="admin_moderation_list")],
        [InlineKeyboardButton(text="📝 Заявки на обучение", callback_data="admin_education_list")]
    ])
    await message.answer("🛠 <b>Панель администратора</b>\n\nВыберите раздел для управления:", parse_mode="HTML", reply_markup=kb)

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

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    async with async_session() as session:
        users_count = await session.scalar(select(func.count()).select_from(User))
        listings_count = await session.scalar(select(func.count()).select_from(Listing).where(Listing.status == "active"))
        apps_count = await session.scalar(select(func.count()).select_from(EducationApplication))
        
    text = (
        "📊 <b>Живая статистика</b>\n\n"
        f"👤 Всего пользователей: {users_count or 0}\n"
        f"📦 Активных объявлений: {listings_count or 0}\n"
        f"📝 Заявок на обучение: {apps_count or 0}"
    )
    await callback.message.answer(text, parse_mode="HTML")
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

@router.callback_query(F.data.startswith("admin_approve_"))
async def approve_listing(callback: types.CallbackQuery):
    listing_id = int(callback.data.split("_")[2])
    async with async_session() as session:
        await session.execute(
            update(Listing).where(Listing.id == listing_id).values(status="active")
        )
        await session.commit()
    
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
        await session.commit()
    
    current_caption = callback.message.caption or ""
    await callback.message.edit_caption(caption=current_caption[:1000] + "\n\n❌ <b>ОТКЛОНЕНО</b>", parse_mode="HTML")
    await callback.answer("Объявление отклонено!")

@router.message(F.forward_from_chat | F.forward_from | F.forward_origin)
async def process_forwarded_post(message: types.Message):
    """Обработка пересланного сообщения из канала партнера"""
    if not is_admin(message.from_user.id):
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

