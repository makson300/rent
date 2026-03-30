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
    logger.info("Running DB Migration for jobs...")
    async with async_session() as session:
        try:
            await session.execute(text("ALTER TABLE jobs ADD COLUMN source_url VARCHAR(500);"))
            logger.info("Added source_url column.")
        except Exception as e:
            logger.warning(f"Could not add source_url: {e}")
            
        try:
            await session.execute(text("ALTER TABLE jobs ADD COLUMN external_id VARCHAR(100);"))
            logger.info("Added external_id column.")
        except Exception as e:
            logger.warning(f"Could not add external_id: {e}")
            
        await session.commit()
    logger.info("Migration finished.")

if __name__ == "__main__":
    asyncio.run(main())
