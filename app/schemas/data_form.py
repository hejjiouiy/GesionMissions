from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, validator

from app.models.enums.Enums import TypeFinancementEnum, EtatMission, TypeMission


class StepMissionDetails(BaseModel):
    # Make all fields optional since they might not be needed for existing missions
    type: Optional[str] = None
    destination: Optional[str] = None
    titre: Optional[str] = None
    details: Optional[str] = None
    pays: Optional[str] = None
    ville: Optional[str] = None
    budgetPrevu: Optional[float] = None
    etat: Optional[str] = None
    missionId: Optional[str] = None  # For existing missions
    dateDebut: Optional[date] = None

    @validator('*', pre=True)
    def validate_mission_requirements(cls, v, values):
        # If we have a missionId, we don't need other fields
        if 'missionId' in values and values['missionId']:
            return v

        # If no missionId, then we need the required fields for new mission
        # This validation will be handled by the endpoint logic
        return v

class StepOrderDetails(BaseModel):
    dateDebut: date
    dateFin: date
    etat: EtatMission = EtatMission.OUVERTE  # Use your actual enum
    includeTravel: bool = False
    includeAccommodation: bool = False
    includeFinancing: bool = False
    # Remove user_id and mission_id - we'll add them in the router

class StepTravelDetails(BaseModel):
    destination: str
    moyen: str
    dateVoyage: datetime
    # Remove ordre_mission_id - we'll add it in the router

class StepAccommodationDetails(BaseModel):
    dateDebut: date
    dateFin: date
    localisation: str
    typeHebergement: str

class StepFinancingDetails(BaseModel):
    type: TypeFinancementEnum  # Use your actual enum
    details: Optional[str] = None
    devise: Optional[str] = "MAD"
    valide: Optional[bool] = False

class DataForm(BaseModel):
    mission_details: StepMissionDetails
    order_details: StepOrderDetails
    travel_details: Optional[StepTravelDetails] = None
    accommodation_details: Optional[StepAccommodationDetails] = None
    financing_details: Optional[StepFinancingDetails] = None


def validate_mission_data(form_data: DataForm):
    """Validate that either missionId or all required fields are provided"""
    mission = form_data.mission_details

    if mission.missionId:
        # Using existing mission - missionId is sufficient
        return True

    # Creating new mission - check required fields
    required_fields = {
        'type': mission.type,
        'destination': mission.destination,
        'titre': mission.titre,
        'pays': mission.pays,
        'ville': mission.ville,
        'budgetPrevu': mission.budgetPrevu
    }

    missing_fields = [field for field, value in required_fields.items() if not value]

    if missing_fields:
        raise ValueError(f"Missing required fields for new mission: {', '.join(missing_fields)}")

    return True