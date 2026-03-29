"""
Модерация планов полётов (ИВП) через Telegram-бота.
Админы получают карточку заявки → одобряют/отклоняют → пилот получает push.
"""
import logging
from aiogram import Router, types, Bot, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.orm import selectinload
from db.base import async_session
from db.models.flight_plan import FlightPlan
from db.models.user import User
from bot.config import ADMIN_IDS

router = Router()
logger = logging.getLogger(__name__)


async def notify_admins_flight_plan(bot: Bot, plan_id: int):
    """Отправка карточки нового ИВП всем админам на модерацию."""
    if not ADMIN_IDS:
        return

    async with async_session() as session:
        plan = await session.get(FlightPlan, plan_id, options=[selectinload(FlightPlan.user)])
        if not plan:
            return

    status_emoji = "🚨" if plan.is_emergency else "📡"
    text = (
        f"{status_emoji} <b>Новая заявка на ИВП</b>\n\n"
        f"<b>Пилот:</b> {plan.operator_name or 'Не указан'}\n"
        f"<b>Координаты:</b> {plan.coords}\n"
        f"<b>Радиус:</b> {plan.radius}м\n"
        f"<b>Высота:</b> {plan.alt_min}–{plan.alt_max}м\n"
        f"<b>Время UTC:</b> {plan.time_start} – {plan.time_end}\n"
        f"<b>Задача:</b> {plan.task_desc}\n"
        f"<b>Телефон:</b> {plan.phone}\n\n"
        f"Одобрить этот план полёта?"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить ИВП", callback_data=f"fp_approve_{plan_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"fp_reject_{plan_id}")
        ]
    ])

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text, parse_mode="HTML", reply_markup=kb)
        except Exception as e:
            logger.error(f"Cannot send flight plan to admin {admin_id}: {e}")


@router.callback_query(F.data.startswith("fp_approve_"))
async def approve_flight_plan(callback: types.CallbackQuery):
    """Одобрение плана полёта — пилот получает push-уведомление."""
    plan_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        plan = await session.get(FlightPlan, plan_id, options=[selectinload(FlightPlan.user)])
        if not plan or plan.status not in ("pending", "draft"):
            await callback.answer("Заявка уже обработана.", show_alert=True)
            return

        plan.status = "approved"
        await session.commit()

        # Обновляем сообщение админа
        await callback.message.edit_text(
            f"✅ ИВП #{plan_id} <b>одобрен</b> ({plan.coords}).",
            parse_mode="HTML"
        )

        # Push пилоту
        if plan.user:
            try:
                await callback.bot.send_message(
                    plan.user.telegram_id,
                    f"✅ <b>Ваш план полёта одобрен!</b>\n\n"
                    f"📍 Зона: {plan.coords}\n"
                    f"⏰ Время: {plan.time_start} – {plan.time_end} UTC\n"
                    f"📡 Высота: {plan.alt_min}–{plan.alt_max}м\n\n"
                    f"Вы можете приступать к полётам. Удачи! 🛩",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Cannot notify pilot about approved flight plan: {e}")


@router.callback_query(F.data.startswith("fp_reject_"))
async def reject_flight_plan(callback: types.CallbackQuery):
    """Отклонение плана полёта — пилот получает уведомление."""
    plan_id = int(callback.data.split("_")[2])

    async with async_session() as session:
        plan = await session.get(FlightPlan, plan_id, options=[selectinload(FlightPlan.user)])
        if not plan or plan.status not in ("pending", "draft"):
            await callback.answer("Уже обработано.", show_alert=True)
            return

        plan.status = "rejected"
        await session.commit()

        await callback.message.edit_text(
            f"❌ ИВП #{plan_id} <b>отклонён</b> ({plan.coords}).",
            parse_mode="HTML"
        )

        # Push пилоту
        if plan.user:
            try:
                await callback.bot.send_message(
                    plan.user.telegram_id,
                    f"❌ <b>Ваш план полёта отклонён</b>\n\n"
                    f"📍 Зона: {plan.coords}\n\n"
                    f"Свяжитесь с диспетчером для уточнения причин или скорректируйте параметры заявки.",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Cannot notify pilot about rejected flight plan: {e}")
