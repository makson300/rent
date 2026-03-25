from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from db.models.listing import Listing, ListingPhoto

async def create_listing(
    session: AsyncSession,
    user_id: int,  # This should be the internal DB ID
    category_id: int,
    city: str,
    title: str,
    description: str,
    deposit_terms: str,
    delivery_terms: str,
    price_list: str,
    contacts: str,
    photo_ids: list[str],
    listing_type: str = "rental",
    partner_id: str | None = None,
    status: str = "moderation"
) -> Listing:
    """Создать новое объявление с фото"""
    listing = Listing(
        user_id=user_id,
        category_id=category_id,
        city=city,
        title=title,
        description=description,
        deposit_terms=deposit_terms,
        delivery_terms=delivery_terms,
        price_list=price_list,
        contacts=contacts,
        listing_type=listing_type,
        partner_id=partner_id,
        status=status
    )
    session.add(listing)
    await session.flush()  # получаем id объявления

    for index, p_id in enumerate(photo_ids):
        photo = ListingPhoto(listing_id=listing.id, photo_id=p_id, order=index)
        session.add(photo)

    await session.commit()
    await session.refresh(listing)
    return listing


async def get_active_listings_by_city(session: AsyncSession, city: str):
    """Поиск активных объявлений по городу"""
    result = await session.execute(
        select(Listing)
        .options(selectinload(Listing.photos))
        .where(Listing.status == "active", Listing.city == city)
    )
    return result.scalars().all()


async def get_user_listings(session: AsyncSession, user_id: int):
    """Получить все объявления конкретного пользователя (включая модерацию)"""
    # Note: user_id provided here is the internal DB ID. 
    # For now, since user_id=1 is used as stub during creation, we use it here.
    # In real logic we would map message.from_user.id to DB id.
    result = await session.execute(
        select(Listing)
        .options(selectinload(Listing.photos))
        .where(Listing.user_id == user_id)
        .order_by(Listing.created_at.desc())
    )
    return result.scalars().all()


async def get_listings_by_filter(
    session: AsyncSession, 
    city: str | None = None, 
    category: str | None = None, 
    status: str = "active"
):
    """Поиск объявлений по фильтрам"""
    query = select(Listing).options(selectinload(Listing.photos)).where(Listing.status == status)
    
    if city:
        query = query.where(Listing.city == city)
    if category:
        # Assuming we search by category name or we need to join with Category model
        # For simplicity now, let's assume category is a string name or we join
        from db.models.category import Category
        query = query.join(Category).where(Category.name == category)
        
    result = await session.execute(query.order_by(Listing.created_at.desc()))
    return result.scalars().all()


async def get_listing_by_id(session: AsyncSession, listing_id: int):
    """Получить объявление по ID"""
    result = await session.execute(
        select(Listing).options(selectinload(Listing.photos)).where(Listing.id == listing_id)
    )
    return result.scalar_one_or_none()


async def update_listing_status(session: AsyncSession, listing_id: int, status: str):
    """Обновить статус объявления (moderation -> active/rejected)"""
    listing = await get_listing_by_id(session, listing_id)
    if listing:
        listing.status = status
        await session.commit()
        await session.refresh(listing)
    return listing


async def delete_listing(session: AsyncSession, listing_id: int):
    """Удалить объявление"""
    from sqlalchemy import delete
    await session.execute(delete(ListingPhoto).where(ListingPhoto.listing_id == listing_id))
    await session.execute(delete(Listing).where(Listing.id == listing_id))
    await session.commit()
