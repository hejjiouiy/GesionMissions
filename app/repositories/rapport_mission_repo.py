from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.enums.Enums import EtatMission
from app.models.ordre_mission import OrdreMission

from app.models.rapport_mission import RapportMission
from app.repositories import ordre_mission_repo
from app.schemas.rapport_schema import RapportCreate

async def create_rapport(db: AsyncSession, rapport_mission: RapportCreate , file_data : bytes = None):
    db_rapport_mission = RapportMission(**rapport_mission.dict())
    db.add(db_rapport_mission)
    await db.commit()
    await db.refresh(db_rapport_mission)
    return db_rapport_mission

async def get_rapport_by_id(db: AsyncSession, rapport_mission_id: UUID):
    result = await db.execute(select(RapportMission)
                              .where(RapportMission.id == rapport_mission_id)
                              .options(selectinload(RapportMission.ordre_mission))
                              )
    return result.scalar_one_or_none()

async def get_rapports(db: AsyncSession, skip: int = 0, limit: int =100):
    result = await db.execute(select(RapportMission)
                              .options(
        selectinload(RapportMission.ordre_mission)
        ).offset(skip).limit(limit))
    return result.scalars().all()

async def delete_rapport(db: AsyncSession, rapport_mission_id: UUID):
    result = await db.execute(select(RapportMission).where(RapportMission.id == rapport_mission_id))
    rapport_mission = result.scalar_one_or_none()
    if rapport_mission:
        await db.delete(rapport_mission)
        await db.commit()
    return rapport_mission

async def update_rapport_mission(db: AsyncSession, rapport_mission_id: UUID, rapport_mission: RapportCreate):
    result = await db.execute(select(RapportMission).where(RapportMission.id == rapport_mission_id))
    db_rapport_mission = result.scalar_one_or_none()
    if db_rapport_mission is None:
        return None

    for key, value in rapport_mission.dict(exclude_unset=True).items():
        setattr(db_rapport_mission, key, value)

    await db.commit()
    await db.refresh(db_rapport_mission)
    return db_rapport_mission


async def validate_rapport_mission(db: AsyncSession, rapport_mission_id: UUID):
    result = await get_rapport_by_id(db, rapport_mission_id)
    if result is None:
        return None
    ordre_mission = await db.execute(
        select(OrdreMission).where(OrdreMission.id == result.ordre_mission_id)
    )
    ordre_mission = ordre_mission.scalar_one_or_none()
    if ordre_mission is None:
        return None
    ordre_mission.etat = EtatMission.CLOTUREE
    result.isValid = True
    await db.commit()
    await db.refresh(result)
    await db.refresh(ordre_mission)

    # Convert to dict while still in async context
    return {
        "id": result.id,
        "objective": result.objective,
        "proceedings": result.proceedings,
        "resultAchieved": result.resultAchieved,
        "nextStep": result.nextStep,
        "keyContact": result.keyContact,
        "interlocutors": result.interlocutors,
        "difficulties": result.difficulties,
        "recommendations": result.recommendations,
        "ordre_mission_id": result.ordre_mission_id,
        "isValid": result.isValid,
        "createdAt": result.createdAt,
        "updatedAt": result.updatedAt,
    }