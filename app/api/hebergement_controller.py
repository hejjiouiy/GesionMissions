from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import hebergement_repo
from app.schemas.hebergement_schema import HebergementCreate, HeberegementOut
from dependencies import get_db

router = APIRouter(prefix="/hebergement", tags=["Hebergements"])

@router.get("/")
async def get_hebergements( db: AsyncSession = Depends(get_db)):
    return await hebergement_repo.get_hebergements(db)

@router.post("/add", response_model=HeberegementOut)
async def create_hebergement(hebergement : HebergementCreate, db: AsyncSession = Depends(get_db)):
    return await hebergement_repo.create_hebergement(db, hebergement)

@router.put("/update-{hebergement_id}", response_model=HeberegementOut)
async def update_hebergement(
    hebergement_id: UUID,
    hebergement_update: HebergementCreate,
    db: AsyncSession = Depends(get_db)
):
    db_hebergement = await hebergement_repo.update_hebergement(db, hebergement_id, hebergement_update)
    if db_hebergement is None:
        raise HTTPException(status_code=404, detail="Hebergement non trouvé")
    return db_hebergement

@router.delete("/delete/{hebergement_id}", response_model=HeberegementOut)
async def delete_hebergement(
        hebergement_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    db_hebergement = await hebergement_repo.delete_hebergement(db, hebergement_id)
    if db_hebergement is None:
        raise HTTPException(status_code=404, detail="Heberegement non trouvé")

    return db_hebergement