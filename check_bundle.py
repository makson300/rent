"""Check if env var was baked into bundle, then force clean rebuild if not."""
import paramiko
import os
import time
import sys

HOST = "45.12.5.177"
USER = "root"
PASSWORD = "Makson30_"
REMOTE = "/root/rentbot"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def r(ssh, cmd, timeout=600):
    print(f"  > {cmd[:90]}")
    _, o, e = ssh.exec_command(cmd, timeout=timeout)
    code = o.channel.recv_exit_status()
    out = o.read().decode("utf-8", errors="replace").strip()
    err = e.read().decode("utf-8", errors="replace").strip()
    if out:
        print("   " + out[:600])
    return code, out


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=15)
print(f"Connected to {HOST}")

# Check if 45.12.5.177 is baked into the bundle
print("\n[1/3] Checking if env var was baked into JS bundle...")
_, baked = r(ssh,
    "docker exec rentbot-frontend-1 grep -rl '45.12.5.177' /app/.next/static/ 2>/dev/null | head -3"
)
if "45.12.5.177" in baked or baked.strip():
    print("   Found 45.12.5.177 in bundle - env var IS baked in!")
else:
    print("   NOT found - doing clean rebuild with --no-cache...")

    # Force clean rebuild
    r(ssh, f"cd {REMOTE} && docker compose stop frontend && docker compose rm -f frontend")
    r(ssh, f"cd {REMOTE} && docker compose build --no-cache frontend", timeout=600)
    r(ssh, f"cd {REMOTE} && docker compose up -d frontend")
    print("   Waiting 40s...")
    time.sleep(40)

    # Verify again
    _, baked2 = r(ssh,
        "docker exec rentbot-frontend-1 grep -rl '45.12.5.177' /app/.next/static/ 2>/dev/null | head -3"
    )
    print(f"   After rebuild, found in bundle: {'YES' if baked2 else 'NO - check Dockerfile'}")

# Also check what URL is in the actual bundle JS
print("\n[2/3] Checking actual URLs in JS chunks...")
_, url_check = r(ssh,
    "docker exec rentbot-frontend-1 grep -r 'localhost:8000\\|45.12.5.177' "
    "/app/.next/static/chunks/ 2>/dev/null | head -3 | cut -c1-150"
)
print(f"   Bundle contains: {url_check or 'nothing found'}")

# Final status
print("\n[3/3] Container status:")
r(ssh, f"cd {REMOTE} && docker compose ps")

ssh.close()
