import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('45.12.5.177', username='root', password='Makson30_')
stdin, stdout, stderr = ssh.exec_command('cd /root/rentbot && docker compose logs bot --tail=50')
print(stdout.read().decode())
