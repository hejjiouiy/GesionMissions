from sqlalchemy import Column, String, Float, Enum, DateTime, ForeignKey

from sqlalchemy.dialects.postgresql import UUID
from app.models.ordre_mission import OrdreMission

import enum
import uuid

from sqlalchemy.orm import relationship

from app.config.database import Base
from datetime import datetime, timezone
from app.models.enums.Enums import TypeMission,EtatMission


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
    createdAt=Column(DateTime, default=datetime.now())
    updatedAt=Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    ordres_mission = relationship("OrdreMission", back_populates="mission")