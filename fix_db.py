import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('45.12.5.177', username='root', password='Makson30_')

sql = """
CREATE TABLE IF NOT EXISTS pilot_certificates (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    cert_type VARCHAR(255) NOT NULL,
    document_number VARCHAR(100),
    issue_date TIMESTAMP,
    expiry_date TIMESTAMP,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cert_user FOREIGN KEY(user_id) REFERENCES users(telegram_id) ON DELETE CASCADE
);
"""

stdin, stdout, stderr = ssh.exec_command(f'docker exec rentbot-db-1 psql -U botuser -d rentbot -c "{sql}"')
print('OUT:', stdout.read().decode())
print('ERR:', stderr.read().decode())
