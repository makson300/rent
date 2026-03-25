import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot

async def test_bot():
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN not found in .env")
        return
        
    print(f"🤖 Testing with token: {token[:10]}...")
    bot = Bot(token=token)
    try:
        me = await bot.get_me()
        print(f"✅ Bot authorized as @{me.username} (ID: {me.id})")
    except Exception as e:
        print(f"❌ Authorization failed: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_bot())
