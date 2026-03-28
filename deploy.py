import os
import subprocess
import time

HOST = "45.12.5.177"
USER = "root"
PASSWORD = "w3X97idI9uAx"
TARGET_DIR = "/root/rentbot"

def run_local(cmd):
    print(f"Running locally: {cmd}")
    os.system(cmd)

# Because we are on Windows and sshpass might not be available, we'll just print manual instructions
# since the user already confirmed they can paste the password.
print("Paramiko authentication failed, likely due to server-side dropping of connection algorithms.")
print("We will use native scp and ssh commands. Please paste the password when prompted:")
print(f"PASSWORD: {PASSWORD}\n")

print("1. Packing project using Python shutil...")
import shutil

# Remove old archive if it exists
if os.path.exists("deploy.zip"):
    os.remove("deploy.zip")

import zipfile
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        # Exclusions
        if '.git' in root or 'venv' in root or '.venv' in root or '__pycache__' in root or '.gemini' in root or 'deploy' in root:
            continue
        for file in files:
            if file in ['deploy.py', 'deploy.zip', 'rentbot.db', 'rentbot.db-journal']:
                continue
            filepath = os.path.join(root, file)
            arcname = os.path.relpath(filepath, path)
            ziph.write(filepath, arcname)

with zipfile.ZipFile('deploy.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipdir('.', zipf)

print("Project packed into deploy.zip")

from fabric import Connection

print(f"\n2. Connecting to {HOST}...")
try:
    c = Connection(host=HOST, user=USER, connect_kwargs={"password": PASSWORD, "look_for_keys": False, "allow_agent": False})
    
    print("\n3. Creating directory on remote")
    c.run(f"mkdir -p {TARGET_DIR}")

    print("\n4. Uploading archive")
    c.put("deploy.zip", remote=f"{TARGET_DIR}/deploy.zip")

    print("\n5. Extracting and starting docker-compose")
    remote_command = f"cd {TARGET_DIR} && apt-get update && apt-get install -y unzip docker.io docker-compose && unzip -o deploy.zip && rm deploy.zip && docker-compose down && docker-compose up -d --build"
    c.run(remote_command)

    if os.path.exists("deploy.zip"):
        os.remove("deploy.zip")

    print("\n🎉 Done! If all steps completed, your bot is running.")
except Exception as e:
    print(f"Deployment failed: {e}")
