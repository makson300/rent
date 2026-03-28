import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'rentbot.db')
try:
    conn = sqlite3.connect(db_path)
    conn.execute('ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT 0')
    conn.commit()
    print("Column is_banned added successfully.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Column already exists.")
    else:
        print("Error:", e)
finally:
    conn.close()
