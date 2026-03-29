"""Final system health check of all endpoints."""
import paramiko
import sys

HOST = "45.12.5.177"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username="root", password="Makson30_", timeout=15)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def r(cmd, timeout=15):
    _, o, _ = ssh.exec_command(cmd, timeout=timeout)
    o.channel.recv_exit_status()
    return o.read().decode("utf-8", errors="replace").strip()


print("=" * 55)
print("SKYRENT - PRODUCTION STATUS")
print("=" * 55)

checks = [
    ("HTTP Dashboard (80)",       "curl -s -o/dev/null -w '%{http_code}' http://127.0.0.1/"),
    ("HTTPS Dashboard (443)",     "curl -sk -o/dev/null -w '%{http_code}' https://127.0.0.1/"),
    ("API /health",               "curl -s http://127.0.0.1/health"),
    ("API /api/v1/radar/markers", "curl -s -o/dev/null -w '%{http_code}' http://127.0.0.1/api/v1/radar/markers"),
    ("Map page /map",             "curl -s -o/dev/null -w '%{http_code}' http://127.0.0.1/map"),
    ("Dashboard /dashboard",      "curl -s -o/dev/null -w '%{http_code}' http://127.0.0.1/dashboard"),
    ("Legal Hub",                 "curl -s -o/dev/null -w '%{http_code}' http://127.0.0.1/dashboard/legal"),
]

for name, cmd in checks:
    result = r(cmd)
    ok = "OK" in result or result in ("200", "301", "302")
    icon = "[OK]" if ok else "[!!]"
    print(f"  {icon}  {name:<35} {result}")

print()
print("Containers:")
rows = r('docker ps --format "{{.Names}}|{{.Status}}"')
for row in rows.splitlines():
    name, status = row.split("|", 1)
    icon = "[OK]" if "healthy" in status else "[..] "
    print(f"  {icon}  {name:<30} {status}")

ssh.close()
print()
print("=" * 55)
print(f"  URL:     http://{HOST}/")
print(f"  SSL:     https://{HOST}/")
print(f"  API:     http://{HOST}/api/v1/radar/markers")
print(f"  Webhook: https://{HOST}/webhook")
print("=" * 55)
