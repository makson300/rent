import asyncio
import os
import sys

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, update
from db.base import async_session
from db.models.listing import Listing

async def migrate_prices():
    print("Starting B2B price migration...")
    async with async_session() as session:
        # Обновляем все объявления
        result = await session.execute(
            update(Listing)
            .where(Listing.price_list != "По запросу (B2B)")
            .values(price_list="По запросу (B2B)")
        )
        await session.commit()
        print(f"Migration successful! Updated records.")

if __name__ == "__main__":
    asyncio.run(migrate_prices())
