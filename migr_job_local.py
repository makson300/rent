import sqlite3

conn = sqlite3.connect("rentbot.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employer_id INTEGER NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    city VARCHAR(100) NOT NULL,
    budget VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS job_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    pilot_id INTEGER NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
)
""")

conn.commit()
conn.close()
print("Local tables created.")
