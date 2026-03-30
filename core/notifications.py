import logging
import httpx
import asyncio
from typing import Optional, List
from core.config import settings

logger = logging.getLogger(__name__)

# Mock for Max Messenger Webhook SDK
MAX_API_URL = "https://api.max-messenger.ru/v1/webhook/send"
MAX_TOKEN = getattr(settings, "MAX_API_TOKEN", "mock_max_token_123")

async def send_to_telegram(bot, chat_id: int, text: str, parse_mode: str = "HTML") -> bool:
    try:
        await bot.send_message(chat_id, text, parse_mode=parse_mode)
        return True
    except Exception as e:
        logger.error(f"[Notifications] Telegram send error to {chat_id}: {e}")
        return False

async def send_to_max(chat_id: int, text: str) -> bool:
    """
    Отправка в корпоративный/резервный мессенджер Макс.
    """
    try:
        payload = {
            "token": MAX_TOKEN,
            "target_id": chat_id, # Маппинг tg_id -> max_id происходит на стороне Макса или в БД
            "message": text,
            "priority": "high"
        }
        
        # В реальной среде это будет httpx.post(MAX_API_URL, json=payload, timeout=5.0)
        # Пока мы эмулируем успешный ответ шлюза:
        await asyncio.sleep(0.1) # Network latency mock
        logger.info(f"[Notifications] MAX Messenger: Successfully sent alert to {chat_id}")
        return True
    except Exception as e:
        logger.error(f"[Notifications] MAX send error to {chat_id}: {e}")
        return False

async def notify_user(bot, user_id: int, text: str, channels: List[str] = ["tg", "max"]) -> bool:
    """
    Отказоустойчивая мульти-канальная отправка.
    Сначала пробует TG. Если падает или указан "max", отправляет в Max.
    """
    success = False
    
    if "tg" in channels and bot:
        success = await send_to_telegram(bot, user_id, text)
        
    # Если Telegram упал (блокировка РКН / Таймаут) или Max запрошен явно как дубликат
    if ("max" in channels) or (not success and "tg" in channels):
        logger.warning(f"[Notifications] Escalating to MAX Messenger for user {user_id}")
        max_success = await send_to_max(user_id, text)
        success = success or max_success
        
    return success

async def notify_admin(bot, text: str, channels: List[str] = ["tg", "max"]) -> bool:
    """
    Уведомление Штаба/Админа.
    Реагирует на настройки `settings.ADMIN_ID`.
    """
    admin_id = getattr(settings, "ADMIN_ID", None)
    if not admin_id:
        logger.error("[Notifications] ADMIN_ID not configured")
        return False
        
    return await notify_user(bot, admin_id, text, channels=channels)
