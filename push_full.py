import paramiko
import os
import zipfile
import time

HOST = "45.12.5.177"
USER = "root"
PASSWORD = "Makson30_"
REMOTE = "/root/rentbot"

print("1. Zipping source code...")
if os.path.exists("deploy.zip"): os.remove("deploy.zip")

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        if any(x in root for x in ['.git', 'node_modules', '.next', 'venv', '__pycache__', '.gemini']):
            continue
        for file in files:
            if file.endswith('.zip') or file in ['rentbot.db', 'rentbot.db-journal']:
                continue
            filepath = os.path.join(root, file)
            ziph.write(filepath, os.path.relpath(filepath, path))

with zipfile.ZipFile('deploy.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipdir('.', zipf)

print(f"Zip created: {os.path.getsize('deploy.zip')} bytes")

def run(ssh, cmd):
    print(f"  > {cmd}")
    _, out, err = ssh.exec_command(cmd)
    code = out.channel.recv_exit_status()
    print("   " + out.read().decode("utf-8", errors="replace").strip()[:300])
    if code != 0: print("   ERR: " + err.read().decode("utf-8", errors="replace").strip()[:300])
    return code

print("2. Connecting to VPS...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=15)

print("3. Uploading via SFTP...")
sftp = ssh.open_sftp()
sftp.put("deploy.zip", "/root/deploy.zip")
sftp.close()

print("4. Unpacking and deploying...")
run(ssh, f"cd /root && unzip -o deploy.zip -d {REMOTE} && rm deploy.zip")
# Build both frontend and bot
run(ssh, f"cd {REMOTE} && docker compose build bot frontend")
run(ssh, f"cd {REMOTE} && docker compose up -d bot frontend")
print("5. Reloading nginx...")
run(ssh, "systemctl reload nginx")

print("Validating bot container:")
time.sleep(5)
run(ssh, f"docker logs --tail 20 rentbot-bot-1")

ssh.close()
print("Deployed Successfully!")
