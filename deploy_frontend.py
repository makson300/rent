"""
Deploy frontend to VPS:
1. Pack zip (includes Dockerfile.frontend + updated docker-compose)
2. Upload & unpack
3. Build and start frontend container
4. Update nginx: / -> :3000, /api -> :8000
"""
import paramiko
import os
import time

HOST = "45.12.5.177"
USER = "root"
PASSWORD = "Makson30_"
REMOTE = "/root/rentbot"


def run(ssh, cmd, timeout=300):
    print(f"  > {cmd[:90]}")
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    code = out.channel.recv_exit_status()
    o = out.read().decode("utf-8", errors="replace").strip()
    e = err.read().decode("utf-8", errors="replace").strip()
    if o:
        print("   " + o[:600])
    if e and code != 0:
        print("   ERR:", e[:300])
    return code, o


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=15)
print(f"Connected to {HOST}")

# Upload latest zip
print("\n[1/4] Uploading...")
sftp = ssh.open_sftp()
sftp.put("deploy.zip", "/root/deploy.zip")
sftp.close()
print(f"   Uploaded {os.path.getsize('deploy.zip')} bytes")

# Unpack
print("\n[2/4] Unpacking...")
run(ssh, f"cd /root && unzip -o deploy.zip -d {REMOTE}")

# Build & start frontend (bot/db/redis already healthy)
print("\n[3/4] Building frontend (this takes 2-3 minutes)...")
run(ssh, f"cd {REMOTE} && docker compose build frontend", timeout=600)
run(ssh, f"cd {REMOTE} && docker compose up -d frontend")
print("   Frontend container started, waiting 30s...")
time.sleep(30)
run(ssh, f"cd {REMOTE} && docker compose ps")

# Update nginx routing
print("\n[4/4] Updating nginx routing...")
nginx_conf = """server {
    listen 80;
    server_name _ 45.12.5.177;

    # API and webhook -> Python bot
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /webhook {
        proxy_pass http://127.0.0.1:8000/webhook;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }

    # Everything else -> Next.js dashboard
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300;
    }
}

server {
    listen 443 ssl;
    server_name 45.12.5.177;

    ssl_certificate /etc/nginx/ssl/selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
    }

    location /webhook {
        proxy_pass http://127.0.0.1:8000/webhook;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300;
    }
}"""

# Write nginx config
run(ssh, f"cat > /etc/nginx/sites-available/rentbot << 'NGINXEOF'\n{nginx_conf}\nNGINXEOF")
code, _ = run(ssh, "nginx -t")
if code == 0:
    run(ssh, "systemctl reload nginx")
    print("   Nginx reloaded OK")
else:
    print("   Nginx config error!")

# Final check
print("\n=== FINAL CHECK ===")
run(ssh, f"cd {REMOTE} && docker compose ps")
run(ssh, "curl -s http://localhost/ | head -5")
run(ssh, "curl -sk https://localhost/ | head -5")

ssh.close()
print(f"\nDashboard: http://{HOST}/")
print(f"Dashboard (SSL): https://{HOST}/")
print(f"API: http://{HOST}/api/v1/radar/markers")
