import uuid
import logging
from yookassa import Configuration, Payment
from bot.config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY

logger = logging.getLogger(__name__)

if YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY:
    Configuration.account_id = YOOKASSA_SHOP_ID
    Configuration.secret_key = YOOKASSA_SECRET_KEY

async def create_payment(amount: float, description: str, return_url: str):
    """Создание платежа в ЮKassa"""
    if not Configuration.account_id:
        logger.error("Yookassa credentials not set")
        return None

    idempotency_key = str(uuid.uuid4())
    try:
        payment = Payment.create({
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": description
        }, idempotency_key)

        return payment
    except Exception as e:
        logger.error(f"Payment creation error: {e}")
        return None

async def check_payment_status(payment_id: str):
    """Проверка статуса платежа"""
    try:
        payment = Payment.find_one(payment_id)
        return payment.status
    except Exception as e:
        logger.error(f"Payment status check error: {e}")
        return None
