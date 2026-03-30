import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("45.12.5.177", username="root", password="Makson30_", timeout=15)

# Put script
sftp = ssh.open_sftp()
sftp.put("test_endpoints_vps.py", "/root/test_endpoints_vps.py")
sftp.close()

# Run script
print("Running tests on VPS network...")
_, out, err = ssh.exec_command("python3 /root/test_endpoints_vps.py")
print(out.read().decode())
print(err.read().decode())

# Check firewall rules
_, out, err = ssh.exec_command("ufw status")
print("\n--- UFW Status ---")
print(out.read().decode())

ssh.close()
