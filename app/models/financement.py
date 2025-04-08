import enum

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.config.database import Base

class TypeFinancementEnum(str, enum.Enum):
    PERSONNEL = "PERSONNEL"
    PARRAINAGE = "PARRAINAGE"
    INTERNE = "INTERNE"

class Financement(Base):
    __tablename__ = "financement"
    __table_args__ = {"schema": "gestion_missions"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(TypeFinancementEnum), nullable=False)
    details = Column(String)
    valide = Column(Boolean, default=False)
    devise = Column(String)

    createdAt = Column(DateTime, default=datetime.now(timezone.utc))
    updatedAt = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    ordre_mission_id = Column(UUID(as_uuid=True), ForeignKey("gestion_missions.ordres_mission.id"), unique=True)

    ordre_mission = relationship("OrdreMission", back_populates="financement")
    justificatifs = relationship("Justificatif", back_populates="financement")
