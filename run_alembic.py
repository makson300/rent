import paramiko
import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("45.12.5.177", username="root", password="Makson30_", timeout=15)

# Wait a little for DB and Bot container to fully sync up
cmd = "cd /root/rentbot && docker exec rentbot-bot-1 bash -c 'alembic revision --autogenerate -m \"Add Wallet models\" && alembic upgrade head'"

print("Running Alembic DB Migration on Remote Server...")
_, stdout, stderr = ssh.exec_command(cmd)

for line in stdout:
    print(line.strip())
for line in stderr:
    print("ERR:", line.strip())

ssh.close()
