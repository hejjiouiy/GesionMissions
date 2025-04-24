from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import justificatif_repo
from app.schemas.justificatif_schema import JustificatifCreate, JustificatifOut
from app.models.justificatif import Justificatif
from dependencies import get_db
import magic
from io import BytesIO
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/justificatif", tags=["Justificatifs"])


@router.get("/")
async def get_justificatifs_metadata(db: AsyncSession = Depends(get_db)):
    justificatifs = await justificatif_repo.get_justificatifs(db)
    return [
        {
            "id": j.id,
            "financement" : j.financement,
            "createdAt": j.createdAt,
            "modifiedAt": j.modifiedAt,
            "downloadUrl": f"/justificatif/{j.id}/download"
        } for j in justificatifs
    ]

@router.get("/{justificatif_id}/download")
async def download_justificatif(justificatif_id: UUID, db: AsyncSession = Depends(get_db)):
    # 1. Fetch the record first (async DB logic)
    justificatif = await justificatif_repo.get_justificatif_by_id(db, justificatif_id)
    if not justificatif:
        raise HTTPException(status_code=404, detail="Justificatif not found")

    # 2. Now do MIME detection (synchronously, outside DB session)
    mime = magic.Magic(mime=True)
    file_mime_type = mime.from_buffer(bytes(justificatif.data))  # Ensure it's bytes, not memoryview

    # 3. Create response
    extension = file_mime_type.split('/')[-1]
    return StreamingResponse(BytesIO(justificatif.data),
                             media_type=file_mime_type,
                             headers={
                                 "Content-Disposition": f"attachment; filename=justificatif_{justificatif_id}.{extension}"
                             })


@router.post("/add", response_model=JustificatifOut)
async def create_justificatif(
        file: UploadFile = File(...),
        financement_id: UUID = Form(...),
        db: AsyncSession = Depends(get_db)
                              ):
    content = await file.read()

    new_justificatif = Justificatif(
        data=content,
        financement_id=financement_id
    )
    db.add(new_justificatif)
    await db.commit()
    await db.refresh(new_justificatif)
    return new_justificatif

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