"""Debug: check nginx config, port 3000, and container status."""
import paramiko

HOST = "45.12.5.177"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username="root", password="Makson30_", timeout=15)


def r(cmd, timeout=30):
    _, o, e = ssh.exec_command(cmd, timeout=timeout)
    o.channel.recv_exit_status()
    return o.read().decode("utf-8", errors="replace").strip()


print("=== Port 3000 direct ===")
print(r("curl -s http://127.0.0.1:3000 | head -5"))

print("\n=== Docker containers ===")
print(r('docker ps'))

print("\n=== Sites-enabled ===")
print(r("ls -la /etc/nginx/sites-enabled/"))

print("\n=== Nginx config (first 15 lines) ===")
print(r("head -20 /etc/nginx/sites-available/rentbot"))

print("\n=== Nginx error log ===")
print(r("tail -5 /var/log/nginx/error.log"))

print("\n=== Frontend container logs ===")
print(r("docker logs rentbot-frontend-1 --tail=15 2>&1"))

ssh.close()
