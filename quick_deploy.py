"""Quick redeploy: upload zip, unpack, rebuild bot container, restart."""
import paramiko
import os
import time

HOST = "45.12.5.177"
USER = "root"
PASSWORD = "Makson30_"
REMOTE = "/root/rentbot"

def run(ssh, cmd, timeout=300):
    print(f"  > {cmd[:80]}")
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    code = out.channel.recv_exit_status()
    o = out.read().decode().strip()
    e = err.read().decode().strip()
    if o:
        print(o[:600])
    if e and code != 0:
        print("[ERR]", e[:300])
    return code

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=15)
print("Connected to VPS")

# Upload
sftp = ssh.open_sftp()
sftp.put("deploy.zip", "/root/deploy.zip")
sftp.close()
print(f"Uploaded deploy.zip ({os.path.getsize('deploy.zip')} bytes)")

# Unpack
run(ssh, f"cd /root && unzip -o deploy.zip -d {REMOTE}")

# Rebuild bot only (db/redis already running)
print("Rebuilding bot container...")
run(ssh, f"cd {REMOTE} && docker compose build bot", timeout=300)
run(ssh, f"cd {REMOTE} && docker compose up -d bot")

print("Waiting 12s for startup...")
time.sleep(12)

# Check
run(ssh, f"cd {REMOTE} && docker compose ps")
run(ssh, f"cd {REMOTE} && docker compose logs bot --tail=20")

ssh.close()
print("Done!")
