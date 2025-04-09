from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.hebergement import Hebergement
from app.schemas.hebergement_schema import HebergementCreate

async def create_hebergement(db: AsyncSession, hebergement: HebergementCreate):
    db_hebergement = Hebergement(**hebergement.dict())
    db.add(db_hebergement)
    await db.commit()
    await db.refresh(db_hebergement)
    return db_hebergement

async def get_hebergement_by_id(db: AsyncSession, hebergement_id: UUID):
    result = await db.execute(select(Hebergement).where(Hebergement.id == hebergement_id))
    return result.scalar_one_or_none()

async def get_hebergements(db: AsyncSession, skip: int = 0, limit: int =100):
    result = await db.execute(select(Hebergement).offset(skip).limit(limit))
    return result.scalars().all()

async def delete_hebergement(db: AsyncSession, hebergement_id: UUID):
    result = await db.execute(select(Hebergement).where(Hebergement.id == hebergement_id))
    hebergement = result.scalar_one_or_none()
    if hebergement:
        await db.delete(hebergement)
        await db.commit()
    return hebergement

async def update_hebergement(db: AsyncSession, hebergement_id: UUID, hebergement: HebergementCreate):
    result = await db.execute(select(Hebergement).where(Hebergement.id == hebergement_id))
    db_hebergement = result.scalar_one_or_none()
    if db_hebergement is None:
        return None;

    for key, value in hebergement.dict(exclude_unset=True).items():
        setattr(db_hebergement, key, value)

    await db.commit()
    await db.refresh(db_hebergement)
    return db_hebergement
