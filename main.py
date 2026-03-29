import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from bot.config import BOT_TOKEN, PROXY_URL, REDIS_URL, USE_WEBHOOK, WEBHOOK_URL, WEBHOOK_SECRET
from bot.handlers import (
    start_router, profile_router, menu_router, 
    listing_create_router, catalog_router, admin_router, 
    admin_moderation_router, my_listings_router, 
    education_router, sales_router, packages_router,
    search_router, seller_profile_router, operators_router,
    support_router, emergency_router, admin_emergency_router,
    admin_advisor_router, booking_router, contract_router,
    job_router, job_hiring_router
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
    
    if REDIS_URL:
        storage = RedisStorage.from_url(REDIS_URL)
        logger.info(f"Using Redis storage: {REDIS_URL}")
    else:
        storage = MemoryStorage()
        logger.info("Using MemoryStorage")
        
    dp = Dispatcher(storage=storage)

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
    dp.include_router(operators_router)
    dp.include_router(search_router)
    dp.include_router(support_router)
    dp.include_router(emergency_router)
    dp.include_router(admin_emergency_router)
    dp.include_router(admin_advisor_router)
    dp.include_router(booking_router)
    dp.include_router(contract_router)
    dp.include_router(job_router)
    dp.include_router(job_hiring_router)

    # Установка команд меню
    from bot.commands import set_commands
    await set_commands(bot)

    # Запуск фонового мониторинга MoMoA
    from bot.services.emergency_monitor import monitor_service
    monitor_task = asyncio.create_task(monitor_service.start())

    logger.info("Bot configuration ready.")
    try:
        me = await bot.get_me()
        logger.info(f"Bot authorized as @{me.username} (ID: {me.id})")
        
        import uvicorn
        from web.dashboard import app
        app.state.bot = bot
        app.state.dp = dp
        config = uvicorn.Config(app=app, host="0.0.0.0", port=8000)
        server = uvicorn.Server(config)

        if USE_WEBHOOK:
            logger.info(f"Setting webhook to {WEBHOOK_URL}...")
            webhook_kwargs = {"url": WEBHOOK_URL, "drop_pending_updates": True}
            if WEBHOOK_SECRET:
                webhook_kwargs["secret_token"] = WEBHOOK_SECRET
            await bot.set_webhook(**webhook_kwargs)
            logger.info("Webhook set. Starting FastAPI server...")
            await server.serve()
        else:
            logger.info("Bot starting polling and FastAPI server concurrently...")
            await bot.delete_webhook(drop_pending_updates=True)
            asyncio.create_task(server.serve())
            await dp.start_polling(bot)
            
    except Exception as e:
        logger.error(f"Runtime error: {e}")
    finally:
        if not USE_WEBHOOK:
            logger.info("Stopping background tasks...")
            monitor_service.stop()
            monitor_task.cancel()



if __name__ == "__main__":
    logger.info("Starting application...")
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
