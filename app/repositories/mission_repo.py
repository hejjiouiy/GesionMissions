from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.Mission import Mission
from app.schemas.mission_schema import MissionCreate

async def create_mission(db: AsyncSession, mission: MissionCreate):
    db_mission = Mission(**mission.dict())
    db.add(db_mission)
    await db.commit()
    await db.refresh(db_mission)
    return db_mission

async def get_mission_by_id(db: AsyncSession, mission_id: UUID):
    result = await db.execute(select(Mission).where(Mission.id == mission_id))
    return result.scalar_one_or_none()

async def get_missions(db: AsyncSession, skip: int = 0, limit: int =100):
    result = await db.execute(select(Mission).offset(skip).limit(limit))
    return result.scalars().all()

# async def get_upcoming_missions(db: AsyncSession):
#     result = await db.execute(select(Mission).where(Mission.))

async def delete_mission(db: AsyncSession, mission_id: UUID):
    result = await db.execute(select(Mission).where(Mission.id == mission_id))
    mission = result.scalar_one_or_none()
    if mission:
        await db.delete(mission)
        await db.commit()
    return mission

async def update_mission(db: AsyncSession, mission_id: UUID, mission: MissionCreate):
    result = await db.execute(select(Mission).where(Mission.id == mission_id))
    db_mission = result.scalar_one_or_none()
    if db_mission is None:
        return None;

    for key, value in mission.dict(exclude_unset=True).items():
        setattr(db_mission, key, value)

    await db.commit()
    await db.refresh(db_mission)
    return db_mission

