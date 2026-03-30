import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("45.12.5.177", username="root", password="Makson30_", timeout=15)

commands = [
    'cd /root/rentbot && docker compose up -d bot'
]

for cmd in commands:
    print(f"Running: {cmd}")
    _, out, err = ssh.exec_command(cmd)
    o = out.read().decode("utf-8", errors="replace")
    e = err.read().decode("utf-8", errors="replace")
    if o: print("OUT:", o.strip())
    if e: print("ERR:", e.strip())

ssh.close()
