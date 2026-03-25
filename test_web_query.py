import asyncio
from sqlalchemy import select, func
from db.base import async_session
from db.models.user import User
from db.models.listing import Listing
from db.models.education import EducationApplication

async def test_queries():
    try:
        async with async_session() as session:
            print("Checking users count...")
            users_count = await session.scalar(select(func.count()).select_from(User))
            print(f"Users: {users_count}")
            
            print("Checking listings count...")
            listings_count = await session.scalar(select(func.count()).select_from(Listing).where(Listing.status == "active"))
            print(f"Active Listings: {listings_count}")
            
            print("Checking education applications count...")
            new_apps = await session.scalar(select(func.count()).select_from(EducationApplication).where(EducationApplication.status == "new"))
            print(f"New Apps: {new_apps}")
            
            print("All queries successful.")
    except Exception as e:
        print(f"Query failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_queries())
