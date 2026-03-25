import uuid
import asyncio
from yookassa import Configuration, Payment
from bot.config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY

Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY

async def create_payment(amount: float, description: str, return_url: str):
    """Создает платеж в ЮKassa (синхронный SDK оборачиваем в thread)"""
    idempotency_key = str(uuid.uuid4())
    payment = await asyncio.to_thread(
        Payment.create,
        {
            "amount": {
                "value": str(amount),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": description
        },
        idempotency_key
    )
    return payment

async def get_payment_status(payment_id: str):
    """Проверяет статус платежа"""
    payment = await asyncio.to_thread(Payment.find_one, payment_id)
    return payment.status
