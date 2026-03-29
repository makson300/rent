scp deploy.zip root@45.12.5.177:/root/rentbot/
ssh root@45.12.5.177 "cd /root/rentbot ; unzip -o deploy.zip ; docker compose build bot frontend ; docker compose up -d bot frontend"
