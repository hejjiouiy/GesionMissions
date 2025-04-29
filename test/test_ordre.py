import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException, status
from uuid import uuid4, UUID
from datetime import date
from app.api.ordre_controller import router, update_etat, process_etat_update  # Adjust import if needed
from app.models.enums.Enums import EtatMission
from unittest.mock import AsyncMock, MagicMock
from contextlib import asynccontextmanager

from app.models.ordre_mission import OrdreMission
from app.repositories import ordre_mission_repo, historique_validation_repo
from app.schemas.historique_validation_schema import HistoriqueValidationCreate

# Setup FastAPI app for testing
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Fake ordre response
fake_ordre = {
    "id": str(uuid4()),
    "etat": "Approuvee",
    "dateDebut": "2025-04-23",
    "dateFin": "2025-04-27",
    "user_id": str(uuid4()),
    "mission": {
        "type": "Nationale",
        "id": str(uuid4())
    },
    "financement": "Interne",
    "rapport": None,
    "accord_respo": b"FakeFileContent"
}

# ----------------------------
def test_get_ordres(monkeypatch):
    async def mock_get_ordres(db):
        class FakeOrdre:
            def __init__(self):
                self.id = fake_ordre["id"]
                self.etat = fake_ordre["etat"]
                self.dateDebut = fake_ordre["dateDebut"]
                self.dateFin = fake_ordre["dateFin"]
                self.user_id = fake_ordre["user_id"]
                self.mission = fake_ordre["mission"]
                self.financement = fake_ordre["financement"]
                self.rapport = fake_ordre["rapport"]
                self.accord_respo = fake_ordre["accord_respo"]
        return [FakeOrdre()]

    monkeypatch.setattr("app.repositories.ordre_mission_repo.get_ordres", mock_get_ordres)

    response = client.get("/order/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["etat demande"] == "Approuvee"

# ----------------------------
def test_create_ordre(monkeypatch):
    fake_ordre = {
        "id": str(uuid4()),
        "etat": "Ouverte",
        "mission_id": str(uuid4()),
        "user_id": str(uuid4()),
        "createdAt": "2025-04-29T10:51:12.008667",
        "updatedAt": "2025-04-29T10:51:12.008677"
    }

    async def mock_create_ordre(db, ordre, file_data):
        return {
            **fake_ordre,
            "dateDebut": str(ordre.dateDebut),
            "dateFin": str(ordre.dateFin)
        }

    monkeypatch.setattr("app.repositories.ordre_mission_repo.create_ordre", mock_create_ordre)

    # Use strings for data since form fields come as strings
    data = {
        "dateDebut": "2025-04-23",
        "dateFin": "2025-04-27",
        "mission_id": fake_ordre["mission_id"],
        "user_id": fake_ordre["user_id"]
    }

    files = {
        "file": ("fake.pdf", b"fake content", "application/pdf")
    }

    response = client.post("/order/add", data=data, files=files)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["etat"] == "Ouverte"
    assert response_data["mission_id"] == fake_ordre["mission_id"]
    assert response_data["user_id"] == fake_ordre["user_id"]
    assert response_data["dateDebut"] == "2025-04-23"
    assert response_data["dateFin"] == "2025-04-27"


# ----------------------------
def test_update_ordre(monkeypatch):
    async def mock_update(db, ordre_id, ordre_update):
        return {
            **fake_ordre,
            "dateDebut": str(ordre_update.dateDebut),
        "dateFin": str(ordre_update.dateFin),
        "mission_id": ordre_update.mission_id,
        "user_id": ordre_update.user_id,
        "createdAt": "2025-04-01T10:00:00",
        "updatedAt": "2025-04-22T12:00:00"
        }

    monkeypatch.setattr("app.repositories.ordre_mission_repo.update_ordre_mission", mock_update)

    payload = {
        "dateDebut": "2025-04-23",
        "dateFin": "2025-04-27",
        "mission_id": str(uuid4()),
        "user_id": str(uuid4())
    }

    response = client.put(f"/order/update-{fake_ordre['id']}", json=payload)
    assert response.status_code == 200
    assert response.json()["etat"] == "Approuvee"

# ----------------------------
def test_delete_ordre(monkeypatch):
    async def mock_delete(db, ordre_id):
        return {
            **fake_ordre,
            "mission_id": str(uuid4()),
            "createdAt": "2025-04-01T10:00:00",
            "updatedAt": "2025-04-22T12:00:00"
        }

    monkeypatch.setattr("app.repositories.ordre_mission_repo.delete_ordre", mock_delete)

    response = client.delete(f"/order/delete/{fake_ordre['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == fake_ordre["id"]

# ----------------------------


@pytest.mark.asyncio
async def test_etat_update(monkeypatch):
    # Create a mock order
    ordre_mock = MagicMock()
    ordre_mock.id = fake_ordre["id"]
    ordre_mock.etat = EtatMission.OUVERTE
    ordre_mock.dateDebut = "2025-04-23"
    ordre_mock.dateFin = "2025-04-27"
    ordre_mock.user_id = fake_ordre["user_id"]
    ordre_mock.mission = fake_ordre["mission"]
    ordre_mock.financement = fake_ordre["financement"]
    ordre_mock.rapport = fake_ordre["rapport"]
    ordre_mock.accord_respo = fake_ordre["accord_respo"]

    # Mock the repository functions
    async def mock_get_by_id(db, ordre_id):
        return ordre_mock

    async def mock_create_historiqueValidation(db, histo):
        return histo

    # Apply the mocks to the repositories
    monkeypatch.setattr("app.repositories.ordre_mission_repo.get_ordre_by_id", mock_get_by_id)
    monkeypatch.setattr("app.repositories.historique_validation_repo.create_historiqueValidation",
                        mock_create_historiqueValidation)

    # Create a mock DB session
    mock_db = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock(side_effect=Exception("This will be caught"))  # Intentionally fail

    # Define the test parameters
    user_id = str(fake_ordre["user_id"])
    user_roles = "CG"
    ordre_mission_id = fake_ordre["id"]

    # Call the business logic function directly - this is the key difference
    result = await process_etat_update(
        user_id=user_id,
        user_roles=user_roles,
        ordre_mission_id=ordre_mission_id,
        db=mock_db
    )

    # Verify the result
    assert result["etat de mission"] == EtatMission.EN_ATTENTE
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()