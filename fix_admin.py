import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('45.12.5.177', username='root', password='Makson30_', timeout=15)

cmd = "sed -i 's/127.0.0.1/45.12.5.177/g' /root/rentbot/bot/handlers/admin.py && cd /root/rentbot && docker compose restart bot"
stdin, stdout, stderr = ssh.exec_command(cmd)
print("Response:", stdout.read().decode('utf-8'))
ssh.close()
