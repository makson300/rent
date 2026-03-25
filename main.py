import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import BOT_TOKEN, PROXY_URL
from bot.handlers import (
    start_router, profile_router, menu_router, 
    listing_create_router, catalog_router, admin_router, 
    my_listings_router, education_router
)
from db.base import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Инициализация базы данных...")
    await init_db()

    session = None
    if PROXY_URL:
        from aiogram.client.session.aiohttp import AiohttpSession
        if PROXY_URL.startswith("socks"):
            from aiohttp_socks import ProxyConnector
            connector = ProxyConnector.from_url(PROXY_URL)
            session = AiohttpSession(connector=connector)
        else:
            session = AiohttpSession(proxy=PROXY_URL)
        logger.info(f"Подключение через прокси: {PROXY_URL}")

    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    # Подключение роутеров
    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(menu_router)
    dp.include_router(listing_create_router)
    dp.include_router(catalog_router)
    dp.include_router(admin_router)
    dp.include_router(my_listings_router)
    dp.include_router(education_router)

    logger.info("Бот запущен и слушает сообщения (polling)")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
