# Экспорт всех моделей для удобного импорта и создания таблиц
from db.models.user import User
from db.models.category import Category
from db.models.tariff import Tariff

__all__ = ["User", "Category", "Tariff"]
