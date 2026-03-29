import sqlite3
import os
from datetime import datetime

print("Starting migration...")
conn = sqlite3.connect('rentbot.db')
cur = conn.cursor()

queries = [
    'ALTER TABLE emergency_alerts ADD COLUMN lat FLOAT',
    'ALTER TABLE emergency_alerts ADD COLUMN lng FLOAT',
    'ALTER TABLE jobs ADD COLUMN lat FLOAT',
    'ALTER TABLE jobs ADD COLUMN lng FLOAT',
    'ALTER TABLE flight_plans ADD COLUMN lat FLOAT',
    'ALTER TABLE flight_plans ADD COLUMN lng FLOAT'
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
