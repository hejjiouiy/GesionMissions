import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from uuid import UUID
from app.api.hebergement_controller import router

# Create test app and client
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Fake hébergement data
fake_hebergement = {
    "id": "c9d8b115-737c-4f90-8c04-ae896456e4f8",
    "dateFin": "2025-04-26",
    "typeHebergement": "HOTEL",
    "localisation": "FES",
    "dateDebut": "2025-04-23",
    "ordre_mission_id": "c7056413-6cf1-4bd6-ac71-45001fef5d81"
}

def test_get_hebergements(monkeypatch):
    async def mock_get_hebergements(db):
        return [fake_hebergement]

    monkeypatch.setattr("app.repositories.hebergement_repo.get_hebergements", mock_get_hebergements)

    response = client.get("/hebergement/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == fake_hebergement["id"]
    # Accéder aux propriétés du premier élément de la liste
    assert data[0]["typeHebergement"] == "HOTEL"
    assert data[0]["localisation"] == "FES"

def test_create_hebergement(monkeypatch):
    async def mock_create_hebergement(db, hebergement):
        return fake_hebergement

    monkeypatch.setattr("app.repositories.hebergement_repo.create_hebergement", mock_create_hebergement)

    response = client.post("/hebergement/add", json={
    "dateFin": "2025-04-26",
    "typeHebergement": "HOTEL",
    "localisation": "FES",
    "dateDebut": "2025-04-23",
    "ordre_mission_id": "c7056413-6cf1-4bd6-ac71-45001fef5d81"
    })
    assert response.status_code == 200
    assert response.json()["typeHebergement"] == "HOTEL"
    assert response.json()["localisation"] == "FES"

def test_update_hebergement(monkeypatch):
    async def mock_update_hebergement(db, hebergement_id, hebergement_update):
        return fake_hebergement

    monkeypatch.setattr("app.repositories.hebergement_repo.update_hebergement", mock_update_hebergement)

    response = client.put(f"/hebergement/update-{fake_hebergement['id']}", json={
        "dateFin": "2025-04-26",
        "typeHebergement": "HOTEL",
        "localisation": "FES",
        "dateDebut": "2025-04-23",
        "ordre_mission_id": "c7056413-6cf1-4bd6-ac71-45001fef5d81"
    })
    assert response.status_code == 200
    assert response.json()["id"] == fake_hebergement["id"]
    # Les valeurs retournées sont toujours celles du fake_hebergement car c'est ce que notre mock renvoie
    assert response.json()["typeHebergement"] == "HOTEL"

def test_update_hebergement_not_found(monkeypatch):
    async def mock_update_hebergement_not_found(db, hebergement_id, hebergement_update):
        return None

    monkeypatch.setattr("app.repositories.hebergement_repo.update_hebergement", mock_update_hebergement_not_found)

    response = client.put(f"/hebergement/update-{fake_hebergement['id']}", json={
        "dateFin": "2025-04-26",
        "typeHebergement": "HOTEL",
        "localisation": "FES",
        "dateDebut": "2025-04-23",
        "ordre_mission_id": "c7056413-6cf1-4bd6-ac71-45001fef5d81"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Hebergement non trouvé"

def test_delete_hebergement(monkeypatch):
    async def mock_delete_hebergement(db, hebergement_id):
        return fake_hebergement

    monkeypatch.setattr("app.repositories.hebergement_repo.delete_hebergement", mock_delete_hebergement)

    response = client.delete(f"/hebergement/delete/{fake_hebergement['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == fake_hebergement["id"]
    assert response.json()["typeHebergement"] == "HOTEL"

def test_delete_hebergement_not_found(monkeypatch):
    async def mock_delete_hebergement_not_found(db, hebergement_id):
        return None

    monkeypatch.setattr("app.repositories.hebergement_repo.delete_hebergement", mock_delete_hebergement_not_found)

    response = client.delete(f"/hebergement/delete/{fake_hebergement['id']}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Heberegement non trouvé"