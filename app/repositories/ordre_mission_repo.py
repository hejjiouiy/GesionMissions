from datetime import date, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.enums.Enums import EtatMission
from app.models.ordre_mission import OrdreMission
from app.schemas.ordre_mission_schema import OrdreMissionCreate
from app.api.form_submission import logger

async def create_ordre(db: AsyncSession, ordre_mission: OrdreMissionCreate, file_data : bytes = None):
    db_ordre_mission = OrdreMission(**ordre_mission.dict())
    if file_data is not None:
        db_ordre_mission.accord_respo = file_data
    db.add(db_ordre_mission)
    await db.commit()
    await db.refresh(db_ordre_mission)
    return db_ordre_mission

async def create_ordre_with_verification(db: AsyncSession, ordre_mission: OrdreMissionCreate, file_data : bytes = None):
    """
        Enhanced version with more detailed verification and logging
        """

    # Get all user's existing orders
    result = await db.execute(select(OrdreMission).where(
        OrdreMission.user_id == ordre_mission.user_id
    ).options(
        selectinload(OrdreMission.rapport)
    ))
    old_user_orders = result.scalars().all()

    # Define order states
    OPEN_STATES = {
        EtatMission.OUVERTE: "Open - Awaiting review",
        EtatMission.EN_ATTENTE: "Pending - Under review",
        EtatMission.VALIDEE_HIERARCHIQUEMENT: "Hierarchically validated",
        EtatMission.VALIDEE_BUDGETAIREMENT: "Budget validated",
        EtatMission.APPROUVEE: "Approved - Ready for execution"
    }

    CLOSED_STATES = {
        EtatMission.CLOTUREE: "Closed - Mission completed",
        EtatMission.REFUSEE: "Refused - Mission denied"
    }

    cutoff_date = date.today() - timedelta(days=15)

    # Categorize existing orders
    open_orders = []
    closed_orders_without_reports = []

    for order in old_user_orders:
        if order.etat in OPEN_STATES:
            open_orders.append(order)
        elif (order.etat in CLOSED_STATES and
              order.dateFin < cutoff_date and
              not order.rapport):
            closed_orders_without_reports.append(order)

    # Check for missing reports first
    if closed_orders_without_reports:
        missing_count = len(closed_orders_without_reports)
        return {
            "error": "Missing Reports Required",
            "message": f"You have {missing_count} completed mission(s) that require reports before submitting new requests. Please upload the missing reports.",
            "details": {
                "missing_reports_count": missing_count,
                "missions_without_reports": [
                    {
                        "order_id": str(order.id),
                        "end_date": order.dateFin.isoformat(),
                        "status": order.etat.value
                    }
                    for order in closed_orders_without_reports
                ]
            }
        }

    # Check for open orders
    if open_orders:
        active_order = open_orders[0]  # Get the first active order
        return {
            "error": "Active Mission Exists",
            "message": f"You already have an active mission order. Status: {OPEN_STATES[active_order.etat]}",
            "details": {
                "active_order_id": str(active_order.id),
                "current_status": active_order.etat.value,
                "status_description": OPEN_STATES[active_order.etat],
                "start_date": active_order.dateDebut.isoformat(),
                "end_date": active_order.dateFin.isoformat()
            }
        }

    # All verifications passed
    logger.info(f"All verifications passed for user {ordre_mission.user_id}")

    db_ordre_mission = OrdreMission(**ordre_mission.dict())
    if file_data is not None:
        db_ordre_mission.accord_respo = file_data

    db.add(db_ordre_mission)
    await db.commit()
    await db.refresh(db_ordre_mission)

    logger.info(f"New order created successfully with ID: {db_ordre_mission.id}")
    return db_ordre_mission


async def get_order_by_userId(db: AsyncSession, user_id: UUID) :
    result = await db.execute(select(OrdreMission).where(OrdreMission.user_id == user_id).
                              options(
        selectinload(OrdreMission.mission),
        selectinload(OrdreMission.financement),
        selectinload(OrdreMission.rapport)
    ))
    return result.scalars().all()


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