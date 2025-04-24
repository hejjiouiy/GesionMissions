from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.financement import Financement
from app.schemas.financement_schema import FinancementCreate

async def create_financement(db: AsyncSession, financement: FinancementCreate):
    db_financement = Financement(**financement.dict())
    db.add(db_financement)
    await db.commit()
    await db.refresh(db_financement)
    return db_financement

async def get_financement_by_id(db: AsyncSession, financement_id: UUID):
    result = await db.execute(select(Financement).
                              where(Financement.id == financement_id).
                              options(selectinload(Financement.ordre_mission)))
    return result.scalar_one_or_none()

async def get_financements(db: AsyncSession, skip: int = 0, limit: int =100):
    result = await db.execute(select(Financement).offset(skip).limit(limit))
    return result.scalars().all()

async def delete_financement(db: AsyncSession, financement_id: UUID):
    result = await db.execute(select(Financement).where(Financement.id == financement_id))
    financement = result.scalar_one_or_none()
    if financement:
        await db.delete(financement)
        await db.commit()
    return financement

async def update_financement(db: AsyncSession, financement_id: UUID, financement: FinancementCreate):
    result = await db.execute(select(Financement).where(Financement.id == financement_id))
    db_financement = result.scalar_one_or_none()
    if db_financement is None:
        return None;

    for key, value in financement.dict(exclude_unset=True).items():
        setattr(db_financement, key, value)

    await db.commit()
    await db.refresh(db_financement)
    return db_financement
