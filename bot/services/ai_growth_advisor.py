import asyncio
from sqlalchemy import select, func
from db.base import async_session
from db.models.user import User
from db.models.listing import Listing
from db.models.feedback import Feedback

async def get_growth_insights():
    """Анализирует метрики и генерирует рекомендации по росту и монетизации"""
    async with async_session() as session:
        users_count = await session.scalar(select(func.count()).select_from(User))
        listings_count = await session.scalar(
            select(func.count()).select_from(Listing).where(Listing.status == "active")
        )
        feedback_count = await session.scalar(select(func.count()).select_from(Feedback))

    # Мок-логика ИИ-советника
    recommendations = []

    if users_count < 100:
        recommendations.append({
            "title": "Привлечение первых пользователей",
            "content": "Запустите реферальную программу: давайте 1 бесплатное размещение за 3 приглашенных друзей."
        })

    if listings_count < 10:
        recommendations.append({
            "title": "Наполнение каталога",
            "content": "Сделайте временную акцию: бесплатное размещение для первых 50 объявлений в категории 'Дроны'."
        })

    recommendations.append({
        "title": "Идея монетизации: Срочная продажа",
        "content": "Добавьте услугу 'Поднять в топ' за 199 руб. Это выделит объявление цветом в поиске."
    })

    recommendations.append({
        "title": "Улучшение UX",
        "content": "Пользователи часто пишут в поддержку про залог. Добавьте калькулятор рекомендуемого залога на этапе создания объявления."
    })

    return recommendations
