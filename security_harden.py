import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("45.12.5.177", username="root", password="Makson30_", timeout=15)

commands = [
    # 1. Close port 8000 from public access (Nginx should handle all public traffic)
    "ufw deny 8000/tcp",
    "ufw reload",
    
    # 2. Install and enable Fail2Ban for SSH protection
    "apt-get update -y && apt-get install -y fail2ban",
    "systemctl enable fail2ban",
    "systemctl start fail2ban",
    
    # 3. View the docker-compose to verify DB ports
    "cat /root/rentbot/docker-compose.yml"
]

for cmd in commands:
    print(f"\n--- Running: {cmd} ---")
    _, out, err = ssh.exec_command(cmd)
    
    # Read output
    o = out.read().decode("utf-8", errors="replace").strip()
    e = err.read().decode("utf-8", errors="replace").strip()
    
    if o: print("OUT:\n", o)
    if e: print("ERR:\n", e)

ssh.close()
