"""Check DNS for skyrent.pro from the VPS, then run certbot if it points to us."""
import paramiko
import sys
import time

HOST = "45.12.5.177"
USER = "root"
PASSWORD = "Makson30_"
REMOTE = "/root/rentbot"
DOMAIN = "skyrent.pro"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def r(ssh, cmd, timeout=120):
    print(f"  > {cmd[:90]}")
    _, o, e = ssh.exec_command(cmd, timeout=timeout)
    code = o.channel.recv_exit_status()
    out = o.read().decode("utf-8", errors="replace").strip()
    err = e.read().decode("utf-8", errors="replace").strip()
    if out:
        print("   " + out[:400])
    return code, out


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=15)
print(f"Connected to {HOST}")

# Check DNS
print(f"\n[1/3] Checking DNS for {DOMAIN}...")
_, dns_a = r(ssh, f"dig +short {DOMAIN} A 2>/dev/null || nslookup {DOMAIN} 2>/dev/null | grep 'Address:' | tail -1")
_, dns_www = r(ssh, f"dig +short www.{DOMAIN} A 2>/dev/null")

print(f"\n   {DOMAIN}     -> '{dns_a}'")
print(f"   www.{DOMAIN} -> '{dns_www}'")

points_here = HOST in dns_a
print(f"\n   Points to this server ({HOST}): {points_here}")

if points_here:
    print(f"\n[2/3] DNS OK! Running certbot for {DOMAIN}...")
    code, out = r(ssh,
        f"certbot --nginx -d {DOMAIN} -d www.{DOMAIN} "
        f"--non-interactive --agree-tos --email admin@{DOMAIN} --redirect 2>&1",
        timeout=120
    )
    if code == 0:
        print(f"\n   SSL cert obtained!")
        # Update .env on VPS
        print("\n[3/3] Updating .env URLs...")
        r(ssh, f"sed -i 's|WEBHOOK_URL=.*|WEBHOOK_URL=https://{DOMAIN}/webhook|' {REMOTE}/.env")
        r(ssh, f"grep -q 'WEBHOOK_URL' {REMOTE}/.env || echo 'WEBHOOK_URL=https://{DOMAIN}/webhook' >> {REMOTE}/.env")
        r(ssh, f"grep -E 'WEBHOOK|WEBAPP' {REMOTE}/.env")
        r(ssh, f"cd {REMOTE} && docker compose restart bot")
        print(f"\n   Done! Site: https://{DOMAIN}")
    else:
        print(f"   Certbot failed. Check output above.")
else:
    print(f"\n[!] {DOMAIN} does not point to {HOST} yet.")
    print(f"    Current value: '{dns_a or 'NOT FOUND'}'")
    print(f"    Need to add A-record: {DOMAIN} -> {HOST}")
    print(f"\n[2/3] Searching for registrar info in project files...")

    # Check if WHOIS gives any info
    r(ssh, f"whois {DOMAIN} 2>/dev/null | grep -iE 'registrar|name server|nserver' | head -10")

ssh.close()
print("\nDone.")
