import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('45.12.5.177', username='root', password='Makson30_', timeout=15)

cmd = "curl -s -X POST https://api.telegram.org/bot8670983320:AAHqvLcDqR_10vh_HywE0I_5S6mPkMJ4wYc/sendMessage -d chat_id=7108317408 -d text='TEST_MESSAGE_FROM_SERVER'"
stdin, stdout, stderr = ssh.exec_command(cmd)
print("Response:", stdout.read().decode('utf-8'))
ssh.close()
