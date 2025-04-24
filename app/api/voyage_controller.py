from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import voyage_repo
from app.schemas.voyage_schema import VoyageCreate, VoyageOut
from dependencies import get_db

router = APIRouter(prefix="/voyage", tags=["Voyages"])

@router.get("/")
async def get_voyages( db: AsyncSession = Depends(get_db)):
    voyages = await voyage_repo.get_voyages(db)
    return [
        {
            'id' : voyage.id,
            'destination' : voyage.destination,
            'moyen' : voyage.moyen,
            'date de depart' : voyage.dateVoyage,
            'ordre de mission' : voyage.ordre_mission.id,
            'creer le' : voyage.createdAt,
        } for voyage in voyages
    ]

@router.post("/add", response_model=VoyageOut)
async def create_voyage(voyage : VoyageCreate, db: AsyncSession = Depends(get_db)):
    return await voyage_repo.create_voyage(db, voyage)

@router.put("/update-{voyage_id}", response_model=VoyageOut)
async def update_voyage(
    voyage_id: UUID,
    voyage_update: VoyageCreate,
    db: AsyncSession = Depends(get_db)
):
    db_voyage = await voyage_repo.update_voyage(db, voyage_id, voyage_update)
    if db_voyage is None:
        raise HTTPException(status_code=404, detail="demande de Voyage non trouvé")
    return db_voyage

@router.delete("/delete/{voyage_id}", response_model=VoyageOut)
async def delete_voyage(
        voyage_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    db_voyage = await voyage_repo.delete_voyage(db, voyage_id)
    if db_voyage is None:
        raise HTTPException(status_code=404, detail="demande de Voyage non trouvé")

    return db_voyage