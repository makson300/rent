from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="menu", description="📱 Главное меню"),
        BotCommand(command="search", description="🔍 Поиск техники"),
        BotCommand(command="profile", description="👤 Личный кабинет"),
        BotCommand(command="admin", description="🛠 Админка"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
