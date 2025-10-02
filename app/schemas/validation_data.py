from uuid import UUID

from pydantic import BaseModel
from typing import Optional
from app.schemas.ligne_budgetaire_schema import LigneBudgetaireCreate


class ValidationData(BaseModel):
    ligneBudgetaire: Optional[LigneBudgetaireCreate] = None
    ligneBudgetaireId: Optional[UUID] = None  # For existing budget lines
    montantEstime: Optional[float] = None
    comment: Optional[str] = None


