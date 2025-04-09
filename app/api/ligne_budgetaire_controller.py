from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import ligne_budgetaire_repo
from app.schemas.ligne_budgetaire_schema import LigneBudgetaireCreate, LigneBudgetaireOut
from dependencies import get_db

router = APIRouter(prefix="/ligne-budgetaire", tags=["Lignes_budgetaire"])

@router.get("/")
async def get_ligne_budgetaire( db: AsyncSession = Depends(get_db)):
    return await ligne_budgetaire_repo.get_lignes_budgetaire(db)

@router.post("/add", response_model=LigneBudgetaireOut)
async def create_ligne_budgetaire(ligne_budgetaire : LigneBudgetaireCreate, db: AsyncSession = Depends(get_db)):
    return await ligne_budgetaire_repo.create_ligne_budgetaire(db, ligne_budgetaire)

@router.put("/update-{ligne_budgetaire_id}", response_model=LigneBudgetaireOut)
async def update_ligne_budgetaire(
    ligne_budgetaire_id: UUID,
    ligne_budgetaire_update: LigneBudgetaireCreate,
    db: AsyncSession = Depends(get_db)
):
    db_ligne_budgetaire = await ligne_budgetaire_repo.update_ligne_budgetaire(db, ligne_budgetaire_id, ligne_budgetaire_update)
    if db_ligne_budgetaire is None:
        raise HTTPException(status_code=404, detail="LigneBudgetaire non trouvé")
    return db_ligne_budgetaire

@router.delete("/delete/{ligne_budgetaire_id}", response_model=LigneBudgetaireOut)
async def delete_ligne_budgetaire(
        ligne_budgetaire_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    db_ligne_budgetaire = await ligne_budgetaire_repo.delete_ligne_budgetaire(db, ligne_budgetaire_id)
    if db_ligne_budgetaire is None:
        raise HTTPException(status_code=404, detail="Ligne Budgetaire non trouvé")

    return db_ligne_budgetaire