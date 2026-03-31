import paramiko
import time

HOST = "45.12.5.177"
USER = "root"
PASSWORD = "Makson30_"
DOMAIN = "45.12.5.177.nip.io"
# Fallback domain if nip.io is rate-limited:
# DOMAIN = "45-12-5-177.nip.io"  # also works

def run(ssh, cmd, ok_nonzero=False):
    print(f"  > {cmd}")
    _, out, err = ssh.exec_command(cmd)
    o = out.read().decode().strip()
    e = err.read().decode().strip()
    if o: print("   [OUT]", o)
    if e: print("   [ERR]", e)
    return out.channel.recv_exit_status(), o, e

def main():
    global DOMAIN
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD)
    print(f"Connected to {HOST}")

    print("\n[1] Updating nginx config to use domain...")
    
    nginx_conf = f"""server {{
    listen 80;
    server_name {DOMAIN} {HOST};

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

    location /webhook {{
        proxy_pass http://127.0.0.1:8000/webhook;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 60;
    }}
}}"""
    
    # Overwrite config
    run(ssh, f"cat > /etc/nginx/sites-available/rentbot <<'NGINXEOF'\n{nginx_conf}\nNGINXEOF")
    run(ssh, "nginx -t")
    run(ssh, "systemctl reload nginx")

    print(f"\n[2] Running Certbot for {DOMAIN}...")
    code, o, e = run(ssh, f"certbot --nginx -d {DOMAIN} --non-interactive --agree-tos -m admin@{DOMAIN} --redirect")
    
    if code == 0:
        print(f"✅ Success! SSL active for {DOMAIN}")
    else:
        print("⚠️ SSL failed. Let's Encrypt limit? Trying sslip.io...")
        DOMAIN2 = "45.12.5.177.sslip.io"
        run(ssh, f"sed -i 's/{DOMAIN}/{DOMAIN2}/g' /etc/nginx/sites-available/rentbot")
        run(ssh, "systemctl reload nginx")
        code, o, e = run(ssh, f"certbot --nginx -d {DOMAIN2} --non-interactive --agree-tos -m admin@{DOMAIN2} --redirect")
        if code == 0:
            print(f"✅ Success! SSL active for {DOMAIN2}")
            DOMAIN = DOMAIN2
        else:
            print("❌ Both SSL attempts failed. Needs manual config or proxy_pass change.")
            ssh.close()
            return
            
    print("\n[3] Restarting Nginx...")
    run(ssh, "systemctl reload nginx")
    print(f"✅ API base is now: https://{DOMAIN}/api/v1")
    ssh.close()

if __name__ == "__main__":
    main()
