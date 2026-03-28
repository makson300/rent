import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'rentbot.db')
try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tables:", cur.fetchall())
    
    # Try fetching from users table
    try:
        cur.execute("SELECT telegram_id, username FROM users ORDER BY created_at DESC LIMIT 5")
        print("Users table:", cur.fetchall())
    except Exception as e:
        print("users error:", e)
        
    # Try fetching from user table
    try:
        cur.execute("SELECT telegram_id, username FROM user ORDER BY created_at DESC LIMIT 5")
        print("user table:", cur.fetchall())
    except Exception as e:
        print("user error:", e)
        
except Exception as e:
    print("General Error:", e)
