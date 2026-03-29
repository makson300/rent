import paramiko
import time

HOST = "45.12.5.177"
USER = "root"
PASSWORD = "Makson30_"
DOMAIN = "45.12.5.177.nip.io"

def run_ssh(ssh, cmd):
    print(f"[RUN] {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(f"  [OUT] {out[:500]}")
    if err and exit_code != 0:
        print(f"  [ERR] {err[:500]}")
    return exit_code

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOST}...")
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=15)
    
    print("Installing Nginx, Certbot...")
    run_ssh(ssh, "apt-get update -y")
    run_ssh(ssh, "apt-get install -y nginx certbot python3-certbot-nginx")
    
    # Create Nginx config
    nginx_conf = f"""
server {{
    listen 80;
    server_name {DOMAIN};

    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
    print("Configuring Nginx...")
    run_ssh(ssh, f"cat > /etc/nginx/sites-available/{DOMAIN} << 'EOF'\n{nginx_conf}\nEOF")
    run_ssh(ssh, f"ln -sf /etc/nginx/sites-available/{DOMAIN} /etc/nginx/sites-enabled/")
    run_ssh(ssh, "rm -f /etc/nginx/sites-enabled/default")
    run_ssh(ssh, "systemctl restart nginx")
    
    print("Obtaining SSL wildcard/domain via Certbot...")
    # --non-interactive --agree-tos -m dummy@email.com
    run_ssh(ssh, f"certbot --nginx -d {DOMAIN} --non-interactive --agree-tos -m admin@rentbot.local --redirect")
    
    print("Restarting Nginx to apply certs...")
    run_ssh(ssh, "systemctl restart nginx")
    
    # Allow ports in UFW just in case 443 isn't allowed
    run_ssh(ssh, "ufw allow 'Nginx Full'")
    
    print("HTTPS setup complete!")
    ssh.close()

if __name__ == "__main__":
    main()
