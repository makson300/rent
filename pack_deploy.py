import zipfile
import os

EXCLUDE_DIRS = {'.git', 'venv', '.venv', '__pycache__', '.gemini', '.next', 'node_modules', 'tmp'}
EXCLUDE_FILES = {
    'deploy.py', 'deploy.zip', 'deploy.tar.gz', 'test_ssh.py',
    'rentbot.db', 'rentbot.db-journal', 'db.sqlite3',
    'paramiko.log', 'web_log.txt'
}

z = zipfile.ZipFile('deploy.zip', 'w', zipfile.ZIP_DEFLATED)
for root, dirs, files in os.walk('.'):
    # Skip excluded directories
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for f in files:
        if f in EXCLUDE_FILES or f.startswith('tmp_'):
            continue
        filepath = os.path.join(root, f)
        arcname = os.path.relpath(filepath, '.')
        z.write(filepath, arcname)
z.close()
print(f"deploy.zip created: {os.path.getsize('deploy.zip')} bytes")
