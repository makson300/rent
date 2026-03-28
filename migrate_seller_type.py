import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('rentbot.db')
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(listings)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'seller_type' not in columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN seller_type VARCHAR(20) DEFAULT 'individual'")
            print("Migration: Added 'seller_type' to 'listings'.")
        else:
            print("Migration: 'seller_type' already exists in 'listings'.")
            
        if 'is_sponsored' not in columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN is_sponsored BOOLEAN DEFAULT 0")
            print("Migration: Added 'is_sponsored' to 'listings'.")
        else:
            print("Migration: 'is_sponsored' already exists in 'listings'.")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Direct sqlite3 migration error: {e}")

if __name__ == "__main__":
    migrate()
