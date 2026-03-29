import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("45.12.5.177", username="root", password="Makson30_", timeout=15)
sql = """
CREATE TABLE IF NOT EXISTS moderation_logs (
    id SERIAL PRIMARY KEY,
    admin_id BIGINT REFERENCES users(telegram_id) ON DELETE SET NULL,
    action_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    details TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);
"""
cmd = f"docker exec rentbot-db-1 psql -U botuser -d rentbot -c \"{sql}\""
stdin, stdout, stderr = ssh.exec_command(cmd)
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())
ssh.close()
