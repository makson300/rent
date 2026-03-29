"""Minimal check: test port 3000 and nginx, no docker logs."""
import paramiko
import sys

HOST = "45.12.5.177"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username="root", password="Makson30_", timeout=15)

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def r(cmd, timeout=30):
    _, o, e = ssh.exec_command(cmd, timeout=timeout)
    o.channel.recv_exit_status()
    return o.read().decode("utf-8", errors="replace").strip()


# Container status (no logs)
print("=== Containers ===")
print(r('docker ps --format "{{.Names}}\t{{.Status}}"'))

# Direct test port 3000
print("\n=== Port 3000 direct ===")
print(r("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3000/"))

# Port 3000 body
print("\n=== Port 3000 body (first 200 chars) ===")
print(r("curl -s http://127.0.0.1:3000/ | head -c 200"))

# Nginx test
print("\n=== Nginx port 80 ===")
print(r("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1/"))

print("\n=== Nginx sites-enabled ===")
print(r("ls /etc/nginx/sites-enabled/"))

# Reload nginx just in case
r("systemctl reload nginx")

ssh.close()
print("\n=== URLs ===")
print(f"http://{HOST}/")
print(f"https://{HOST}/")
