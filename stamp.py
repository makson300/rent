import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('45.12.5.177', username='root', password='Makson30_')
# For existing schemas, we mark the database as up-to-date with alembic "head" without running the create table scripts.
stdin, stdout, stderr = ssh.exec_command('cd /root/rentbot && docker compose exec bot alembic stamp head')
print("OUT:", stdout.read().decode())
print("ERR:", stderr.read().decode())
