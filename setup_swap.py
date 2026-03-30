import paramiko
import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("45.12.5.177", username="root", password="Makson30_", timeout=15)

commands = [
    # Check if swapfile exists
    "if [ ! -f /swapfile ]; then fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile && echo '/swapfile none swap sw 0 0' >> /etc/fstab; fi",
    
    # Configure swappiness (only use swap when RAM is really low to preserve SSD lifespan)
    "sysctl vm.swappiness=10",
    "if ! grep -q 'vm.swappiness=10' /etc/sysctl.conf; then echo 'vm.swappiness=10' >> /etc/sysctl.conf; fi",
    
    # Verify success
    "swapon --show",
    "free -m"
]

print("Applying Server Memory Hardening (Swap 2GB)...")
for cmd in commands:
    _, out, err = ssh.exec_command(cmd)
    o = out.read().decode('utf-8', 'ignore').strip()
    e = err.read().decode('utf-8', 'ignore').strip()
    if o: print(o)
    if e: print("ERR:", e)
    
ssh.close()
