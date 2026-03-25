import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./rentbot.db")

# Telegram ID администраторов (через запятую в .env)
_admin_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: list[int] = [int(x.strip()) for x in _admin_ids_raw.split(",") if x.strip()]

PROXY_URL = os.getenv("PROXY_URL")  # e.g., socks5://user:pass@127.0.0.1:1080 or http://127.0.0.1:8080

# Yookassa Payment settings
YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в .env")
