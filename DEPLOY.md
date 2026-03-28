# 🚀 Инструкция по деплою на VPS

## Требования
- Ubuntu 22.04+ VPS с root-доступом
- Минимум 1 ГБ RAM, 10 ГБ диск
- Docker и Docker Compose установлены

---

## Шаг 1: Подготовка сервера (выполнить 1 раз)

Скопируйте и вставьте этот блок целиком в терминал VPS:

```bash
# Обновление системы и установка Docker
apt update && apt upgrade -y
apt install -y curl git ufw fail2ban unzip

# Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker

# Docker Compose (v2 — уже встроен в Docker)
docker compose version
```

---

## Шаг 2: Firewall (ufw)

```bash
# Разрешаем SSH и порт бота, закрываем всё остальное
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 8000/tcp  # Webhook (FastAPI)
ufw --force enable
ufw status
```

---

## Шаг 3: Fail2Ban (защита от брутфорса SSH)

```bash
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime  = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port    = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s
maxretry = 3
bantime = 86400
EOF

systemctl enable fail2ban
systemctl restart fail2ban
```

---

## Шаг 4: Загрузка проекта

**С вашего Windows-компьютера:**

```powershell
# Из папки проекта (бот аренда)
scp deploy.zip root@45.12.5.177:/root/
```

**На VPS:**

```bash
cd /root
unzip -o deploy.zip -d rentbot
cd rentbot
```

---

## Шаг 5: Настройка .env (ОБЯЗАТЕЛЬНО)

```bash
cat > .env << 'EOF'
BOT_TOKEN=8670983320:AAHqvLcDqR_10vh_HywE0I_5S6mPkMJ4wYc
ADMIN_IDS=7108317408,8341832184,675101681

# Yookassa
YOOKASSA_SHOP_ID=1310834
YOOKASSA_SECRET_KEY=live_ghi9tZC9wScVBQhW6Tk7PbBduuP6NW1DaY54jw3XkfE

# Database (должен совпадать с docker-compose)
POSTGRES_USER=botuser
POSTGRES_PASSWORD=Xk9m2Qw7rB4nJfLt
POSTGRES_DB=rentbot
DATABASE_URL=postgresql+asyncpg://botuser:Xk9m2Qw7rB4nJfLt@db:5432/rentbot

# Redis
REDIS_PASSWORD=Yz3nWm8vRp5sKdHx
REDIS_URL=redis://:Yz3nWm8vRp5sKdHx@redis:6379/0

# Webhook
USE_WEBHOOK=True
WEBHOOK_URL=http://45.12.5.177:8000/webhook
WEBHOOK_SECRET=aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2u

# Admin Dashboard
ADMIN_DASHBOARD_PASSWORD=MySecureDashboard2026
EOF
```

> ⚠️ **ВАЖНО:** Замените пароли на свои уникальные значения!

---

## Шаг 6: Запуск

```bash
cd /root/rentbot
docker compose up -d --build
```

Проверка:

```bash
# Все 3 контейнера должны быть Running
docker compose ps

# Логи бота
docker compose logs -f bot --tail=50
```

---

## Шаг 7: Проверка работы

```bash
# Проверить, что webhook отвечает
curl -s http://localhost:8000/webhook | head

# Проверить, что бот жив
docker compose logs bot | grep "Bot authorized"
```

---

## Полезные команды

```bash
# Перезапуск
docker compose restart bot

# Обновление кода (загрузите новый deploy.zip и)
docker compose down
unzip -o deploy.zip -d /root/rentbot
docker compose up -d --build

# Бэкап БД
docker compose exec db pg_dump -U botuser rentbot > backup_$(date +%Y%m%d).sql
```
