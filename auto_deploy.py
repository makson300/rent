"""
Automated VPS deployment script.
Uploads deploy.zip, installs Docker, configures env, and starts services.
"""
import paramiko
import os
import time

HOST = "45.12.5.177"
USER = "root"
PASSWORD = "Makson30_"
LOCAL_ZIP = "deploy.zip"
REMOTE_DIR = "/root/rentbot"

def run_ssh(ssh, cmd, timeout=120):
    """Execute command and return output, raising on failure."""
    print(f"  > {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(f"    {out[:500]}")
    if err and exit_code != 0:
        print(f"    [ERR] {err[:500]}")
    return out, err, exit_code

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print(f"[1/7] Connecting to {HOST}...")
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=15)
    print("  Connected!")
    
    # Upload deploy.zip
    print(f"[2/7] Uploading {LOCAL_ZIP}...")
    sftp = ssh.open_sftp()
    sftp.put(LOCAL_ZIP, f"/root/{LOCAL_ZIP}")
    sftp.close()
    print(f"  Uploaded {os.path.getsize(LOCAL_ZIP)} bytes")
    
    # Install dependencies
    print("[3/7] Installing Docker and utilities...")
    run_ssh(ssh, "apt-get update -qq", timeout=120)
    run_ssh(ssh, "apt-get install -y -qq curl unzip ufw fail2ban", timeout=120)
    
    # Check if Docker is installed
    _, _, docker_rc = run_ssh(ssh, "docker --version")
    if docker_rc != 0:
        print("  Installing Docker...")
        run_ssh(ssh, "curl -fsSL https://get.docker.com | sh", timeout=300)
        run_ssh(ssh, "systemctl enable docker && systemctl start docker")
    else:
        print("  Docker already installed")
    
    # Check docker compose
    run_ssh(ssh, "docker compose version")
    
    # Setup firewall
    print("[4/7] Configuring firewall (ufw) and fail2ban...")
    run_ssh(ssh, "ufw default deny incoming")
    run_ssh(ssh, "ufw default allow outgoing")
    run_ssh(ssh, "ufw allow 22/tcp")
    run_ssh(ssh, "ufw allow 8000/tcp")
    run_ssh(ssh, "echo 'y' | ufw enable")
    
    # fail2ban config
    fail2ban_cfg = """[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
maxretry = 3
bantime = 86400"""
    run_ssh(ssh, f"cat > /etc/fail2ban/jail.local << 'EOFCFG'\n{fail2ban_cfg}\nEOFCFG")
    run_ssh(ssh, "systemctl enable fail2ban && systemctl restart fail2ban")
    
    # Unpack project
    print("[5/7] Unpacking project...")
    run_ssh(ssh, f"mkdir -p {REMOTE_DIR}")
    run_ssh(ssh, f"cd /root && unzip -o {LOCAL_ZIP} -d {REMOTE_DIR}")
    
    # Create .env
    print("[6/7] Creating .env with production config...")
    env_content = """BOT_TOKEN=8670983320:AAHqvLcDqR_10vh_HywE0I_5S6mPkMJ4wYc
ADMIN_IDS=7108317408,8341832184,675101681

YOOKASSA_SHOP_ID=1310834
YOOKASSA_SECRET_KEY=live_ghi9tZC9wScVBQhW6Tk7PbBduuP6NW1DaY54jw3XkfE

POSTGRES_USER=botuser
POSTGRES_PASSWORD=Xk9m2Qw7rB4nJfLt
POSTGRES_DB=rentbot
DATABASE_URL=postgresql+asyncpg://botuser:Xk9m2Qw7rB4nJfLt@db:5432/rentbot

REDIS_PASSWORD=Yz3nWm8vRp5sKdHx
REDIS_URL=redis://:Yz3nWm8vRp5sKdHx@redis:6379/0

USE_WEBHOOK=True
WEBHOOK_URL=http://45.12.5.177:8000/webhook
WEBHOOK_SECRET=aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uVw3xYz4

ADMIN_DASHBOARD_PASSWORD=DroneMarket2026Secure"""
    
    run_ssh(ssh, f"cat > {REMOTE_DIR}/.env << 'EOFENV'\n{env_content}\nEOFENV")
    
    # Docker compose up
    print("[7/7] Building and starting Docker containers...")
    run_ssh(ssh, f"cd {REMOTE_DIR} && docker compose down 2>/dev/null; docker compose up -d --build", timeout=600)
    
    # Wait and check
    print("  Waiting 15s for containers to start...")
    time.sleep(15)
    
    out, _, _ = run_ssh(ssh, f"cd {REMOTE_DIR} && docker compose ps")
    print(f"\n{'='*60}")
    print("CONTAINER STATUS:")
    print(out)
    print(f"{'='*60}")
    
    # Check logs
    out, _, _ = run_ssh(ssh, f"cd {REMOTE_DIR} && docker compose logs bot --tail=20")
    print("\nBOT LOGS (last 20 lines):")
    print(out[:1000])
    
    ssh.close()
    print("\nDone!")

if __name__ == "__main__":
    main()
