import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("45.12.5.177", username="root", password="Makson30_", timeout=15)

stdin, stdout, stderr = ssh.exec_command("docker ps")
print(stdout.read().decode())
err = stderr.read().decode()
if err: print("ERR:", err)
ssh.close()