import paramiko

HOST = "45.12.5.177"
USER = "root"
PASSWORD = "Makson30_"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=15)

_, out, err = ssh.exec_command("docker logs --tail 200 rentbot-bot-1")
logs = out.read().decode("utf-8", errors="replace")
err_logs = err.read().decode("utf-8", errors="replace")

with open("bot_crash.log", "w", encoding="utf-8") as f:
    f.write(logs)
    f.write("\n\n--- STDERR ---\n\n")
    f.write(err_logs)

ssh.close()
print("Saved to bot_crash.log")
