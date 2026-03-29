import paramiko
import os

key_path = os.path.expanduser('~/.ssh/id_rsa')
key = paramiko.RSAKey.from_private_key_file(key_path)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print('Connecting to 45.12.5.177...')
ssh.connect('45.12.5.177', username='root', pkey=key)

sftp = ssh.open_sftp()
project_dir = '/opt/rentbot'

files_to_upload = [
    ('bot/handlers/catalog.py', 'bot/handlers/catalog.py'),
    ('web/dashboard.py', 'web/dashboard.py'),
    ('web/templates/jobs_admin.html', 'web/templates/jobs_admin.html'),
    ('web/templates/base.html', 'web/templates/base.html'),
    ('web/templates/webapp_catalog.html', 'web/templates/webapp_catalog.html')
]

for local_file, remote_file in files_to_upload:
    remote_path = project_dir + '/' + remote_file
    local_path = os.path.join(os.getcwd(), os.path.normpath(local_file))
    print('Uploading ' + local_path + ' to ' + remote_path + '...')
    sftp.put(local_path, remote_path)

sftp.close()

print('Restarting services...')
stdin, stdout, stderr = ssh.exec_command('systemctl restart rentbot && systemctl restart rentbot-dashboard')
print(stdout.read().decode())
if stderr.read():
    print('ERROR:', stderr.read().decode())

ssh.close()
print('Done!')