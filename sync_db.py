import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.base import engine

async def alter_users_table():
    print("Altering users table to add referrer_id and referral_bonus...")
    async with engine.begin() as conn:
        try:
            await conn.execute(
                __import__('sqlalchemy').text("ALTER TABLE users ADD COLUMN referrer_id INTEGER REFERENCES users(id) ON DELETE SET NULL")
            )
        except Exception as e:
            print(f"referrer_id already exists or error: {e}")
            
        try:
            await conn.execute(
                __import__('sqlalchemy').text("ALTER TABLE users ADD COLUMN referral_bonus INTEGER DEFAULT 0")
            )
        except Exception as e:
            print(f"referral_bonus already exists or error: {e}")
    print("Done!")

if __name__ == "__main__":
    asyncio.run(alter_users_table())
