from pydantic import BaseModel
from typing import Optional
from app.schemas.ligne_budgetaire_schema import LigneBudgetaireCreate


class ValidationData(BaseModel):
    ligneBudgetaire: Optional[LigneBudgetaireCreate] = None
    comment : Optional[str] = None


