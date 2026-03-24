# Telegram Бот - Маркетплейс аренды оборудования

Проект для аренды и сдачи съемочного, спортивного и туристического оборудования (P2P).

## Стек технологий
- Python 3.10+
- aiogram 3.x (Фреймворк для Telegram API)
- SQLAlchemy + PostgreSQL / asyncpg (Работа с БД)

## Локальный запуск

1. **Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   ```

2. **Активируйте окружение:**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте переменные окружения:**
   Скопируйте `\.env.example` в `\.env` и укажите ваш `BOT_TOKEN` и настройки БД.
   ```bash
   copy .env.example .env
   ```

5. **Запустите бота:**
   ```bash
   python main.py
   ```
