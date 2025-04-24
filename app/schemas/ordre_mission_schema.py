from datetime import date, datetime

from fastapi import File
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.models.enums.Enums import EtatMission


class OrdreMissionCreate(BaseModel):
    dateDebut : date
    dateFin : date
    etat:EtatMission= EtatMission.OUVERTE
    mission_id: UUID
    user_id: UUID

class OrderMissionOut(OrdreMissionCreate):
    id: UUID
    createdAt: datetime
    updatedAt: Optional[datetime]

    class Config:
        orm_mode = True
