from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.HistoriqueValidation import HistoriqueValidation
from app.schemas.historique_validation_schema import HistoriqueValidationCreate

async def create_historiqueValidation(db: AsyncSession, historiqueValidation: HistoriqueValidationCreate):
    db_historiqueValidation = HistoriqueValidation(**historiqueValidation.dict())
    db.add(db_historiqueValidation)
    await db.commit()
    await db.refresh(db_historiqueValidation)
    return db_historiqueValidation

async def get_historiqueValidation_by_id(db: AsyncSession, historiqueValidation_id: UUID):
    result = await db.execute(select(HistoriqueValidation).where(HistoriqueValidation.id == historiqueValidation_id))
    return result.scalar_one_or_none()

async def get_historiqueValidations(db: AsyncSession, skip: int = 0, limit: int =100):
    result = await db.execute(select(HistoriqueValidation).offset(skip).limit(limit))
    return result.scalars().all()

async def delete_historiqueValidation(db: AsyncSession, historiqueValidation_id: UUID):
    result = await db.execute(select(HistoriqueValidation)
                              .where(HistoriqueValidation.id == historiqueValidation_id)
                              .options(selectinload(HistoriqueValidation.ordre_mission))
                              )
    historiqueValidation = result.scalar_one_or_none()
    if historiqueValidation:
        await db.delete(historiqueValidation)
        await db.commit()
    return historiqueValidation

async def update_historiqueValidation(db: AsyncSession, historiqueValidation_id: UUID, historiqueValidation: HistoriqueValidationCreate):
    result = await db.execute(select(HistoriqueValidation).where(HistoriqueValidation.id == historiqueValidation_id))
    db_historiqueValidation = result.scalar_one_or_none()
    if db_historiqueValidation is None:
        return None

    for key, value in historiqueValidation.dict(exclude_unset=True).items():
        setattr(db_historiqueValidation, key, value)

    await db.commit()
    await db.refresh(db_historiqueValidation)
    return db_historiqueValidation