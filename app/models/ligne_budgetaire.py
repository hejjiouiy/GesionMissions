import enum

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.config.database import Base


class LigneBudgetaire(Base):
    __tablename__ = "ligne_budgetaire"
    __table_args__ = {"schema": "gestion_missions"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codeLigne = Column(String, nullable=False)
    nom = Column(String, nullable=False)
    exerciceBudgetaire = Column(String, nullable=False)
