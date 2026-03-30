import logging
from aiogram import Router, types, Bot, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from db.base import async_session
from db.models.emergency import EmergencyAlert
from db.models.listing import Listing
from db.models.user import User
from bot.config import ADMIN_IDS

router = Router()
logger = logging.getLogger(__name__)

async def notify_admins_about_alert(bot: Bot, alert_id: int):
    """Отправка карточки заявки админам на модерацию"""
    if not ADMIN_IDS:
        return
        
    async with async_session() as session:
        alert = await session.get(EmergencyAlert, alert_id)
        if not alert:
            return
            
    text = (
        f"🚨 <b>Новая заявка на ЧП (ИИ-Анализ)</b> 🚨\n\n"
        f"<b>Локация:</b> {alert.city}\n"
        f"<b>Тип ЧП:</b> {alert.problem_type}\n"
        f"<b>Оборудование:</b> {alert.required_equipment}\n\n"
        f"<b>Сводка ИИ:</b>\n{alert.ai_summary}\n\n"
        f"<b>Оригинал:</b>\n<i>{alert.raw_text}</i>\n\n"
        f"Одобрить массовую рассылку операторам в городе {alert.city}?"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить и разослать", callback_data=f"alert_approve_{alert_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"alert_reject_{alert_id}")
        ]
    ])
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text, parse_mode="HTML", reply_markup=kb)
        except Exception as e:
            logger.error(f"Cannot send alert to admin {admin_id}: {e}")

@router.callback_query(F.data.startswith("alert_approve_"))
async def approve_alert(callback: types.CallbackQuery):
    alert_id = int(callback.data.split("_")[2])
    
    async with async_session() as session:
        alert = await session.get(EmergencyAlert, alert_id, options=[selectinload(EmergencyAlert.reporter)])
        if not alert or alert.status != "pending":
            await callback.answer("Заявка уже обработана или не найдена.", show_alert=True)
            return
            
        alert.status = "approved"
        await session.commit()
        
        # Ищем операторов в этом городе
        # Оператор - это User, у которого есть Listing в категории 'Операторы' (id=6, но будем искать по имени для безопасности)
        # Упростим: берем всех пользователей, у которых есть листинги в 'Операторы' в городе 'city'
        from db.models.category import Category
        stmt = (
            select(User)
            .join(Listing, Listing.user_id == User.id)
            .join(Category, Listing.category_id == Category.id)
            .where(Category.name == "Операторы")
            # Смягчаем поиск по городу: или точное совпадение (если ИИ угадал правильно), или отправляем хотя бы просто по всей базе, 
            # но в идеале: .where(Listing.city.ilike(f"%{alert.city}%"))
        )
        # В MVP отправим всем операторам, у которых город листинга совпадает
        if alert.city and alert.city != "Неизвестно":
            stmt = stmt.where(Listing.city.ilike(f"%{alert.city}%"))
            
        result = await session.execute(stmt)
        operators = result.scalars().unique().all()
        
        # Умный диспетчер MoMoA: Выделяем ключевое оборудование
        from bot.services.emergency_monitor import monitor_service
        keywords = await monitor_service.get_emergency_keywords(alert.raw_text)
        
        # Рассылка операторам
        notified = 0
        dispatch_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🙋‍♂️ Я готов помочь (Связь)", callback_data=f"alert_respond_{alert_id}")]
        ])
        
        for op in operators:
            # Считываем оборудование
            op_result = await session.execute(select(Listing).where(Listing.user_id == op.id))
            op_listings = op_result.scalars().all()
            all_equipment = " ".join([l.title + " " + (l.description or "") for l in op_listings]).lower()
            
            is_priority = False
            if keywords:
                for k in keywords:
                    if k.lower() in all_equipment:
                        is_priority = True
                        break
                        
            if is_priority:
                dispatch_text = (
                    f"🔴 <b>КРИТИЧЕСКИЙ ПРИОРИТЕТ: ВАШЕ ОБОРУДОВАНИЕ ИДЕАЛЬНО ПОДХОДИТ!</b> 🔴\n\n"
                    f"<b>Локация:</b> {alert.city}\n"
                    f"<b>Ситуация:</b> {alert.problem_type}\n"
                    f"<b>Нужен:</b> {alert.required_equipment}\n\n"
                    f"<i>{alert.raw_text}</i>\n\n"
                    f"Нажмите кнопку ниже для получения контактов штаба."
                )
            else:
                dispatch_text = (
                    f"🚨 <b>КРАСНЫЙ КОД: ТРЕБУЕТСЯ БПЛА</b> 🚨\n\n"
                    f"<b>Локация:</b> {alert.city}\n"
                    f"<b>Ситуация:</b> {alert.problem_type}\n"
                    f"<b>Нужен:</b> {alert.required_equipment}\n\n"
                    f"<i>{alert.raw_text}</i>\n\n"
                    f"Если вы можете помочь прямо сейчас, нажмите кнопку ниже."
                )
                
            try:
                await callback.bot.send_message(op.telegram_id, dispatch_text, parse_mode="HTML", reply_markup=dispatch_kb)
                notified += 1
            except Exception:
                pass
                
        # Обновляем админское сообщение
        await callback.message.edit_text(
            f"✅ Заявка #{alert_id} <b>одобрена</b>.\nРазослано {notified} операторам в радиусе/городе {alert.city}.",
            parse_mode="HTML"
        )
        
        # Уведомляем репортера
        try:
            reporter_id = alert.reporter.telegram_id
            await callback.bot.send_message(
                reporter_id,
                f"✅ Ваша экстренная заявка одобрена модератором. Мы разослали сигнал {notified} операторам БПЛА. "
                f"Если кто-то откликнется, мы пришлем вам его контакты."
            )
        except Exception:
            pass

