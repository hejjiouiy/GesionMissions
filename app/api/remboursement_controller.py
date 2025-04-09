from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import remboursement_repo
from app.schemas.remboursement_schema import RemboursementCreate, RemboursementOut
from dependencies import get_db

router = APIRouter(prefix="/remboursement", tags=["Remboursements"])

@router.get("/")
async def get_remboursements( db: AsyncSession = Depends(get_db)):
    return await remboursement_repo.get_remboursements(db)

@router.post("/add", response_model=RemboursementOut)
async def create_remboursement(remboursement : RemboursementCreate, db: AsyncSession = Depends(get_db)):
    return await remboursement_repo.create_remboursement(db, remboursement)

@router.put("/update-{remboursement_id}", response_model=RemboursementOut)
async def update_remboursement(
    remboursement_id: UUID,
    remboursement_update: RemboursementCreate,
    db: AsyncSession = Depends(get_db)
):
    db_remboursement = await remboursement_repo.update_remboursement(db, remboursement_id, remboursement_update)
    if db_remboursement is None:
        raise HTTPException(status_code=404, detail="demande de Remboursement non trouvé")
    return db_remboursement

@router.delete("/delete/{remboursement_id}", response_model=RemboursementOut)
async def delete_remboursement(
        remboursement_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    db_remboursement = await remboursement_repo.delete_remboursement(db, remboursement_id)
    if db_remboursement is None:
        raise HTTPException(status_code=404, detail="demande de Remboursement non trouvé")

    return db_remboursement