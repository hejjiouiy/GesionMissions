from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import justificatif_repo
from app.schemas.justificatif_schema import JustificatifCreate, JustificatifOut
from dependencies import get_db

router = APIRouter(prefix="/justificatif", tags=["Justificatifs"])

@router.get("/")
async def get_justificatifs( db: AsyncSession = Depends(get_db)):
    return await justificatif_repo.get_justificatifs(db)

@router.post("/add", response_model=JustificatifOut)
async def create_justificatif(justificatif : JustificatifCreate, db: AsyncSession = Depends(get_db)):
    return await justificatif_repo.create_justificatif(db, justificatif)

@router.put("/update-{justificatif_id}", response_model=JustificatifOut)
async def update_justificatif(
    justificatif_id: UUID,
    justificatif_update: JustificatifCreate,
    db: AsyncSession = Depends(get_db)
):
    db_justificatif = await justificatif_repo.update_justificatif(db, justificatif_id, justificatif_update)
    if db_justificatif is None:
        raise HTTPException(status_code=404, detail="Justificatif non trouvé")
    return db_justificatif

@router.delete("/delete/{justificatif_id}", response_model=JustificatifOut)
async def delete_justificatif(
        justificatif_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    db_justificatif = await justificatif_repo.delete_justificatif(db, justificatif_id)
    if db_justificatif is None:
        raise HTTPException(status_code=404, detail="Justificatif non trouvé")

    return db_justificatif