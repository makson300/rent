import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("45.12.5.177", username="root", password="Makson30_", timeout=15)
cmd = "docker exec rentbot-db-1 psql -U botuser -d rentbot -c 'ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE; ALTER TABLE users ADD COLUMN is_moderator BOOLEAN DEFAULT FALSE;'"
stdin, stdout, stderr = ssh.exec_command(cmd)
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())
ssh.close()
