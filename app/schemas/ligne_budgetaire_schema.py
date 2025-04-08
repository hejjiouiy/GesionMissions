from datetime import datetime,date
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class LigneBudgetaireCreate(BaseModel):
    codeLigne:str
    nom:str
    exerciceBudgetaire: int

class LigneBudgetaireOut(LigneBudgetaireCreate):
    id: UUID