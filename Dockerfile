# Используем официальный образ Python 3.12 (облегченная версия)
FROM python:3.12-slim

# Настройка переменных окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Рабочая директория
WORKDIR /app

# Устанавливаем системные зависимости (например, для компиляции некоторых Python пакетов и работы с БД)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt /app/

# Устанавливаем Python зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем исходный код проекта
COPY . /app/

# Открываем порт для FastAPI дашборда
EXPOSE 8000

# Создаем скрипт запуска
RUN echo '#!/bin/bash\n\
echo "Применение миграций Alembic..."\n\
python -m alembic upgrade head\n\
echo "Запуск бота и дашборда..."\n\
python main.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Запускаем приложение
CMD ["/app/start.sh"]
