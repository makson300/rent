"""Write correct nginx config: port 80 -> Next.js :3000, /api -> bot :8000."""
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
    out = o.read().decode("utf-8", errors="replace").strip()
    err = e.read().decode("utf-8", errors="replace").strip()
    if out:
        print("  " + out[:400])
    return out

# Write nginx config via python file upload instead of heredoc
nginx_conf = r"""server {
    listen 80;
    server_name _ 45.12.5.177;

    # API backend -> Python bot
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

    # Frontend -> Next.js dashboard
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

# Upload config via SFTP (avoids heredoc encoding issues)
sftp = ssh.open_sftp()
with sftp.open("/etc/nginx/sites-available/rentbot", "w") as f:
    f.write(nginx_conf)
sftp.close()
print("Nginx config uploaded via SFTP")

# Test and reload
r("nginx -t")
r("systemctl reload nginx")

# Verify
print("\n=== Testing ===")
print("Port 80:", r("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1/"))
print("Port 80 body:", r("curl -s http://127.0.0.1/ | head -c 150"))
print("Port 443:", r("curl -sk -o /dev/null -w '%{http_code}' https://127.0.0.1/"))
print("API /health:", r("curl -s http://127.0.0.1/health"))

ssh.close()
print(f"\nDone! Dashboard: http://{HOST}/")
print(f"Dashboard SSL: https://{HOST}/")
