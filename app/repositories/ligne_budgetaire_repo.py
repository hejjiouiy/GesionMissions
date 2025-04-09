from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.ligne_budgetaire import LigneBudgetaire
from app.schemas.ligne_budgetaire_schema import LigneBudgetaireCreate

async def create_ligne_budgetaire(db: AsyncSession, ligne_budgetaire: LigneBudgetaireCreate):
    db_ligne_budgetaire = LigneBudgetaire(**ligne_budgetaire.dict())
    db.add(db_ligne_budgetaire)
    await db.commit()
    await db.refresh(db_ligne_budgetaire)
    return db_ligne_budgetaire

async def get_ligne_budgetaire_by_id(db: AsyncSession, ligne_budgetaire_id: UUID):
    result = await db.execute(select(LigneBudgetaire).where(LigneBudgetaire.id == ligne_budgetaire_id))
    return result.scalar_one_or_none()

async def get_lignes_budgetaire(db: AsyncSession, skip: int = 0, limit: int =100):
    result = await db.execute(select(LigneBudgetaire).offset(skip).limit(limit))
    return result.scalars().all()

async def delete_ligne_budgetaire(db: AsyncSession, ligne_budgetaire_id: UUID):
    result = await db.execute(select(LigneBudgetaire).where(LigneBudgetaire.id == ligne_budgetaire_id))
    ligne_budgetaire = result.scalar_one_or_none()
    if ligne_budgetaire:
        await db.delete(ligne_budgetaire)
        await db.commit()
    return ligne_budgetaire

async def update_ligne_budgetaire(db: AsyncSession, ligne_budgetaire_id: UUID, ligne_budgetaire: LigneBudgetaireCreate):
    result = await db.execute(select(LigneBudgetaire).where(LigneBudgetaire.id == ligne_budgetaire_id))
    db_ligne_budgetaire = result.scalar_one_or_none()
    if db_ligne_budgetaire is None:
        return None;

    for key, value in ligne_budgetaire.dict(exclude_unset=True).items():
        setattr(db_ligne_budgetaire, key, value)

    await db.commit()
    await db.refresh(db_ligne_budgetaire)
    return db_ligne_budgetaire
