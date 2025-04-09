from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import financement_repo
from app.schemas.financement_schema import FinancementCreate, FinancementOut
from dependencies import get_db

router = APIRouter(prefix="/financement", tags=["Financements"])

@router.get("/")
async def get_financements( db: AsyncSession = Depends(get_db)):
    return await financement_repo.get_financements(db)

@router.post("/add", response_model=FinancementOut)
async def create_financement(financement : FinancementCreate, db: AsyncSession = Depends(get_db)):
    return await financement_repo.create_financement(db, financement)

@router.put("/update-{financement_id}", response_model=FinancementOut)
async def update_financement(
    financement_id: UUID,
    financement_update: FinancementCreate,
    db: AsyncSession = Depends(get_db)
):
    db_financement = await financement_repo.update_financement(db, financement_id, financement_update)
    if db_financement is None:
        raise HTTPException(status_code=404, detail="Financement non trouvé")
    return db_financement

@router.delete("/delete/{financement_id}", response_model=FinancementOut)
async def delete_financement(
        financement_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    db_financement = await financement_repo.delete_financement(db, financement_id)
    if db_financement is None:
        raise HTTPException(status_code=404, detail="demande de Financement non trouvé")

    return db_financement