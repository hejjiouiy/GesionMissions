from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.models.enums.Enums import EtatMission


class RemboursementCreate(BaseModel):
    etat:EtatMission
    financement_id: UUID
    valide:Optional[bool] = False
    dateDemande: date

class RemboursementOut(RemboursementCreate):
    id:UUID
    createdAt : datetime
    updatedAt : Optional[datetime]