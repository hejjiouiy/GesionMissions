from datetime import date, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.ordre_mission import OrdreMission
from app.schemas.ordre_mission_schema import OrdreMissionCreate

async def create_ordre(db: AsyncSession, ordre_mission: OrdreMissionCreate, file_data : bytes = None):
    db_ordre_mission = OrdreMission(**ordre_mission.dict())
    if file_data is not None:
        db_ordre_mission.accord_respo = file_data
    db.add(db_ordre_mission)
    await db.commit()
    await db.refresh(db_ordre_mission)
    return db_ordre_mission

async def create_ordre_with_verification(db: AsyncSession, ordre_mission: OrdreMissionCreate, file_data : bytes = None):
    result = await db.execute(select(OrdreMission).where(
        OrdreMission.user_id == ordre_mission.user_id
    ).options(
        selectinload(OrdreMission.rapport)
    ))
    old_user_orders = result.scalars().all()

    cutoff_date = date.today() - timedelta(days=15)

    for old_user_order in old_user_orders:
        print("*************************************")
        print("*************************************")
        print("*************************************")
        print(cutoff_date.isoformat())
        print("*************************************")
        print("*************************************")
        print("*************************************")
        print(old_user_order.dateFin.isoformat())
        print("*************************************")
        print("*************************************")
        print("*************************************")
        print(old_user_order.id)
        print("*************************************")
        print("*************************************")
        print(not old_user_order.rapport)
        print("*************************************")
        if(old_user_order.dateFin < cutoff_date and not old_user_order.rapport):
            return {
                "error": "Service Unavailable",
                "message": "Please upload reports for your old missions before creating a new one"
            }

    db_ordre_mission = OrdreMission(**ordre_mission.dict())
    if file_data is not None:
        db_ordre_mission.accord_respo = file_data
    db.add(db_ordre_mission)
    await db.commit()
    await db.refresh(db_ordre_mission)
    return db_ordre_mission



    db_ordre_mission = OrdreMission(**ordre_mission.dict())
    if file_data is not None:
        db_ordre_mission.accord_respo = file_data
    db.add(db_ordre_mission)
    await db.commit()
    await db.refresh(db_ordre_mission)
    return db_ordre_mission


async def get_ordre_by_id(db: AsyncSession, ordre_id: UUID):
    result = await db.execute(select(OrdreMission).where(OrdreMission.id == ordre_id).options(
            selectinload(OrdreMission.mission),
            selectinload(OrdreMission.financement),
        selectinload(OrdreMission.rapport)
        ))
    return result.scalar_one_or_none()

async def get_ordres(db: AsyncSession, skip: int = 0, limit: int =100):
    result = await db.execute(select(OrdreMission).options(
            selectinload(OrdreMission.mission),
            selectinload(OrdreMission.financement),
        selectinload(OrdreMission.rapport)
        ).offset(skip).limit(limit))
    return result.scalars().all()

async def delete_ordre(db: AsyncSession, ordre_mission_id: UUID):
    result = await db.execute(select(OrdreMission).where(OrdreMission.id == ordre_mission_id))
    ordre_mission = result.scalar_one_or_none()
    if ordre_mission:
        await db.delete(ordre_mission)
        await db.commit()
    return ordre_mission

async def update_ordre_mission(db: AsyncSession, ordre_mission_id: UUID, ordre_mission: OrdreMissionCreate):
    result = await db.execute(select(OrdreMission).where(OrdreMission.id == ordre_mission_id))
    db_ordre_mission = result.scalar_one_or_none()
    if db_ordre_mission is None:
        return None;

    for key, value in ordre_mission.dict(exclude_unset=True).items():
        setattr(db_ordre_mission, key, value)

    await db.commit()
    await db.refresh(db_ordre_mission)
    return db_ordre_mission