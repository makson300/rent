"""
Tariff purchase flow:
/tariffs → list of plans → user selects → YooKassa payment link → webhook → credits ad_slots
"""
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from sqlalchemy import select
from db.base import async_session
from db.models.tariff import Tariff
from db.models.user import User
from bot.utils.payment import create_payment, check_payment_status
import logging

logger = logging.getLogger(__name__)
router = Router()

# ─── Тарифы по умолчанию (создаются при первом запуске если таблица пустая) ───
DEFAULT_TARIFFS = [
    {"name": "Старт", "price": 299.0, "duration_days": 30, "listings_count": 1, "type": "rent"},
    {"name": "Бизнес", "price": 799.0, "duration_days": 30, "listings_count": 5, "type": "rent"},
    {"name": "PRO", "price": 1999.0, "duration_days": 30, "listings_count": 20, "type": "rent"},
]

async def ensure_default_tariffs():
    """Создаёт дефолтные тарифы если таблица пустая"""
    async with async_session() as session:
        result = await session.execute(select(Tariff))
        existing = result.scalars().all()
        if not existing:
            for t in DEFAULT_TARIFFS:
                session.add(Tariff(**t))
            await session.commit()
            logger.info("Default tariffs created")

async def get_user_by_telegram_id(telegram_id: int) -> User | None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalars().first()

async def get_all_tariffs():
    async with async_session() as session:
        result = await session.execute(select(Tariff).order_by(Tariff.price))
        return result.scalars().all()

# ─── Команда /tariffs ────────────────────────────────────────────────────────
@router.message(Command("tariffs"))
async def cmd_tariffs(message: Message):
    await ensure_default_tariffs()
    tariffs = await get_all_tariffs()
    if not tariffs:
        await message.answer("Тарифы временно недоступны.")
        return

    text = "💎 <b>Тарифные планы Горизонт</b>\n\nВыберите тариф для размещения объявлений:\n\n"
    buttons = []
    for t in tariffs:
        text += f"📦 <b>{t.name}</b> — {int(t.price)} ₽/мес\n"
        text += f"   ✅ До {t.listings_count} объявлений · {t.duration_days} дней\n\n"
        buttons.append([InlineKeyboardButton(
            text=f"{t.name} — {int(t.price)} ₽",
            callback_data=f"buy_tariff:{t.id}"
        )])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

# ─── Покупка тарифа ──────────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("buy_tariff:"))
async def cb_buy_tariff(callback: CallbackQuery):
    tariff_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        tariff = await session.get(Tariff, tariff_id)

    if not tariff:
        await callback.answer("Тариф не найден", show_alert=True)
        return

    user = await get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Сначала зарегистрируйтесь через /start", show_alert=True)
        return

    try:
        payment_id, pay_url = await create_payment(
            amount=float(tariff.price),
            description=f"Тариф «{tariff.name}» · {tariff.listings_count} объявлений · {tariff.duration_days} дней",
            user_id=user.id
        )

        # Сохраняем pending-платёж в кэш (в памяти, для MVP)
        pending_payments[payment_id] = {
            "user_id": user.id,
            "telegram_id": callback.from_user.id,
            "tariff_id": tariff_id,
            "ad_slots": tariff.listings_count,
        }

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", url=pay_url)],
            [InlineKeyboardButton(text="✅ Я оплатил — проверить", callback_data=f"check_payment:{payment_id}")]
        ])
        await callback.message.edit_text(
            f"🛒 <b>Тариф «{tariff.name}»</b>\n\n"
            f"Сумма: <b>{int(tariff.price)} ₽</b>\n"
            f"Слоты для объявлений: {tariff.listings_count} шт.\n\n"
            f"Нажмите кнопку для оплаты через ЮКасса:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Payment creation error for user {callback.from_user.id}: {e}")
        await callback.answer("Ошибка создания платежа. Попробуйте позже.", show_alert=True)

# ─── In-memory cache для pending платежей (для MVP; в проде — Redis) ──────────
pending_payments: dict = {}

# ─── Проверка статуса оплаты ─────────────────────────────────────────────────
@router.callback_query(F.data.startswith("check_payment:"))
async def cb_check_payment(callback: CallbackQuery):
    payment_id = callback.data.split(":")[1]
    payment_info = pending_payments.get(payment_id)

    if not payment_info:
        await callback.answer("Платёж не найден. Возможно, уже обработан.", show_alert=True)
        return

    try:
        status = await check_payment_status(payment_id)
    except Exception as e:
        logger.error(f"Payment check error {payment_id}: {e}")
        await callback.answer("Ошибка при проверке. Попробуйте позже.", show_alert=True)
        return

    if status == "succeeded":
        # Зачисляем слоты пользователю
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.id == payment_info["user_id"])
            )
            user = result.scalars().first()
            if user:
                user.ad_slots += payment_info["ad_slots"]
                await session.commit()

        pending_payments.pop(payment_id, None)

        await callback.message.edit_text(
            f"✅ <b>Оплата прошла успешно!</b>\n\n"
            f"На ваш аккаунт зачислено <b>{payment_info['ad_slots']}</b> слотов для объявлений.\n\n"
            f"Теперь вы можете размещать объявления через /my_listings.",
            parse_mode="HTML"
        )
    elif status == "pending":
        await callback.answer("⏳ Платёж ещё обрабатывается. Подождите немного и проверьте снова.", show_alert=True)
    elif status == "canceled":
        pending_payments.pop(payment_id, None)
        await callback.answer("❌ Платёж отменён. Попробуйте снова через /tariffs.", show_alert=True)
    else:
        await callback.answer(f"Статус платежа: {status}", show_alert=True)
