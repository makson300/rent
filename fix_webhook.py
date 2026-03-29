"""Fix WEBHOOK_URL on VPS .env and verify."""
import paramiko

HOST = "45.12.5.177"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username="root", password="Makson30_", timeout=15)

def run(cmd):
    _, out, _ = ssh.exec_command(cmd, timeout=30)
    out.channel.recv_exit_status()
    return out.read().decode("utf-8", errors="replace").strip()

# Check current .env
print("Before:")
print(run("grep -E 'WEBHOOK|WEBAPP' /root/rentbot/.env"))

# Fix: add WEBHOOK_URL if missing
run("grep -q 'WEBHOOK_URL' /root/rentbot/.env || echo 'WEBHOOK_URL=https://45.12.5.177/webhook' >> /root/rentbot/.env")
# Update in case it exists but wrong
run("sed -i 's|WEBHOOK_URL=.*|WEBHOOK_URL=https://45.12.5.177/webhook|' /root/rentbot/.env")

print("\nAfter:")
print(run("grep -E 'WEBHOOK|WEBAPP' /root/rentbot/.env"))

# Restart bot to pick up webhook
run("cd /root/rentbot && docker compose restart bot")
print("\nBot restarted.")
ssh.close()
