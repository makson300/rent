import asyncio
import logging
import os
from dotenv import load_dotenv

# Загрузим .env (там DATABASE_URL и API ключи для Gemini)
load_dotenv()
logging.basicConfig(level=logging.INFO)

async def run_b2g_test():
    logging.info("Starting B2G Parser Test...")
    try:
        import db.models.reward
    except ImportError:
        pass
    from bot.services.b2g_parser import parse_b2g_tenders
    
    # Запускаем парсер, передав None вместо реального Bot, 
    # так как внутри send_message обернут в try-except.
    await parse_b2g_tenders(None)
    logging.info("B2G Parser Test Finished!")

if __name__ == "__main__":
    asyncio.run(run_b2g_test())
