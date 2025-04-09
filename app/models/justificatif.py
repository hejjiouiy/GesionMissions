import enum

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Date, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.config.database import Base


class Justificatif(Base):
    __tablename__ = "justificatif"
    __table_args__ = {"schema": "gestion_missions"}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data = Column(LargeBinary, nullable=False)
    createdAt = Column(DateTime, default=datetime.now())
    modifiedAt = Column(DateTime, default=datetime.now() , onupdate=datetime.now())

    financement_id = Column(UUID(as_uuid=True), ForeignKey("gestion_missions.financement.id"))

    financement = relationship("Financement", back_populates="justificatifs")