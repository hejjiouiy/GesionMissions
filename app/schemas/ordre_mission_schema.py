from datetime import date, datetime

from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class OrdreMissionCreate(BaseModel):
    dateDebut : date
    dateFin : date
    mission_id: UUID
    user_id: UUID

class OrderMissionOut(OrdreMissionCreate):
    id: UUID
    createdAt: datetime
    updatedAt: Optional[datetime]

    class Config:
        orm_mode = True
