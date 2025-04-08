from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.models.financement import TypeFinancementEnum


class FinancementCreate(BaseModel):
    type: TypeFinancementEnum
    details: Optional[str]
    valide: Optional[bool]=False
    devise: Optional[str]="MAD"
    ordre_mission_id: UUID

class FinancementOut(FinancementCreate):
    id: UUID
    createdAt: datetime
    updatedAt: Optional[datetime]
