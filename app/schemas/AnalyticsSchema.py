from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import date


class ChartDataset(BaseModel):
    label: str
    data: List[float]
    backgroundColor: Optional[List[str]] = None
    borderColor: Optional[List[str]] = None
    borderWidth: Optional[int] = 1
    tension: Optional[float] = None
    fill: Optional[bool] = None


class ChartData(BaseModel):
    labels: List[str]
    datasets: List[ChartDataset]


class TopDestination(BaseModel):
    destination: str
    count: int


class RecentMission(BaseModel):
    id: str
    destination: str
    type: str
    dateDebut: Optional[str]
    dateFin: Optional[str]
    status: str


class Statistics(BaseModel):
    totalMissions: int
    missionsEnCours: int
    budgetTotal: float
    moyenneDuree: float


class DashboardAnalytics(BaseModel):
    missionsByType: ChartData
    budgetByDestination: ChartData
    missionsByMonth: ChartData
    missionsByStatus: ChartData
    topDestinations: List[TopDestination]
    recentMissions: List[RecentMission]
    statistics: Statistics


# Additional schemas for specific endpoints

class UserMissionCount(BaseModel):
    user_id: str
    count: int
    user_name: Optional[str] = None


class MonthlyBudget(BaseModel):
    month: int
    budget: float


class MissionStatusCount(BaseModel):
    status: str
    count: int
    percentage: float


class AnalyticsFilters(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    user_id: Optional[str] = None
    mission_type: Optional[str] = None
    destination: Optional[str] = None