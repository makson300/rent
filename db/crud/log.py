from sqlalchemy.ext.asyncio import AsyncSession
from db.models.log import ModerationLog

async def create_moderation_log(
    session: AsyncSession,
    admin_id: int | None,
    action_type: str,
    entity_type: str,
    entity_id: int,
    details: str | None = None
) -> ModerationLog:
    log_entry = ModerationLog(
        admin_id=admin_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )
    session.add(log_entry)
    await session.commit()
    await session.refresh(log_entry)
    return log_entry
