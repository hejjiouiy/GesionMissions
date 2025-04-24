from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import rapport_mission_repo
from app.schemas.rapport_schema import RapportCreate, RapportOut
from dependencies import get_db

router = APIRouter(prefix="/rapport", tags=["Rapport"])

@router.get("/")
async def get_rapports( db: AsyncSession = Depends(get_db)):
    rapports = await rapport_mission_repo.get_rapports(db)
    return [
        {
            "id": rapport.id,
            "titre": rapport.contenu,
            "ordre_mission": {
                "id": rapport.ordre_mission.id,
                "debut" : rapport.ordre_mission.dateDebut,
                "fin": rapport.ordre_mission.dateFin,
                "user": rapport.ordre_mission.user_id,
                "mission":rapport.ordre_mission.mission_id,
                "accord resposnable": f"order/file/{rapport.ordre_mission.id}/download",
                "createdAt": rapport.ordre_mission.createdAt,
                "updatedAt": rapport.ordre_mission.updatedAt,
            } if rapport.ordre_mission else None,
            "rapport": f"/rapport/{rapport.id}/download"

        } for rapport in rapports
    ]

@router.post("/add", response_model=RapportOut)
async def create_rapport(
        file: UploadFile = File(...),
        ordre_mission_id: UUID = Form(...),
        content: str = Form(...),
        db: AsyncSession = Depends(get_db)
):
    rapport = RapportCreate(contenu=content,ordre_mission_id=ordre_mission_id)
    file_data = await file.read() if file else None
    return await rapport_mission_repo.create_rapport(db, rapport, file_data)


@router.put("/update-{rapport_id}", response_model=RapportOut)
async def update_rapport(
    rapport_id: UUID,
    rapport_update: RapportCreate,
    db: AsyncSession = Depends(get_db)
):
    db_rapport = await rapport_mission_repo.update_rapport_mission(db, rapport_id, rapport_update)
    if db_rapport is None:
        raise HTTPException(status_code=404, detail="Rapport de mission non trouvé")
    return db_rapport

@router.delete("/delete/{rapport_mission_id}", response_model=RapportOut)
async def delete_rapport(
        rapport_mission_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    db_rapport_mission = await rapport_mission_repo.delete_rapport(db, rapport_mission_id)
    if db_rapport_mission is None:
        raise HTTPException(status_code=404, detail="Rapport de mission non trouvé")

    return db_rapport_mission