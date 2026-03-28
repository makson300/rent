from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.user import User


async def get_user(session: AsyncSession, telegram_id: int) -> User | None:
    """Найти пользователя по telegram_id"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    first_name: str,
    last_name: str | None = None,
    username: str | None = None,
    phone: str | None = None,
    user_type: str = "private",
    referrer_id: int | None = None,
) -> User:
    """Создать нового пользователя"""
    user = User(
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
        phone=phone,
        user_type=user_type,
        referrer_id=referrer_id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user_type(session: AsyncSession, telegram_id: int, user_type: str) -> User | None:
    """Обновить тип пользователя"""
    user = await get_user(session, telegram_id)
    if user:
        user.user_type = user_type
        await session.commit()
        await session.refresh(user)
    return user


async def update_user_phone(session: AsyncSession, telegram_id: int, phone: str) -> User | None:
    """Обновить телефон пользователя"""
    user = await get_user(session, telegram_id)
    if user:
        user.phone = phone
        await session.commit()
        await session.refresh(user)
    return user


async def get_user_by_db_id(session: AsyncSession, user_id: int) -> User | None:
    """Найти пользователя по id в БД"""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

async def get_all_users(session: AsyncSession):
    """Получить всех пользователей для рассылки"""
    result = await session.execute(select(User))
    return result.scalars().all()

async def set_user_ban_status(session: AsyncSession, telegram_id: int, is_banned: bool) -> bool:
    """Установить статус блокировки пользователя. Возвращает True если юзер найден."""
    user = await get_user(session, telegram_id)
    if user:
        user.is_banned = is_banned
        await session.commit()
        return True
    return False
