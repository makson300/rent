"""
core/notifications.py — Мульти-канальные уведомления Горизонт
================================================================
Приоритет: Telegram → Max Messenger (резерв на случай блокировки РКН).
Supports:
  - Exponential backoff retry
  - Graceful fallback to Max если Telegram недоступен
  - notify_user / notify_admin / notify_bulk
"""
import asyncio
import logging
from typing import Any

import httpx

from core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Константы
# ---------------------------------------------------------------------------
_MAX_API_URL = "https://api.max-messenger.ru/v1/webhook/send"
_MAX_TOKEN   = getattr(settings, "MAX_API_TOKEN", "")
_ADMIN_ID    = getattr(settings, "ADMIN_ID", None)

_RETRY_ATTEMPTS = 3
_RETRY_BASE_DELAY = 0.5  # секунды


# ---------------------------------------------------------------------------
# Низкоуровневые отправщики
# ---------------------------------------------------------------------------

async def _send_tg(bot: Any, chat_id: int, text: str, parse_mode: str = "HTML") -> bool:
    """Отправка в Telegram с экспоненциальным backoff."""
    for attempt in range(_RETRY_ATTEMPTS):
        try:
            await bot.send_message(chat_id, text, parse_mode=parse_mode)
            return True
        except Exception as exc:
            delay = _RETRY_BASE_DELAY * (2 ** attempt)
            logger.warning(
                "[TG] Attempt %d/%d failed for chat_id=%d: %s. Retry in %.1fs",
                attempt + 1, _RETRY_ATTEMPTS, chat_id, exc, delay,
            )
            if attempt < _RETRY_ATTEMPTS - 1:
                await asyncio.sleep(delay)

    logger.error("[TG] All %d attempts failed for chat_id=%d", _RETRY_ATTEMPTS, chat_id)
    return False


async def _send_max(chat_id: int, text: str) -> bool:
    """
    Отправка через Max Messenger (корпоративный мессенджер / резерв РКН).
    В продакшне: реальный httpx.AsyncClient POST к API Макса.
    """
    if not _MAX_TOKEN:
        logger.debug("[MAX] MAX_API_TOKEN not configured, skipping")
        return False

    payload = {
        "token": _MAX_TOKEN,
        "target_id": chat_id,
        "message": text,
        "priority": "high",
    }

    for attempt in range(_RETRY_ATTEMPTS):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(_MAX_API_URL, json=payload)
                resp.raise_for_status()
            logger.info("[MAX] Delivered to chat_id=%d", chat_id)
            return True
        except Exception as exc:
            delay = _RETRY_BASE_DELAY * (2 ** attempt)
            logger.warning(
                "[MAX] Attempt %d/%d failed for chat_id=%d: %s. Retry in %.1fs",
                attempt + 1, _RETRY_ATTEMPTS, chat_id, exc, delay,
            )
            if attempt < _RETRY_ATTEMPTS - 1:
                await asyncio.sleep(delay)

    logger.error("[MAX] All %d attempts failed for chat_id=%d", _RETRY_ATTEMPTS, chat_id)
    return False


# ---------------------------------------------------------------------------
# Публичный API
# ---------------------------------------------------------------------------

async def send_to_telegram(
    bot: Any,
    chat_id: int,
    text: str,
    parse_mode: str = "HTML",
) -> bool:
    """Прямая отправка в Telegram (без фоллбека)."""
    return await _send_tg(bot, chat_id, text, parse_mode)


async def notify_user(
    bot: Any | None,
    user_id: int,
    text: str,
    *,
    channels: list[str] | None = None,
) -> bool:
    """
    Отказоустойчивая мульти-канальная отправка.

    channels: список каналов по приоритету, по умолчанию ["tg", "max"].
    Если TG недоступен — автоматический фоллбек на Max.
    """
    if channels is None:
        channels = ["tg", "max"]

    tg_ok = False

    if "tg" in channels and bot is not None:
        tg_ok = await _send_tg(bot, user_id, text)
        if tg_ok:
            return True
        logger.warning("[Notify] TG failed for user %d — escalating to MAX", user_id)

    if "max" in channels:
        return await _send_max(user_id, text)

    return tg_ok


async def notify_admin(
    bot: Any | None,
    text: str,
    *,
    channels: list[str] | None = None,
) -> bool:
    """Уведомление администратора платформы (ADMIN_ID из .env)."""
    if not _ADMIN_ID:
        logger.error("[Notify] ADMIN_ID not configured in settings")
        return False
    return await notify_user(bot, int(_ADMIN_ID), text, channels=channels)


async def notify_bulk(
    bot: Any | None,
    user_ids: list[int],
    text: str,
    *,
    channels: list[str] | None = None,
    delay_between: float = 0.05,
) -> dict[int, bool]:
    """
    Массовая рассылка по списку пользователей.
    Возвращает словарь {user_id: success}.
    Использует небольшую задержку чтобы не триггерить rate limit TG (30 msg/s).
    """
    results: dict[int, bool] = {}
    for uid in user_ids:
        results[uid] = await notify_user(bot, uid, text, channels=channels)
        if delay_between > 0:
            await asyncio.sleep(delay_between)
    return results
