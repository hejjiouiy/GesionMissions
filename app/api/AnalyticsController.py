from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any

from dependencies import get_db
from app.services.AnalyticsService import AnalyticsService

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/missions-by-type")
async def get_missions_by_type(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get missions count grouped by type"""
    try:
        analytics_service =  AnalyticsService(db)
        return await analytics_service.get_missions_by_type()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/budget-by-destination")
async def get_budget_by_destination(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get total budget grouped by destination"""
    try:
        analytics_service = AnalyticsService(db)
        return await analytics_service.get_budget_by_destination()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/missions-by-month")
async def get_missions_by_month(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get missions count by month for current and previous year"""
    try:
        analytics_service = AnalyticsService(db)
        return await analytics_service.get_missions_by_month()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/missions-by-status")
async def get_missions_by_status(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get missions count grouped by status"""
    try:
        analytics_service = AnalyticsService(db)
        return await analytics_service.get_missions_by_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-destinations")
async def get_top_destinations(
        limit: int = 5,
        db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get top destinations by mission count"""
    try:
        analytics_service = AnalyticsService(db)
        return await analytics_service.get_top_destinations(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent-missions")
async def get_recent_missions(
        limit: int = 10,
        db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get recent missions"""
    try:
        analytics_service = AnalyticsService(db)
        return await analytics_service.get_recent_missions(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_statistics(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get general statistics"""
    try:
        analytics_service = AnalyticsService(db)
        return await analytics_service.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_dashboard_analytics(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get all analytics data for dashboard"""
    try:
        analytics_service = AnalyticsService(db)
        return await analytics_service.get_all_analytics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Additional endpoints for more specific analytics

@router.get("/missions-by-user")
async def get_missions_by_user(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get missions count by user"""
    try:
        analytics_service = AnalyticsService(db)

        from app.models.ordre_mission import OrdreMission
        from sqlalchemy import func

        query = (
            db.query(
                OrdreMission.user_id,
                func.count(OrdreMission.id).label('count')
            )
            .group_by(OrdreMission.user_id)
            .order_by(func.count(OrdreMission.id).desc())
            .all()
        )

        labels = []
        data = []

        for user_id, count in query:
            # You might want to join with User table to get actual names
            labels.append(f"User {str(user_id)[:8]}")
            data.append(count)

        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Nombre de missions',
                    'data': data,
                    'backgroundColor': 'rgba(0, 84, 63, 0.7)',
                    'borderColor': 'rgba(0, 84, 63, 1)',
                    'borderWidth': 1
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/budget-evolution")
async def get_budget_evolution(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get budget evolution over time"""
    try:
        from app.models.Mission import Mission
        from app.models.ordre_mission import OrdreMission
        from sqlalchemy import func, extract

        current_year = 2024

        query = (
            db.query(
                extract('month', OrdreMission.createdAt).label('month'),
                func.sum(Mission.budgetPrevu).label('total_budget')
            )
            .join(Mission, OrdreMission.mission_id == Mission.id)
            .filter(extract('year', OrdreMission.createdAt) == current_year)
            .group_by(extract('month', OrdreMission.createdAt))
            .all()
        )

        # Initialize with 0 for all months
        monthly_budgets = [0] * 12

        for month, budget in query:
            monthly_budgets[int(month) - 1] = float(budget) if budget else 0

        return {
            'labels': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
                       'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc'],
            'datasets': [
                {
                    'label': f'Budget {current_year} (MAD)',
                    'data': monthly_budgets,
                    'borderColor': 'rgba(0, 84, 63, 1)',
                    'backgroundColor': 'rgba(0, 84, 63, 0.1)',
                    'tension': 0.4,
                    'fill': True
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))