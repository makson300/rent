import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.base import async_session, init_db
from db.models.user import User
from db.models.reward import Reward
from db.models.emergency import EmergencyAlert
from sqlalchemy import select

async def main():
    print("Initializing Database (this will create new tables like 'rewards')...")
    await init_db()
    
    async with async_session() as session:
        print("Checking if 'rewards' table is accessible...")
        # Just a simple query to ensure ORM maps it
        res = await session.execute(select(Reward).limit(1))
        print("Reward query successful. Table exists.")
        
        # Test imports for the new features
        from bot.handlers.store_ai import store_main
        from bot.handlers.education import start_edu_test
        from bot.handlers.profile import show_profile
        from bot.handlers.admin_emergency import respond_to_alert
        
        print("All new handler imports successful!")
        
    print("Testing complete. Ready for production.")

if __name__ == "__main__":
    asyncio.run(main())
