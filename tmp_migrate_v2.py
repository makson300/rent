import sqlite3
import asyncio
from db.base import init_db

async def migrate():
    # 1. Добавляем КОЛОНКИ в существующие таблицы через sqlite3 напрямую ДО init_db
    try:
        conn = sqlite3.connect('rentbot.db')
        cursor = conn.cursor()
        
        # Проверяем наличие колонки ad_slots в users
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'ad_slots' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN ad_slots INTEGER DEFAULT 0")
            print("Migration: Added 'ad_slots' to 'users'.")
        else:
            print("Migration: 'ad_slots' already exists in 'users'.")
            
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Direct sqlite3 migration error: {e}")

    # 2. Теперь инициализируем БД через SQLAlchemy (это создаст новые ТАБЛИЦЫ, например reviews)
    await init_db()
    print("Schema migration via SQLAlchemy completed.")

if __name__ == "__main__":
    asyncio.run(migrate())
