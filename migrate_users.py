import sqlite3

print("Starting users migration...")
conn = sqlite3.connect('rentbot.db')
cur = conn.cursor()

queries = [
    'ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0',
    'ALTER TABLE users ADD COLUMN is_moderator BOOLEAN DEFAULT 0',
    'ALTER TABLE users ADD COLUMN volunteer_rescues INTEGER DEFAULT 0',
    'ALTER TABLE users ADD COLUMN referrer_id INTEGER DEFAULT NULL',
    'ALTER TABLE users ADD COLUMN referral_bonus INTEGER DEFAULT 0',
]

for q in queries:
    try:
        cur.execute(q)
        print(f"Success: {q}")
    except Exception as e:
        print(f"Error ({q}): {e}")

conn.commit()
conn.close()
print("Migration complete.")
