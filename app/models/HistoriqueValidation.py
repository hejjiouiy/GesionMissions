from sqlalchemy import Column, String, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.models.enums.Enums import EtatMission
from app.config.database import Base



class HistoriqueValidation(Base):
    __tablename__ = "historique_validation"
    __table_args__ = {"schema": "gestion_missions"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ordre_mission_id = Column(UUID(as_uuid=True), ForeignKey("gestion_missions.ordres_mission.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    role = Column(String, nullable=False)
    etat = Column(Enum(EtatMission), nullable=False)
    timestamp = Column(DateTime, default=datetime.now())

    ordre_mission = relationship("OrdreMission", back_populates="historique")
