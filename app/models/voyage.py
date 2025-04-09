import enum

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.config.database import Base


class Voyage(Base):
    __tablename__ = "voyage"
    __table_args__ = {"schema": "gestion_missions"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destination = Column(String)
    moyen = Column(String)
    dateVoyage = Column(Date)

    createdAt = Column(DateTime, default=datetime.now())
    updatedAt = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    ordre_mission_id = Column(UUID(as_uuid=True), ForeignKey("gestion_missions.ordres_mission.id"))

    ordre_mission = relationship("OrdreMission", back_populates="voyages")