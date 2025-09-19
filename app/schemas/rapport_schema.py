from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class RapportCreate(BaseModel):
    objective: Optional[str]
    proceedings: Optional[str]
    resultAchieved: Optional[str]
    nextStep: Optional[str]
    keyContact: Optional[str]
    interlocutors: Optional[str]
    difficulties: Optional[str]
    recommendations: Optional[str]
    ordre_mission_id: UUID
    isValid:Optional[bool] = False

class RapportOut(RapportCreate):
    id: UUID
    createdAt: datetime
    updatedAt: Optional[datetime]
    class Config:
        from_attributes = True

