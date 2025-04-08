from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class RapportCreate(BaseModel):
    contenu:str
    ordre_mission_id: UUID

class RapportOut(RapportCreate):
    id: UUID
    createdAt: datetime
    updatedAt: Optional[datetime]

