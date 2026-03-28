import asyncio
import sys
import os

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from db.base import engine as async_engine, Base
from db.models import * # Импортируем все модели, включая EmergencyAlert

async def migrate_alerts():
    async with async_engine.begin() as conn:
        print("Создание таблиц, если их нет...")
        await conn.run_sync(Base.metadata.create_all)
        print("Готово!")

if __name__ == "__main__":
    asyncio.run(migrate_alerts())
