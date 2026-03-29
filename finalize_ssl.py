"""Finalize SSL setup: update .env URLs, restart bot, verify all services."""
import paramiko
import time

HOST = "45.12.5.177"
USER = "root"
PASSWORD = "Makson30_"
REMOTE = "/root/rentbot"
BASE_URL = f"https://{HOST}"


def run(ssh, cmd, timeout=60):
    print(f"  > {cmd[:80]}")
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    out.channel.recv_exit_status()
    o = out.read().decode().strip()
    e = err.read().decode().strip()
    if o:
        print("   ", o[:500])
    if e and len(e) > 0:
        print("   ERR:", e[:200])
    return o


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=15)
print(f"Connected to {HOST}")

# Update .env on VPS
print("\n[1/4] Updating .env URLs...")
run(ssh, fr"sed -i 's|WEBHOOK_URL=.*|WEBHOOK_URL={BASE_URL}/webhook|' {REMOTE}/.env")
run(ssh, fr"sed -i 's|WEBAPP_URL=.*|WEBAPP_URL={BASE_URL}|' {REMOTE}/.env")
run(ssh, f"grep -E 'WEBHOOK_URL|WEBAPP_URL' {REMOTE}/.env")

# Restart bot
print("\n[2/4] Restarting bot container...")
run(ssh, f"cd {REMOTE} && docker compose restart bot", timeout=30)
time.sleep(10)

# Check nginx
print("\n[3/4] Checking nginx...")
run(ssh, "systemctl status nginx --no-pager | head -6")
run(ssh, f"curl -sk {BASE_URL}/health")
run(ssh, f"curl -s http://{HOST}/health")

# Check containers + bot logs
print("\n[4/4] Final status...")
run(ssh, f"cd {REMOTE} && docker compose ps")
run(ssh, f"cd {REMOTE} && docker compose logs bot --tail=10")

ssh.close()
print(f"\n=== DONE ===")
print(f"API (HTTP):  http://{HOST}/")
print(f"API (HTTPS): {BASE_URL}/")
print(f"Webhook:     {BASE_URL}/webhook")
print(f"Map:         {BASE_URL}/map")
print(f"\nNOTE: Domain skyrent.pro not yet pointed here.")
print(f"When DNS is ready, run: certbot --nginx -d skyrent.pro")
