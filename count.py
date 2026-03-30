import os

total = 0
for root, dirs, files in os.walk('.'):
    if 'venv' in root or 'node_modules' in root or '.next' in root or '.git' in root or 'alembic' in root:
        continue
    for f in files:
        if f.endswith(('.py', '.tsx', '.ts', '.css', '.html', '.sh')):
            try:
                with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                    lines = [l for l in file.readlines() if l.strip()]
                    total += len(lines)
            except:
                pass
print(f"Total LOC: {total}")
