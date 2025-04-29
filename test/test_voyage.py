import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from uuid import UUID, uuid4
from datetime import date, datetime
from app.api.voyage_controller import router

# Créer une application de test
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Données de test
fake_voyage_id = uuid4()
fake_ordre_mission_id = uuid4()


# Classe mock pour simuler la relation avec ordre_mission
class MockOrdreMission:
    def __init__(self, id=fake_ordre_mission_id):
        self.id = id


# Classe mock pour simuler un voyage
class MockVoyage:
    def __init__(self):
        self.id = fake_voyage_id
        self.destination = "Marrakech"
        self.moyen = "AVION"
        self.dateVoyage = date(2025, 5, 15)
        self.ordre_mission_id = fake_ordre_mission_id
        self.ordre_mission = MockOrdreMission()
        self.createdAt = datetime(2025, 4, 29, 10, 30, 28, 833312)
        self.updatedAt = datetime(2025, 4, 29, 10, 30, 28, 833323)


# Données JSON de voyage pour les tests
fake_voyage_json = {
    "id": str(fake_voyage_id),
    "destination": "Marrakech",
    "moyen": "AVION",
    "dateVoyage": "2025-05-15",
    "ordre_mission_id": str(fake_ordre_mission_id),
    "createdAt": "2025-04-29T10:30:28.833312",
    "updatedAt": "2025-04-29T10:30:28.833323"
}


# Test pour récupérer tous les voyages
def test_get_voyages(monkeypatch):
    # Mock voyage à retourner par le repository
    mock_voyage = MockVoyage()

    # Mocker la fonction du repository
    async def mock_get_voyages(db):
        return [mock_voyage]

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.voyage_repo.get_voyages", mock_get_voyages)

    # Faire l'appel API
    response = client.get("/voyage/")

    # Vérifier les résultats
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(fake_voyage_id)
    assert data[0]["destination"] == "Marrakech"
    assert data[0]["moyen"] == "AVION"
    assert data[0]["ordre de mission"] == str(fake_ordre_mission_id)


# Test pour créer un voyage
def test_create_voyage(monkeypatch):
    # Données du nouveau voyage
    new_voyage_data = {
        "destination": "Casablanca",
        "moyen": "TRAIN",
        "dateVoyage": "2025-06-20",
        "ordre_mission_id": str(fake_ordre_mission_id)
    }

    # Mocker la fonction du repository
    async def mock_create_voyage(db, voyage_data):
        # Simuler l'enrichissement des données par la base de données
        return {
            "id": str(uuid4()),
            **new_voyage_data,
            "dateVoyage": "2025-06-20T00:00:00",
            "createdAt": "2025-04-30T10:30:28.833312",
            "updatedAt": "2025-04-30T10:30:28.833312"
        }

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.voyage_repo.create_voyage", mock_create_voyage)

    # Faire l'appel API
    response = client.post("/voyage/add", json=new_voyage_data)

    # Vérifier les résultats
    assert response.status_code == 200
    result = response.json()
    assert "id" in result
    assert result["destination"] == new_voyage_data["destination"]
    assert result["moyen"] == new_voyage_data["moyen"]
    assert result["dateVoyage"].startswith(new_voyage_data["dateVoyage"])
    assert result["ordre_mission_id"] == new_voyage_data["ordre_mission_id"]
    assert "createdAt" in result
    assert "updatedAt" in result


# Test pour mettre à jour un voyage
def test_update_voyage(monkeypatch):
    # Données de mise à jour
    update_data = {
        "destination": "Tanger",
        "moyen": "VOITURE",
        "dateVoyage": "2025-07-10",
        "ordre_mission_id": str(fake_ordre_mission_id)
    }

    # Mocker la fonction du repository
    async def mock_update_voyage(db, voyage_id, voyage_update):
        # Vérifier que l'ID correspond bien à notre voyage fictif
        if str(voyage_id) == str(fake_voyage_id):
            # Retourner les données mises à jour
            return {
                **fake_voyage_json,
                **update_data,
                "updatedAt": "2025-04-30T11:45:28.833323"
            }
        return None

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.voyage_repo.update_voyage", mock_update_voyage)

    # Faire l'appel API
    response = client.put(f"/voyage/update-{fake_voyage_id}", json=update_data)

    # Vérifier les résultats
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == str(fake_voyage_id)
    assert result["destination"] == update_data["destination"]
    assert result["moyen"] == update_data["moyen"]
    assert result["dateVoyage"].startswith(update_data["dateVoyage"])


# Test pour mettre à jour un voyage qui n'existe pas
def test_update_voyage_not_found(monkeypatch):
    # Données de mise à jour
    update_data = {
        "destination": "Tanger",
        "moyen": "VOITURE",
        "dateVoyage": "2025-07-10",
        "ordre_mission_id": str(fake_ordre_mission_id)
    }

    # Mocker la fonction du repository pour retourner None (voyage non trouvé)
    async def mock_update_voyage_not_found(db, voyage_id, voyage_update):
        return None

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.voyage_repo.update_voyage", mock_update_voyage_not_found)

    # Faire l'appel API
    response = client.put(f"/voyage/update-{fake_voyage_id}", json=update_data)

    # Vérifier que l'API renvoie bien une erreur 404
    assert response.status_code == 404
    assert response.json()["detail"] == "demande de Voyage non trouvé"


# Test pour supprimer un voyage
def test_delete_voyage(monkeypatch):
    # Mocker la fonction du repository
    async def mock_delete_voyage(db, voyage_id):
        # Simuler la suppression réussie
        if str(voyage_id) == str(fake_voyage_id):
            return fake_voyage_json
        return None

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.voyage_repo.delete_voyage", mock_delete_voyage)

    # Faire l'appel API
    response = client.delete(f"/voyage/delete/{fake_voyage_id}")

    # Vérifier les résultats
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == str(fake_voyage_id)
    assert result["destination"] == fake_voyage_json["destination"]


# Test pour supprimer un voyage qui n'existe pas
def test_delete_voyage_not_found(monkeypatch):
    # Mocker la fonction du repository pour retourner None
    async def mock_delete_voyage_not_found(db, voyage_id):
        return None

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.voyage_repo.delete_voyage", mock_delete_voyage_not_found)

    # Faire l'appel API
    response = client.delete(f"/voyage/delete/{fake_voyage_id}")

    # Vérifier que l'API renvoie bien une erreur 404
    assert response.status_code == 404
    assert response.json()["detail"] == "demande de Voyage non trouvé"