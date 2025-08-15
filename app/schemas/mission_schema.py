from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.models.Mission import TypeMission, EtatMission


class MissionCreate(BaseModel):
    type: TypeMission
    destination:str
    titre:str
    details:Optional[str]
    pays:str
    ville:str
    budgetPrevu:float

class MissionOut(MissionCreate):
    id:UUID
    createdAt:datetime
    updatedAt:Optional[datetime]
