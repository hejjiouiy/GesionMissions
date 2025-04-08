from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class VoyageCreate(BaseModel):
    destination: str
    moyen: str
    dateVoyage: datetime
    ordre_mission_id: UUID

class VoyageOut(VoyageCreate):
    id:UUID
    createdAt: datetime
    updatedAt: Optional[datetime]