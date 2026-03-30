import paramiko
import sys

# Ensure stdout uses utf-8 instead of cp1251
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("45.12.5.177", username="root", password="Makson30_", timeout=15)

print("Rebuilding frontend...")
_, out, err = ssh.exec_command("cd /root/rentbot && docker compose up -d --build frontend")
print(out.read().decode('utf-8', 'ignore'))
print(err.read().decode('utf-8', 'ignore'))
    
ssh.close()
