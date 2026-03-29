# -*- coding: utf-8 -*-
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print("Connecting to 45.12.5.177...")
ssh.connect("45.12.5.177", username="root", password="Makson30_", timeout=15)

sftp = ssh.open_sftp()
project_dir = "/opt/rentbot"

files_to_upload = [
    ("bot/handlers/catalog.py", "bot/handlers/catalog.py"),
    ("web/dashboard.py", "web/dashboard.py"),
    ("web/templates/jobs_admin.html", "web/templates/jobs_admin.html"),
    ("web/templates/base.html", "web/templates/base.html"),
    ("web/templates/webapp_catalog.html", "web/templates/webapp_catalog.html")
]

for local_file, remote_file in files_to_upload:
    remote_path = f"{project_dir}/{remote_file}"
    # check if directory exists remote
    remote_dir = remote_path.rsplit('/', 1)[0]
    try:
        sftp.stat(remote_dir)
    except IOError:
        print(f"Directory {remote_dir} doesn't exist, creating...")
        ssh.exec_command(f"mkdir -p {remote_dir}")
        
    print(f"Uploading {local_file} to {remote_path}...")
    sftp.put(local_file, remote_path)

sftp.close()

print("Restarting services...")
stdin, stdout, stderr = ssh.exec_command("systemctl restart rentbot && systemctl restart rentbot-dashboard")
print("STDOUT:", stdout.read().decode())
err = stderr.read().decode()
if err:
    print("STDERR:", err)

ssh.close()
print("Done!")
