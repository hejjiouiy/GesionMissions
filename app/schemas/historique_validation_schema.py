from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.models.enums.Enums import EtatMission


class HistoriqueValidationCreate(BaseModel):
    user_id:UUID
    role:str
    ordre_mission_id:UUID
    etat:EtatMission

class HistoriqueValidationOut(HistoriqueValidationCreate):
    id: UUID
    timestamp: datetime