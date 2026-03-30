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
    logger.info("Running DB Migration for listings...")
    async with async_session() as session:
        try:
            await session.execute(text("ALTER TABLE listings ADD COLUMN is_promoted BOOLEAN DEFAULT FALSE;"))
            logger.info("Added is_promoted column.")
        except Exception as e:
            logger.warning(f"Could not add is_promoted: {e}")
            
        try:
            await session.execute(text("ALTER TABLE listings ADD COLUMN booked_dates VARCHAR;"))
            logger.info("Added booked_dates column.")
        except Exception as e:
            logger.warning(f"Could not add booked_dates: {e}")
            
        await session.commit()
    logger.info("Migration finished.")

if __name__ == "__main__":
    asyncio.run(main())
