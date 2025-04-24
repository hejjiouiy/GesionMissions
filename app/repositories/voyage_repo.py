from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.voyage import Voyage
from app.schemas.voyage_schema import VoyageCreate

async def create_voyage(db: AsyncSession, voyage: VoyageCreate):
    db_voyage = Voyage(**voyage.dict())
    db.add(db_voyage)
    await db.commit()
    await db.refresh(db_voyage)
    return db_voyage

async def get_voyage_by_id(db: AsyncSession, voyage_id: UUID):
    result = await db.execute(select(Voyage).where(Voyage.id == voyage_id).options(selectinload(Voyage.ordre_mission)))
    return result.scalar_one_or_none()

async def get_voyages(db: AsyncSession, skip: int = 0, limit: int =100):
    result = await db.execute(select(Voyage).options(selectinload(Voyage.ordre_mission)).offset(skip).limit(limit))
    return result.scalars().all()

async def delete_voyage(db: AsyncSession, voyage_id: UUID):
    result = await db.execute(select(Voyage).where(Voyage.id == voyage_id))
    voyage = result.scalar_one_or_none()
    if voyage:
        await db.delete(voyage)
        await db.commit()
    return voyage

async def update_voyage(db: AsyncSession, voyage_id: UUID, voyage: VoyageCreate):
    result = await db.execute(select(Voyage).where(Voyage.id == voyage_id))
    db_voyage = result.scalar_one_or_none()
    if db_voyage is None:
        return None;

    for key, value in voyage.dict(exclude_unset=True).items():
        setattr(db_voyage, key, value)

    await db.commit()
    await db.refresh(db_voyage)
    return db_voyage
