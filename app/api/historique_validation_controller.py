from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import historique_validation_repo
from app.schemas.historique_validation_schema import HistoriqueValidationCreate, HistoriqueValidationOut
from dependencies import get_db

router = APIRouter(prefix="/validation", tags=["Validations"])

@router.get("/home")
async def get_historiqueValidation(request:Request, db: AsyncSession = Depends(get_db)):
    user_id = request.headers.get("x-user-id")
    user_email = request.headers.get("x-user-email")
    user_roles = request.headers.get("x-user-roles")
    user_fullName = request.headers.get("x-user-name")
    print("User ID:", user_id)
    print("User Email:", user_email)
    print("User Roles:", user_roles)

    res = await historique_validation_repo.get_historiqueValidations(db)
    return {
        "user": {
            "id": user_id,
            "email": user_email,
            "roles": user_roles
        },
        "historiqueValidations": res
    }

@router.post("/createHistoriqueValidation", response_model=HistoriqueValidationOut)
async def create_historiqueValidation(historiqueValidation : HistoriqueValidationCreate, db: AsyncSession = Depends(get_db)):
    return await historique_validation_repo.create_historiqueValidation(db, historiqueValidation)


@router.put("/update-{historiqueValidation_id}", response_model=HistoriqueValidationOut)
async def update_historiqueValidation(
    historiqueValidation_id: UUID,
    historiqueValidation_update: HistoriqueValidationCreate,
    db: AsyncSession = Depends(get_db)
):
    db_historiqueValidation = await historique_validation_repo.update_historiqueValidation(db, historiqueValidation_id, historiqueValidation_update)
    if db_historiqueValidation is None:
        raise HTTPException(status_code=404, detail="HistoriqueValidation non trouvé")
    return db_historiqueValidation

@router.delete("/delete/{historiqueValidation_id}", response_model=HistoriqueValidationOut)
async def delete_historiqueValidation(
        historiqueValidation_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    db_historiqueValidation = await historique_validation_repo.delete_historiqueValidation(db, historiqueValidation_id)
    if db_historiqueValidation is None:
        raise HTTPException(status_code=404, detail="HistoriqueValidation non trouvé")

    return db_historiqueValidation