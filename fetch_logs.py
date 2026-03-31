import paramiko

HOST = "45.12.5.177"
USER = "root"
PASSWORD = "Makson30_"

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD)
    
    print("Fetching last 100 lines of bot logs...")
    _, out, err = ssh.exec_command("docker logs --tail 200 rentbot-bot-1")
    o = out.read().decode(errors="replace")
    print(o)
    ssh.close()

if __name__ == "__main__":
    main()
