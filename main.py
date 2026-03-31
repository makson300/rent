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
    admin_advisor_router, admin_flight_router, booking_router, contract_router,
    job_router, job_hiring_router, orvd_router, tariffs_router, tenders_router,
    momoa_assessment_router, store_ai_router
)
from bot.handlers.company_profile import router as company_profile_router
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

    from bot.handlers.inline import router as inline_router

    # Подключение роутеров
    logger.info("Registering routers...")
    dp.include_router(inline_router)
    dp.include_router(company_profile_router)
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
    dp.include_router(admin_flight_router)
    dp.include_router(booking_router)
    dp.include_router(contract_router)
    from bot.handlers.job_hiring import router as job_hiring_router
    from bot.handlers.airspace import router as airspace_router
    from bot.handlers.logbook import router as logbook_router
    from bot.handlers.insurance import router as insurance_router
    from bot.handlers.ai_vision import router as ai_vision_router
    from bot.handlers.admin_radar import router as admin_radar_router
    from bot.handlers.fleet_manager import router as fleet_router
    from bot.handlers.escrow import router as escrow_router
    dp.include_router(escrow_router)
    dp.include_router(admin_radar_router)
    dp.include_router(job_hiring_router)
    dp.include_router(airspace_router)
    dp.include_router(logbook_router)
    dp.include_router(insurance_router)
    dp.include_router(ai_vision_router)
    dp.include_router(fleet_router)
    dp.include_router(orvd_router)
    dp.include_router(tariffs_router)
    dp.include_router(tenders_router)
    dp.include_router(momoa_assessment_router)
    dp.include_router(store_ai_router)
    try:
        from bot.commands import set_commands
        await set_commands(bot)
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}")

    # Запуск фонового мониторинга MoMoA
    from bot.services.emergency_monitor import monitor_service
    monitor_task = asyncio.create_task(monitor_service.start())

    # === Инициализация Планировщика Задач (APScheduler) ===
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from datetime import datetime, timedelta
    scheduler = AsyncIOScheduler()
    
    # 1. Запуск парсера hh.ru (раз в 12 часов)
    from db.base import async_session
    from bot.services.hh_parser import process_and_save_vacancies
    async def run_hh_parser(bot_instance):
        try:
            async with async_session() as session:
                new_jobs = await process_and_save_vacancies(bot_instance, session)
                if new_jobs > 0:
                    logger.info(f"HH Parser: added {new_jobs} new vacancies!")
        except Exception as e:
            logger.error(f"HH Parser loop error: {e}")
            
    # 2. ИИ Ежедневного Отчета (Daily Digest)
    from bot.services.smart_moderator import smart_moderator
    async def run_daily_digest(bot_instance):
        try:
            from bot.config import ADMIN_IDS
            async with async_session() as session:
                report = await smart_moderator.generate_daily_report(session)
                for admin_id in filter(None, ADMIN_IDS.split(',')):
                    try:
                        await bot_instance.send_message(admin_id, report, parse_mode="HTML")
                    except Exception as e:
                        logger.error(f"Cannot send digest to admin {admin_id}: {e}")
        except Exception as e:
            logger.error(f"Daily Digest loop error: {e}")
            
    # 3. Радар Госзакупок B2G (ЕИС 44-ФЗ)
    from bot.services.b2g_parser import parse_b2g_tenders
    async def run_b2g_radar(bot_instance):
        try:
            await parse_b2g_tenders(bot_instance)
        except Exception as e:
            logger.error(f"B2G Parser loop error: {e}")

    # Добавляем джобы в планировщик, выполняя первые запуски с задержкой (10-60 сек)
    scheduler.add_job(run_hh_parser, 'interval', hours=12, args=[bot], next_run_time=datetime.now() + timedelta(seconds=10))
    scheduler.add_job(run_daily_digest, 'interval', days=1, args=[bot], next_run_time=datetime.now() + timedelta(seconds=60))
    scheduler.add_job(run_b2g_radar, 'interval', hours=6, args=[bot], next_run_time=datetime.now() + timedelta(seconds=20))
    
    scheduler.start()
    logger.info("APScheduler background tasks started.")

    logger.info("Bot configuration ready.")
    
    import uvicorn
    from web.dashboard import app
    app.state.bot = bot
    app.state.dp = dp
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)

    try:
        me = await bot.get_me()
        logger.info(f"Bot authorized as @{me.username} (ID: {me.id})")
        
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
            asyncio.create_task(dp.start_polling(bot))
            await server.serve()
            
    except Exception as e:
        logger.error(f"Telegram connection error (check Proxy/VPN): {e}")
        logger.info("Starting FastAPI server in FALLBACK mode (Web Map will work, Bot will be offline)...")
        await server.serve()
    finally:
        if not USE_WEBHOOK:
            logger.info("Stopping background tasks...")
            monitor_service.stop()
            monitor_task.cancel()
            scheduler.shutdown()



if __name__ == "__main__":
    logger.info("Starting application...")
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
