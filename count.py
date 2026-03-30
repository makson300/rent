import os

root = '.'
exts = {}
ignore_dirs = {'.git', 'node_modules', '.next', 'venv', '__pycache__', 'tmp', 'tmp_momoa'}

for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
    for f in filenames:
        ext = os.path.splitext(f)[1]
        filepath = os.path.join(dirpath, f)
        if not ext or ext.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.webp', '.mp4', '.sqlite3', '.db', '.zip', '.gz', '.tar', '.log']:
            continue
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                count = sum(1 for line in file)
                exts[ext] = exts.get(ext, 0) + count
        except UnicodeDecodeError:
            pass
        except Exception as e:
            pass

sorted_exts = sorted(exts.items(), key=lambda item: item[1], reverse=True)
for ext, count in sorted_exts:
    print(f'{ext}: {count}')
print(f'Total: {sum(exts.values())}')
