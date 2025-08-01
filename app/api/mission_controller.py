from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import mission_repo
from app.schemas.mission_schema import MissionCreate, MissionOut
from dependencies import get_db

router = APIRouter(prefix="/mission", tags=["Missions"])

@router.get("/home")
async def get_mission(request:Request, db: AsyncSession = Depends(get_db)):
    user_id = request.headers.get("x-user-id")
    user_email = request.headers.get("x-user-email")
    user_roles = request.headers.get("x-user-roles")
    user_fullName = request.headers.get("x-user-name")
    print("User ID:", user_id)
    print("User Email:", user_email)
    print("User Roles:", user_roles)

    res = await mission_repo.get_missions(db)
    return {
        "user": {
            "id": user_id,
            "email": user_email,
            "roles": user_roles
        },
        "missions": res
    }

@router.post("/createMission", response_model=MissionOut)
async def create_mission(mission : MissionCreate, db: AsyncSession = Depends(get_db)):
    return await mission_repo.create_mission(db, mission)

@router.put("/update-{mission_id}", response_model=MissionOut)
async def update_mission(
    mission_id: UUID,
    mission_update: MissionCreate,
    db: AsyncSession = Depends(get_db)
):
    db_mission = await mission_repo.update_mission(db, mission_id, mission_update)
    if db_mission is None:
        raise HTTPException(status_code=404, detail="Mission non trouvé")
    return db_mission

@router.delete("/delete/{mission_id}", response_model=MissionOut)
async def delete_mission(
        mission_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    db_mission = await mission_repo.delete_mission(db, mission_id)
    if db_mission is None:
        raise HTTPException(status_code=404, detail="Mission non trouvé")

    return db_mission

@router.get("/")
async def get_missions(db: AsyncSession = Depends(get_db)):
    return await mission_repo.get_missions(db)