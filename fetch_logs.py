import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('45.12.5.177', username='root', password='Makson30_', timeout=15)

cmd = "cd /root/rentbot && docker compose logs bot --tail=20"
stdin, stdout, stderr = ssh.exec_command(cmd)
with open("docker_logs.txt", "w", encoding="utf-8") as f:
    f.write(stdout.read().decode('utf-8', errors="replace"))
ssh.close()
