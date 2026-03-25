import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.config import BOT_TOKEN, PROXY_URL
from bot.handlers import (
    start_router, profile_router, menu_router, 
    listing_create_router, catalog_router, admin_router, 
    my_listings_router, education_router, sales_router
)
from db.base import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database is ready.")

    session = None
    # Proxy logic
    try:
        if PROXY_URL:
            from aiogram.client.session.aiohttp import AiohttpSession
            if PROXY_URL.startswith("socks"):
                from aiohttp_socks import ProxyConnector
                connector = ProxyConnector.from_url(PROXY_URL)
                session = AiohttpSession(connector=connector)
            else:
                session = AiohttpSession(proxy=PROXY_URL)
            logger.info(f"Using proxy: {PROXY_URL}")
    except Exception as e:
        logger.error(f"Proxy error: {e}. Trying direct connection.")
        session = None

    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    # Подключение роутеров
    logger.info("Registering routers...")
    dp.include_router(admin_router) # Админский роутер первым!
    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(menu_router)
    dp.include_router(listing_create_router)
    dp.include_router(catalog_router)
    dp.include_router(my_listings_router)
    dp.include_router(education_router)
    dp.include_router(sales_router)


    logger.info("Bot starting polling...")
    try:
        me = await bot.get_me()
        logger.info(f"Bot authorized as @{me.username} (ID: {me.id})")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Runtime error: {e}")



if __name__ == "__main__":
    logger.info("Starting application...")
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
