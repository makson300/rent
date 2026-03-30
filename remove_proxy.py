import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("45.12.5.177", username="root", password="Makson30_", timeout=15)

print("Removing PROXY_URL from VPS .env")
cmd = "sed -i '/PROXY_URL/d' /root/rentbot/.env && docker compose -f /root/rentbot/docker-compose.yml restart bot"
_, out, err = ssh.exec_command(cmd)

print("OUT:", out.read().decode())
print("ERR:", err.read().decode())

ssh.close()
