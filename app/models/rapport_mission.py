import enum

from sqlalchemy import Column, String,LargeBinary, Boolean, DateTime, ForeignKey, Enum, Date, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid


from app.config.database import Base


class RapportMission(Base):
    __tablename__ = "rapport_mission"
    __table_args__ = {"schema": "gestion_missions"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    objective = Column(String)
    proceedings = Column(String)
    resultAchieved = Column(String)
    nextStep = Column(String)
    keyContact = Column(String)
    interlocutors = Column(String)
    difficulties = Column(String)
    recommendations = Column(String)
    isValid = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.now)
    updatedAt= Column(DateTime, default=datetime.now, onupdate=datetime.now)

    ordre_mission_id = Column(UUID(as_uuid=True), ForeignKey("gestion_missions.ordres_mission.id"), unique=True)
    ordre_mission = relationship("OrdreMission", back_populates="rapport")


# class RapportMission(Base):
#     __tablename__ = "rapport_mission"
#     __table_args__ = {"schema": "gestion_missions"}
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     contenu=Column(String, nullable=False)
#     data=Column(LargeBinary)
#     createdAt = Column(DateTime, default=datetime.now())
#     updatedAt = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
#
#     ordre_mission_id = Column(UUID(as_uuid=True), ForeignKey("gestion_missions.ordres_mission.id"), unique=True)
#     ordre_mission = relationship("OrdreMission", back_populates="rapport")