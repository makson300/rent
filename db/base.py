from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from bot.config import DATABASE_URL


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Создаёт все таблицы и начальные данные при первом запуске"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Сидинг начальных данных
    from db.models.category import Category
    from db.models.user import User
    from db.models.review import Review
    from sqlalchemy import select
    
    async with async_session() as session:
        # Проверяем наличие категорий
        result = await session.execute(select(Category).limit(1))
        if not result.scalar():
            categories = [
                Category(id=1, name="Аренда", type="rent"),
                Category(id=2, name="Продажа", type="sale"),
                Category(id=3, name="Обучение", type="course")
            ]
            session.add_all(categories)
            
        # Проверяем наличие системного пользователя
        result = await session.execute(select(User).where(User.id == 1))
        if not result.scalar():
            system_user = User(
                id=1,
                telegram_id=0,
                first_name="System",
                username="system_bot"
            )
            session.add(system_user)
            
        await session.commit()


async def get_session() -> AsyncSession:
    """Получить сессию БД"""
    async with async_session() as session:
        return session
