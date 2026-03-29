"""Deploy changes to both bot and frontend containers."""
import paramiko
import os
import time
import sys

HOST = "45.12.5.177"
USER = "root"
PASSWORD = "Makson30_"
REMOTE = "/root/rentbot"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def r(ssh, cmd, timeout=300):
    print(f"  > {cmd[:80]}")
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    code = out.channel.recv_exit_status()
    o = out.read().decode("utf-8", errors="replace").strip()
    e = err.read().decode("utf-8", errors="replace").strip()
    if o:
        print("   " + o[:400])
    if e and code != 0 and "warning" not in e.lower() and "deprecated" not in e.lower():
        print("   ERR:", e[:200])
    return code


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=15)
print(f"Connected to {HOST}")

print("\n[1/3] Uploading...")
sftp = ssh.open_sftp()
sftp.put("deploy.zip", "/root/deploy.zip")
sftp.close()
print(f"   {os.path.getsize('deploy.zip')} bytes uploaded")
r(ssh, f"cd /root && unzip -o deploy.zip -d {REMOTE}")

print("\n[2/3] Rebuilding bot and frontend...")
r(ssh, f"cd {REMOTE} && docker compose build bot frontend", timeout=600)
r(ssh, f"cd {REMOTE} && docker compose up -d bot frontend")
print("   Waiting 35s for services to start...")
time.sleep(35)

print("\n[3/3] Verification...")
r(ssh, f"cd {REMOTE} && docker compose ps")
_, result_code, _ = ssh.exec_command("curl -s http://127.0.0.1:8000/api/v1/radar/markers | head -c 100")
result_code.channel.recv_exit_status()
markers = result_code.read().decode("utf-8", errors="replace").strip()
print(f"   Radar markers API: {markers[:100] or 'empty/error'}")

ssh.close()
print(f"\nDone! Map updated. Verify at: http://{HOST}/map")
