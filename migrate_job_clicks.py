import asyncio
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.base import async_session
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Running DB Migration for jobs clicks...")
    async with async_session() as session:
        try:
            await session.execute(text("ALTER TABLE jobs ADD COLUMN clicks_count INTEGER DEFAULT 0;"))
            logger.info("Added clicks_count column.")
        except Exception as e:
            logger.warning(f"Could not add clicks_count: {e}")
            
        await session.commit()
    logger.info("Migration finished.")

if __name__ == "__main__":
    asyncio.run(main())
