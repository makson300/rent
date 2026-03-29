import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('45.12.5.177', username='root', password='Makson30_', timeout=15)

stdin, stdout, stderr = ssh.exec_command('systemctl list-units --type=service | grep -iE "x-ui|marzban|v2ray|outline|3x-ui|shadowsocks|vpn|amz|openvpn"')
print("VPN Services:\n", stdout.read().decode('utf-8'))

ssh.close()
