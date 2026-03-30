import paramiko

def run_audit():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('45.12.5.177', username='root', password='Makson30_')
    
    print("=== BOT LOGS ===")
    _, out, _ = ssh.exec_command('cd /root/rentbot && docker compose logs bot --tail=50')
    print(out.read().decode("utf-8", "replace"))
    
    print("\n=== FRONTEND LOGS ===")
    _, out, _ = ssh.exec_command('cd /root/rentbot && docker compose logs frontend --tail=30')
    print(out.read().decode("utf-8", "replace"))
    
    print("\n=== DB ERRORS ===")
    _, out, _ = ssh.exec_command('cd /root/rentbot && docker compose logs db | grep -i "error\\|warning" | tail -n 20')
    print(out.read().decode("utf-8", "replace"))

run_audit()
