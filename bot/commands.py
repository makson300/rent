from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота / Регистрация"),
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="search", description="Поиск оборудования"),
        BotCommand(command="profile", description="Мой профиль"),
        BotCommand(command="admin", description="Панель администратора (только для админов)")
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
