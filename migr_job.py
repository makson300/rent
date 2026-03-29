import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("45.12.5.177", username="root", password="Makson30_", timeout=15)

sql = """
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    employer_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    city VARCHAR(100) NOT NULL,
    budget VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS job_responses (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    pilot_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);
"""

cmd = f"docker exec rentbot-db-1 psql -U botuser -d rentbot -c \"{sql}\""
stdin, stdout, stderr = ssh.exec_command(cmd)

print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())

ssh.close()
