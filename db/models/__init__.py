# Экспорт всех моделей для удобного импорта и создания таблиц
from db.models.user import User
from db.models.category import Category
from db.models.tariff import Tariff
from db.models.listing import Listing, ListingPhoto
from db.models.feedback import Feedback

__all__ = ["User", "Category", "Tariff", "Listing", "ListingPhoto", "Feedback"]

