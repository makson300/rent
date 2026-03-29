"""
Nginx + SSL setup on VPS.
- Installs nginx
- Configures reverse proxy to bot on port 8000
- Gets Let's Encrypt SSL cert (or falls back to self-signed)
- Updates .env WEBHOOK_URL / WEBAPP_URL
- Reloads bot with new config
"""
import paramiko
import time

HOST = "45.12.5.177"
USER = "root"
PASSWORD = "Makson30_"
REMOTE = "/root/rentbot"
DOMAIN = "skyrent.pro"  # Change to actual domain if different


def run(ssh, cmd, timeout=120, ok_nonzero=False):
    print(f"  > {cmd[:90]}")
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    code = out.channel.recv_exit_status()
    o = out.read().decode().strip()
    e = err.read().decode().strip()
    if o:
        print("   ", o[:500])
    if e and (code != 0 or "error" in e.lower()):
        print("   [ERR]", e[:400])
    return code, o, e


def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=15)
    print(f"Connected to {HOST}")

    # 1. Check if domain resolves to our IP
    print("\n[1/5] Checking DNS for domain...")
    code, dns_out, _ = run(ssh, f"dig +short {DOMAIN} 2>/dev/null || nslookup {DOMAIN} 2>/dev/null | grep Address | tail -1")
    domain_points_here = HOST in dns_out
    print(f"   DNS result: '{dns_out}' | Points to this server: {domain_points_here}")

    # 2. Install nginx and certbot
    print("\n[2/5] Installing nginx, certbot...")
    run(ssh, "apt-get install -y -qq nginx certbot python3-certbot-nginx", timeout=120)
    run(ssh, "ufw allow 80/tcp")
    run(ssh, "ufw allow 443/tcp")

    # 3. Write nginx config
    print("\n[3/5] Writing nginx config...")
    # Use domain if it resolves here, else use IP directly
    server_name = DOMAIN if domain_points_here else "_"

    nginx_conf = f"""server {{
    listen 80;
    server_name {server_name} {HOST};

    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }}

    # Telegram webhook
    location /webhook {{
        proxy_pass http://127.0.0.1:8000/webhook;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 60;
    }}
}}"""

    # Write config file via heredoc
    run(ssh, f"cat > /etc/nginx/sites-available/rentbot <<'NGINXEOF'\n{nginx_conf}\nNGINXEOF")
    run(ssh, "ln -sf /etc/nginx/sites-available/rentbot /etc/nginx/sites-enabled/rentbot")
    run(ssh, "rm -f /etc/nginx/sites-enabled/default")
    run(ssh, "nginx -t")
    run(ssh, "systemctl restart nginx")
    run(ssh, "systemctl enable nginx")
    print("   Nginx configured and started")

    # 4. Get SSL cert
    print(f"\n[4/5] Getting SSL certificate...")
    if domain_points_here:
        print(f"   Domain {DOMAIN} → getting Let's Encrypt cert...")
        code, _, certerr = run(ssh,
            f"certbot --nginx -d {DOMAIN} --non-interactive --agree-tos "
            f"--email admin@{DOMAIN} --redirect 2>&1",
            timeout=120
        )
        if code == 0:
            base_url = f"https://{DOMAIN}"
            print(f"   ✅ SSL cert obtained! URL: {base_url}")
        else:
            print(f"   ⚠️  Let's Encrypt failed. Falling back to self-signed cert.")
            base_url = f"https://{HOST}"
            setup_self_signed(ssh, HOST)
    else:
        print(f"   Domain {DOMAIN} doesn't point here yet. Setting up self-signed cert for IP...")
        base_url = f"https://{HOST}"
        setup_self_signed(ssh, HOST)

    # 5. Update .env on VPS with correct URLs
    print(f"\n[5/5] Updating .env on VPS...")
    run(ssh, f"sed -i 's|WEBHOOK_URL=.*|WEBHOOK_URL={base_url}/webhook|' {REMOTE}/.env")
    run(ssh, f"sed -i 's|WEBAPP_URL=.*|WEBAPP_URL={base_url}|' {REMOTE}/.env")

    # Verify
    code, env_out, _ = run(ssh, f"grep -E 'WEBHOOK_URL|WEBAPP_URL' {REMOTE}/.env")
    print(f"   .env URLs updated:\n{env_out}")

    # Restart bot to pick up new env
    run(ssh, f"cd {REMOTE} && docker compose restart bot")
    print("   Bot restarted with new URLs")
    time.sleep(8)

    # Final status
    print("\n=== FINAL STATUS ===")
    run(ssh, f"cd {REMOTE} && docker compose ps")
    run(ssh, "systemctl status nginx --no-pager -l | head -10")
    run(ssh, f"cd {REMOTE} && docker compose logs bot --tail=10")

    print(f"\n✅ Done! API available at: {base_url}")
    print(f"   Map: {base_url}/map")
    print(f"   Webhook: {base_url}/webhook")

    ssh.close()


def setup_self_signed(ssh, ip):
    """Generate self-signed SSL cert and add HTTPS nginx block."""
    run(ssh, "mkdir -p /etc/nginx/ssl")
    run(ssh,
        f'openssl req -x509 -nodes -days 365 -newkey rsa:2048 '
        f'-keyout /etc/nginx/ssl/selfsigned.key '
        f'-out /etc/nginx/ssl/selfsigned.crt '
        f'-subj "/C=RU/ST=Moscow/L=Moscow/O=SkyRent/CN={ip}"',
        timeout=30
    )

    ssl_block = f"""
server {{
    listen 443 ssl;
    server_name {ip};

    ssl_certificate /etc/nginx/ssl/selfsigned.crt;
    ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_read_timeout 300;
    }}

    location /webhook {{
        proxy_pass http://127.0.0.1:8000/webhook;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 60;
    }}
}}"""

    run(ssh, f"cat >> /etc/nginx/sites-available/rentbot <<'SSLEOF'\n{ssl_block}\nSSLEOF")
    run(ssh, "nginx -t")
    run(ssh, "systemctl reload nginx")
    print(f"   ✅ Self-signed SSL configured for https://{ip}")


if __name__ == "__main__":
    main()
