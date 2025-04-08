from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, DateTime, Date, LargeBinary
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class OrdreMission(Base):
    __tablename__ = 'ordres_mission'
    __table_args__ = {"schema": "gestion_missions"}

    id=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    accord_respo = Column(LargeBinary, nullable=False)
    dateDebut =Column(Date)
    dateFin =Column(Date)
    createdAt=Column(DateTime, default=datetime.now(timezone.utc))
    updatedAt=Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    user_id=Column(UUID(as_uuid=True))
    mission_id=Column(UUID(as_uuid=True), ForeignKey('gestion_missions.missions.id'))

    mission = relationship("Mission", back_populates="ordres_mission", cascade="all, delete-orphan")
    financement = relationship("Financement", back_populates="ordre_mission",uselist=False, cascade="all, delete-orphan")
    voyages = relationship("Voyage", back_populates="ordre_mission", cascade="all, delete-orphan")
    rapport = relationship("RapportMission", back_populates="ordre_mission", cascade="all, delete")
    hebergements = relationship("Hebergement", back_populates="ordre_mission", cascade="all, delete-orphan")