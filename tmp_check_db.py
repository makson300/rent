import asyncio
from sqlalchemy import select, func
from db.base import async_session
from db.models.listing import Listing

async def check_db():
    async with async_session() as session:
        result = await session.execute(select(func.count(Listing.id)))
        count = result.scalar()
        print(f"Total listings: {count}")
        
        result = await session.execute(select(Listing).where(Listing.listing_type == "sale"))
        sales = result.scalars().all()
        print(f"Total sales listings: {len(sales)}")
        for sale in sales:
            print(f"- {sale.title} ({sale.status})")

if __name__ == "__main__":
    asyncio.run(check_db())
