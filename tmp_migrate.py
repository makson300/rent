import sqlite3
try:
    conn = sqlite3.connect('rentbot.db')
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE users ADD COLUMN user_type TEXT DEFAULT 'private'")
    conn.commit()
    conn.close()
    print("Migration successful: user_type column added.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Note: user_type column already exists.")
    else:
        print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
