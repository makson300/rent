import asyncio
import sys
import os

# Добавление корневой директории в пути поиска (для импорта db)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.base import init_db

async def main():
    print("⏳ Инициализация базы данных...")
    try:
        await init_db()
        print("✅ Таблицы созданы/обновлены успешно.")
    except Exception as e:
        print(f"❌ Ошибка при инициализации: {e}")

if __name__ == "__main__":
    asyncio.run(main())
