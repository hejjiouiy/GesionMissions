from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.remboursement import Remboursement
from app.schemas.remboursement_schema import RemboursementCreate

async def create_remboursement(db: AsyncSession, remboursement: RemboursementCreate):
    db_remboursement = Remboursement(**remboursement.dict())
    db.add(db_remboursement)
    await db.commit()
    await db.refresh(db_remboursement)
    return db_remboursement

async def get_remboursement_by_id(db: AsyncSession, remboursement_id: UUID):
    result = await db.execute(select(Remboursement).where(Remboursement.id == remboursement_id))
    return result.scalar_one_or_none()

async def get_remboursements(db: AsyncSession, skip: int = 0, limit: int =100):
    result = await db.execute(select(Remboursement).offset(skip).limit(limit))
    return result.scalars().all()

async def delete_remboursement(db: AsyncSession, remboursement_id: UUID):
    result = await db.execute(select(Remboursement).where(Remboursement.id == remboursement_id))
    remboursement = result.scalar_one_or_none()
    if remboursement:
        await db.delete(remboursement)
        await db.commit()
    return remboursement

async def update_remboursement(db: AsyncSession, remboursement_id: UUID, remboursement: RemboursementCreate):
    result = await db.execute(select(Remboursement).where(Remboursement.id == remboursement_id))
    db_remboursement = result.scalar_one_or_none()
    if db_remboursement is None:
        return None;

    for key, value in remboursement.dict(exclude_unset=True).items():
        setattr(db_remboursement, key, value)

    await db.commit()
    await db.refresh(db_remboursement)
    return db_remboursement
