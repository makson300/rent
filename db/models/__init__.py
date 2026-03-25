# Экспорт всех моделей для удобного импорта и создания таблиц
from db.models.user import User
from db.models.category import Category
from db.models.tariff import Tariff
from db.models.listing import Listing, ListingPhoto

__all__ = ["User", "Category", "Tariff", "Listing", "ListingPhoto"]
