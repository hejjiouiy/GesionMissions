from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ordre_mission import OrdreMission
from app.repositories import ordre_mission_repo
from app.schemas.ordre_mission_schema import OrdreMissionCreate, OrderMissionOut
from dependencies import get_db

router = APIRouter(prefix="/order", tags=["Orders"])

@router.get("/")
async def get_ordres( db: AsyncSession = Depends(get_db)):
    return await ordre_mission_repo.get_ordres(db)

@router.post("/add", response_model=OrderMissionOut)
async def create_ordre(
    dateDebut: date = Form(...),
    dateFin: date = Form(...),
    mission_id: UUID = Form(...),
    user_id: UUID = Form(...),
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
):
    ordre = OrdreMissionCreate(
        dateDebut=dateDebut,
        dateFin=dateFin,
        mission_id=mission_id,
        user_id=user_id,
    )
    file_data = await file.read() if file else None
    return await ordre_mission_repo.create_ordre(db, ordre, file_data)

@router.get("/file/{ordre_id}")
async def download_file(ordre_id: UUID, db: AsyncSession = Depends(get_db)):
    ordre = await db.get(OrdreMission, ordre_id)
    if ordre is None or ordre.accord_respo is None:
        raise HTTPException(status_code=404, detail="File not found")

    return Response(
        content=ordre.accord_respo,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=mission_{ordre_id}.pdf"}
    )



@router.put("/update-{ordre_id}", response_model=OrderMissionOut)
async def update_ordre(
    ordre_id: UUID,
    ordre_update: OrdreMissionCreate,
    db: AsyncSession = Depends(get_db)
):
    db_ordre = await ordre_mission_repo.update_ordre_mission(db, ordre_id, ordre_update)
    if db_ordre is None:
        raise HTTPException(status_code=404, detail="Ordre de mission non trouvé")
    return db_ordre

@router.delete("/delete/{ordre_mission_id}", response_model=OrderMissionOut)
async def delete_ordre_mission(
        ordre_mission_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    db_ordre_mission = await ordre_mission_repo.delete_ordre(db, ordre_mission_id)
    if db_ordre_mission is None:
        raise HTTPException(status_code=404, detail="Ordre de mission non trouvé")

    return db_ordre_mission