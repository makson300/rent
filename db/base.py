from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from bot.config import DATABASE_URL


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


engine_kwargs = {"echo": False}
if "sqlite" not in DATABASE_URL:
    engine_kwargs.update({
        "pool_size": 5,        # base number of persistent connections
        "max_overflow": 10,    # extra connections allowed during spikes
        "pool_recycle": 3600,  # recycle stale connections every hour
        "pool_pre_ping": True, # verify connection is alive before using it
    })

engine = create_async_engine(DATABASE_URL, **engine_kwargs)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Создаёт все таблицы и начальные данные при первом запуске"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Сидинг начальных данных
    from db.models.category import Category
    from db.models.user import User
    from db.models.review import Review
    from db.models.log import ModerationLog
    from db.models.job import Job
    from db.models.job_response import JobResponse
    from sqlalchemy import select
    
    async with async_session() as session:
        # Проверяем наличие категорий
        result = await session.execute(select(Category).limit(1))
        if not result.scalar():
            categories = [
                Category(id=1, name="Дроны", type="rent"),
                Category(id=2, name="Продажа", type="sale"),
                Category(id=3, name="Обучение", type="course"),
                Category(id=4, name="Техника для съемки", type="rent"),
                Category(id=5, name="Другое", type="rent"),
                Category(id=6, name="Операторы", type="operator"),
                Category(id=7, name="ЧП / Гуманитарная миссия", type="emergency"),
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
