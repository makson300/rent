from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from db.models.listing import Listing, ListingPhoto

async def create_listing(
    session: AsyncSession,
    user_id: int,
    category_id: int,
    city: str,
    title: str,
    description: str,
    deposit_terms: str,
    delivery_terms: str,
    price_list: str,
    contacts: str,
    photo_ids: list[str]
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
        status="moderation"
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


async def delete_listing(session: AsyncSession, listing_id: int):
    """Удалить объявление"""
    from sqlalchemy import delete
    await session.execute(delete(ListingPhoto).where(ListingPhoto.listing_id == listing_id))
    await session.execute(delete(Listing).where(Listing.id == listing_id))
    await session.commit()
