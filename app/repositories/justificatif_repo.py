from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.justificatif import Justificatif
from app.schemas.justificatif_schema import JustificatifCreate

async def create_justificatif(db: AsyncSession, justificatif: JustificatifCreate):
    db_justificatif = Justificatif(**justificatif.dict())
    db.add(db_justificatif)
    await db.commit()
    await db.refresh(db_justificatif)
    return db_justificatif

async def get_justificatif_by_id(db: AsyncSession, justificatif_id: UUID):
    result = await db.execute(select(Justificatif).where(Justificatif.id == justificatif_id))
    return result.scalar_one_or_none()

async def get_justificatifs(db: AsyncSession, skip: int = 0, limit: int =100):
    result = await db.execute(select(Justificatif).options(selectinload(Justificatif.financement)).offset(skip).limit(limit))
    return result.scalars().all()

async def delete_justificatif(db: AsyncSession, justificatif_id: UUID):
    result = await db.execute(select(Justificatif)
                              .where(Justificatif.id == justificatif_id)
                              .options(selectinload(Justificatif.financement))
                              )
    justificatif = result.scalar_one_or_none()
    if justificatif:
        await db.delete(justificatif)
        await db.commit()
    return justificatif

async def update_justificatif(db: AsyncSession, justificatif_id: UUID, justificatif: JustificatifCreate):
    result = await db.execute(select(Justificatif).where(Justificatif.id == justificatif_id))
    db_justificatif = result.scalar_one_or_none()
    if db_justificatif is None:
        return None;

    for key, value in justificatif.dict(exclude_unset=True).items():
        setattr(db_justificatif, key, value)

    await db.commit()
    await db.refresh(db_justificatif)
    return db_justificatif