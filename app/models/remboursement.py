import enum

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Date, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.models.Mission import EtatMission

from app.config.database import Base


class Remboursement(Base):
    __tablename__ = "remboursement"
    __table_args__ = {"schema": "gestion_missions"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    etat=Column(Enum(EtatMission, name='etatmission',schema='gestion_missions', create_type=False))
    valide = Column(Boolean , default=False)
    dateDemande = Column(Date)

    createdAt = Column(DateTime, default=datetime.now())
    updatedAt = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    financement_id = Column(UUID(as_uuid=True), ForeignKey("gestion_missions.financement.id"))

    financement = relationship("Financement", back_populates="remboursements")