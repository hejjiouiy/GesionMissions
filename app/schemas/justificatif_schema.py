from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class JustificatifCreate(BaseModel):
    financement_id:UUID

class JustificatifOut(BaseModel):
    id: UUID
    createdAt: datetime
    modifiedAt:Optional[datetime]