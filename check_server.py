import paramiko
import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("45.12.5.177", username="root", password="Makson30_", timeout=15)

commands = [
    "echo \"=== CPU ===\"",
    "lscpu | grep -E 'Model name|Socket|Core|Thread|CPU MHz'",
    "echo \"=== RAM ===\"",
    "free -m",
    "echo \"=== DISK ===\"",
    "df -h /",
    "echo \"=== TOP PROCESSES ===\"",
    "top -b -n 1 | head -n 12",
    "echo \"=== DOCKER STATS ===\"",
    "docker stats --no-stream",
    "echo \"=== SWAP ===\"",
    "swapon --show"
]

for cmd in commands:
    _, out, err = ssh.exec_command(cmd)
    o = out.read().decode('utf-8', 'ignore')
    e = err.read().decode('utf-8', 'ignore')
    if o: print(o.strip())
    if e: print("ERR:", e.strip())
    
ssh.close()
