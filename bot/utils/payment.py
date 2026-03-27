import uuid
from yookassa import Configuration, Payment
from bot.config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY

# Настройка
Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY

async def create_payment(amount: float, description: str, user_id: int):
    """
    Создание платежа в Юкассе
    :param amount: Сумма (RUB)
    :param description: Описание для пользователя
    :param user_id: ID пользователя в нашей БД (для метаданных)
    :return: (payment_id, confirmation_url)
    """
    idempotency_key = str(uuid.uuid4())
    
    res = Payment.create({
        "amount": {
            "value": str(amount),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/SKY_RENT_HUB_BOT" # Ссылка для возврата
        },
        "capture": True,
        "description": description,
        "metadata": {
            "user_id": str(user_id)
        }
    }, idempotency_key)
    
    return res.id, res.confirmation.confirmation_url

async def check_payment_status(payment_id: str):
    """
    Проверка статуса платежа
    :return: status (succeeded, pending, canceled)
    """
    res = Payment.find_one(payment_id)
    return res.status
