from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class HebergementCreate(BaseModel):
    dateDebut: date
    dateFin: date
    localisation: str
    typeHebergement: str
    ordre_mission_id: UUID


class HeberegementOut(HebergementCreate):
    id: UUID
