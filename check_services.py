"""Final check: verify all endpoints are working."""
import paramiko
import sys

HOST = "45.12.5.177"
USER = "root"
PASSWORD = "Makson30_"
REMOTE = "/root/rentbot"


def run(ssh, cmd, timeout=30):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    out.channel.recv_exit_status()
    # Decode with error replacement to avoid cp1251 issues
    o = out.read().decode("utf-8", errors="replace").strip()
    e = err.read().decode("utf-8", errors="replace").strip()
    return o, e


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=15)

# Check env
o, _ = run(ssh, f"grep -E 'WEBHOOK_URL|WEBAPP_URL' {REMOTE}/.env")
print("=== .env URLs ===")
print(o)

# Check containers
o, _ = run(ssh, f"cd {REMOTE} && docker compose ps --format 'table {{{{.Name}}}}\\t{{{{.Status}}}}'")
print("\n=== Containers ===")
print(o)

# Test HTTP
o, _ = run(ssh, f"curl -s http://{HOST}/health")
print(f"\n=== HTTP /health ===\n{o or '(empty)'}")

# Test HTTPS (ignore cert)
o, _ = run(ssh, f"curl -sk https://{HOST}/health")
print(f"\n=== HTTPS /health ===\n{o or '(empty)'}")

# Bot logs
o, _ = run(ssh, f"cd {REMOTE} && docker compose logs bot --tail=8 2>/dev/null")
print("\n=== Bot logs (last 8) ===")
for line in o.splitlines():
    # strip special chars
    clean = line.encode("ascii", errors="replace").decode()
    print(clean)

ssh.close()
print(f"\n=== URLS ===")
print(f"  HTTP:    http://{HOST}/")
print(f"  HTTPS:   https://{HOST}/")
print(f"  Webhook: https://{HOST}/webhook")
print(f"  Map:     https://{HOST}/map")
