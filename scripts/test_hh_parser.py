import asyncio
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.base import async_session, init_db
from bot.services.hh_parser import process_and_save_vacancies

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dummy bot class
class DummyBot:
    async def send_message(self, chat_id, text, **kwargs):
        # We don't want to actually send messages during this pure logic test to real users.
        logger.info(f"Would send to {chat_id}: {text[:50]}...")

async def main():
    logger.info("Initializing DB for test...")
    await init_db()
    
    bot = DummyBot()
    
    logger.info("Running HH API test...")
    async with async_session() as session:
        added = await process_and_save_vacancies(bot, session)
        logger.info(f"Test completed. Added {added} new vacancies from HH.ru!")

if __name__ == "__main__":
    asyncio.run(main())