@router.callback_query(F.data.startswith("alert_reject_"))
async def reject_alert(callback: types.CallbackQuery):
    alert_id = int(callback.data.split("_")[2])
    
    async with async_session() as session:
        alert = await session.get(EmergencyAlert, alert_id, options=[selectinload(EmergencyAlert.reporter)])
        if not alert or alert.status != "pending":
            await callback.answer("Уже обработано.", show_alert=True)
            return
            
        alert.status = "rejected"
        await session.commit()
        
        await callback.message.edit_text(f"❌ Заявка #{alert_id} <b>отклонена</b>.", parse_mode="HTML")
        
        # Уведомляем репортера
        try:
            reporter_id = alert.reporter.telegram_id
            await callback.bot.send_message(
                reporter_id,
                f"❌ Ваша экстренная заявка была отклонена модератором (возможно, не соответствует профилю площадки)."
            )
        except Exception:
            pass

@router.callback_query(F.data.startswith("alert_respond_"))
async def respond_to_alert(callback: types.CallbackQuery):
    alert_id = int(callback.data.split("_")[2])
    
    async with async_session() as session:
        alert = await session.get(EmergencyAlert, alert_id, options=[selectinload(EmergencyAlert.reporter)])
        if not alert:
            await callback.answer("Заявка не найдена.", show_alert=True)
            return
            
        if alert.status != "approved":
            await callback.answer("Заявка уже не активна.", show_alert=True)
            return
            
        # Геймификация: начисляем спасение оператору
        from db.models.reward import Reward
        
        op_user = await session.get(User, callback.from_user.id)
        if op_user:
            op_user.volunteer_rescues += 1
            rescues = op_user.volunteer_rescues
            
            # Логика выдачи наград
            new_reward = None
            if rescues == 1:
                new_reward = Reward(user_id=op_user.id, title="Первое Спасение", description="Доказано делом: готовность прийти на помощь.", emoji="🔰")
            elif rescues == 5:
                new_reward = Reward(user_id=op_user.id, title="Ветеран-Поисковик", description="Успешно завершил 5 экстренных вылетов.", emoji="🎖")
            elif rescues == 10:
                new_reward = Reward(user_id=op_user.id, title="Крылья Надежды", description="Герой Горизонта. Провел 10 гуманитарных миссий.", emoji="🕊")
                
            if new_reward:
                session.add(new_reward)
                # Торжественное уведомление
                try:
                    await callback.bot.send_message(
                        callback.from_user.id,
                        f"🎉 <b>НОВОЕ ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!</b> 🎉\n\n"
                        f"Вам присвоена цифровая награда:\n"
                        f"{new_reward.emoji} <b>{new_reward.title}</b>\n"
                        f"<i>{new_reward.description}</i>\n\n"
                        f"Медаль добавлена в ваш Профиль и повышает доверие заказчиков.",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
                    
            await session.commit()
            
        # Отправляем оператору контакты заявителя
        reporter = alert.reporter
        reporter_contact = f"@{reporter.username}" if reporter.username else f"ТГ: tg://user?id={reporter.telegram_id}"
        await callback.message.answer(
            f"✅ Вы откликнулись на экстренный вызов!\n\n"
            f"👤 <b>Связь с заявителем/штабом:</b>\n{reporter_contact}\n"
            f"Свяжитесь с ним как можно скорее."
        )
        
        # Отправляем заявителю контакты оператора
        try:
            op_contact = f"@{callback.from_user.username}" if callback.from_user.username else f"ТГ: tg://user?id={callback.from_user.id}"
            await callback.bot.send_message(
                reporter.telegram_id,
                f"🚁 <b>ОПЕРАТОР НАЙДЕН!</b>\n\n"
                f"Оператор откликнулся на вашу экстренную заявку:\n"
                f"👤 {op_contact}\n\nСвяжитесь с ним."
            )
        except Exception:
            pass
