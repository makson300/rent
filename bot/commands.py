from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, MenuButtonWebApp, WebAppInfo
from bot.config import WEBAPP_URL

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="menu", description="📱 Главное меню"),
        BotCommand(command="search", description="🔍 Поиск техники"),
        BotCommand(command="profile", description="👤 Личный кабинет"),
        BotCommand(command="admin", description="🛠 Админка"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
    
    # Установка глобальной кнопки меню (Слева от поля ввода)
    try:
        if WEBAPP_URL:
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(
                    type="web_app", 
                    text="SkyRent", 
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Could not set web_app menu button: {e}")
