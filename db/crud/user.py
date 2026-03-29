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

async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    """Найти пользователя по username (без @)"""
    username = username.lstrip("@").lower()
    # ILIKE is not natively in sqlite, so we lower both sides for cross-db compat if we can, or just ilike for postgres
    from sqlalchemy import or_, func
    result = await session.execute(
        select(User).where(func.lower(User.username) == username)
    )
    return result.scalar_one_or_none()

async def set_user_role(session: AsyncSession, target_id: int | None, username: str | None, role: str, is_active: bool) -> tuple[bool, str]:
    """Установить роль (admin, moderator) по telegram_id или username"""
    user = None
    if target_id is not None:
        user = await get_user(session, target_id)
    elif username is not None:
        user = await get_user_by_username(session, username)
        
    if not user:
        return False, "Пользователь не найден в БД."
        
    if role == "admin":
        user.is_admin = is_active
    elif role == "moderator":
        user.is_moderator = is_active
        
    await session.commit()
    return True, f"Роль {role} {'выдана' if is_active else 'снята'} для пользователя {user.first_name}"
