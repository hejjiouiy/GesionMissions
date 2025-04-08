from sqlalchemy import Column, String, Float, Enum, DateTime, ForeignKey

from sqlalchemy.dialects.postgresql import UUID

import enum
import uuid

from sqlalchemy.orm import relationship

from app.config.database import Base
from datetime import datetime, timezone

class TypeMission(str, enum.Enum):
    NATIONALE="Nationale"
    INTERNATIONALE="Internationale"

class EtatMission(str, enum.Enum):
    OUVERTE="Ouverte"
    EN_ATTENTE="En attente"
    VALIDEE="Validee"
    REFUSEE="Refusee"

class Mission(Base):
    __tablename__ = 'missions'
    __table_args__ = {"schema": "gestion_missions"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(TypeMission))
    destination=Column(String, nullable=False)
    details=Column(String, nullable=False)
    pays=Column(String, nullable=False)
    ville=Column(String, nullable=False)
    etat=Column(Enum(EtatMission))
    budgetPrevu=Column(Float, nullable=False)
    createdAt=Column(DateTime, default=datetime.now(timezone.utc))
    updatedAt=Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    ordres_mission = relationship("OrdreMission", back_populates="mission")