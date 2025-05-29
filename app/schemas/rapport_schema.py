from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class RapportCreate(BaseModel):
    objective:str
    proceedings:str
    resultAchieved:str
    nextStep:str
    keyContact:str
    interlocutors:str
    difficulties:str
    recommendations:str
    ordre_mission_id: UUID
    isValid:bool

class RapportOut(RapportCreate):
    id: UUID
    createdAt: datetime
    updatedAt: Optional[datetime]

