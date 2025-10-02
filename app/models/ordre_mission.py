from datetime import datetime

from sqlalchemy import Column, String,Float, ForeignKey, DateTime, Date, LargeBinary, Enum
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

from app.models.enums.Enums import EtatMission
from app.models.financement import Financement
from app.models.voyage import Voyage
from app.models.rapport_mission import RapportMission
from app.models.hebergement import Hebergement
from app.models.ligne_budgetaire import LigneBudgetaire

class OrdreMission(Base):
    __tablename__ = 'ordres_mission'
    __table_args__ = {"schema": "gestion_missions"}

    id=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    accord_respo = Column(LargeBinary, nullable=False)
    dateDebut =Column(Date)
    dateFin =Column(Date)
    etat=Column(Enum(EtatMission , name='etatmission',schema='gestion_missions', create_type=False), default=EtatMission.OUVERTE)
    createdAt=Column(DateTime, default=datetime.now())
    updatedAt=Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    montant_alloue = Column(Float)
    user_id=Column(UUID(as_uuid=True))
    mission_id=Column(UUID(as_uuid=True), ForeignKey('gestion_missions.missions.id'))
    ligne_budgetaire_id = Column(UUID(as_uuid=True),ForeignKey('gestion_missions.ligne_budgetaire.id'))

    mission = relationship("Mission", back_populates="ordres_mission")
    financement = relationship("Financement", back_populates="ordre_mission",uselist=False, cascade="all, delete-orphan")
    voyages = relationship("Voyage", back_populates="ordre_mission", cascade="all, delete-orphan")
    rapport = relationship("RapportMission", back_populates="ordre_mission", cascade="all, delete")
    hebergements = relationship("Hebergement", back_populates="ordre_mission", cascade="all, delete-orphan")
    historique = relationship("HistoriqueValidation", back_populates="ordre_mission", cascade="all, delete")
    ligne_budgetaire = relationship("LigneBudgetaire",back_populates="ordre_mission", cascade="all, delete")
