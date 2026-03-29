import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('45.12.5.177', username='root', password='Makson30_', timeout=15)

stdin, stdout, stderr = ssh.exec_command('ss -tuln && systemctl list-units --type=service')
print("Services:", stdout.read().decode('utf-8')[:1000])

ssh.close()
