"""
Fix frontend deployment:
1. Remove old nginx site (45.12.5.177.nip.io)
2. Rebuild frontend with fixed healthcheck
3. Check frontend logs properly
"""
import paramiko
import os
import time

HOST = "45.12.5.177"
USER = "root"
PASSWORD = "Makson30_"
REMOTE = "/root/rentbot"


def r(ssh, cmd, timeout=300):
    print(f"  > {cmd[:80]}")
    _, o, e = ssh.exec_command(cmd, timeout=timeout)
    code = o.channel.recv_exit_status()
    out = o.read().decode("utf-8", errors="replace").strip()
    err = e.read().decode("utf-8", errors="replace").strip()
    if out:
        print("   " + out[:500])
    if err and code != 0:
        print("   ERR:", err[:300])
    return code, out


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=15)
print(f"Connected to {HOST}")

# 1. Remove old conflicting nginx site
print("\n[1/5] Removing old nginx site...")
r(ssh, "rm -f /etc/nginx/sites-enabled/45.12.5.177.nip.io")
r(ssh, "ls /etc/nginx/sites-enabled/")

# 2. Upload latest zip with fixed docker-compose
print("\n[2/5] Uploading latest code...")
sftp = ssh.open_sftp()
sftp.put("deploy.zip", "/root/deploy.zip")
sftp.close()
print(f"   Uploaded {os.path.getsize('deploy.zip')} bytes")
r(ssh, f"cd /root && unzip -o deploy.zip -d {REMOTE}")

# 3. Stop frontend, rebuild with fixed healthcheck
print("\n[3/5] Rebuilding frontend container...")
r(ssh, f"cd {REMOTE} && docker compose stop frontend && docker compose rm -f frontend")
r(ssh, f"cd {REMOTE} && docker compose build frontend", timeout=600)
r(ssh, f"cd {REMOTE} && docker compose up -d frontend")
print("   Waiting 40s for Next.js startup...")
time.sleep(40)

# 4. Check frontend logs
print("\n[4/5] Frontend logs:")
_, logs = r(ssh, f"docker logs rentbot-frontend-1 --tail=20 2>&1")

# 5. Test ports
print("\n[5/5] Testing services...")
_, out3000 = r(ssh, "curl -s http://127.0.0.1:3000 | head -3")
_, out80 = r(ssh, "curl -s http://127.0.0.1/ | head -5")

# Reload nginx
r(ssh, "nginx -t && systemctl reload nginx")

print("\n=== Final container status ===")
r(ssh, f"cd {REMOTE} && docker compose ps")

print(f"\nPort 3000 response: {out3000[:100] if out3000 else 'EMPTY - Next.js not started!'}")
print(f"Port 80 response:   {out80[:100] if out80 else 'EMPTY'}")

ssh.close()
print(f"\nDashboard URL: http://{HOST}/")
