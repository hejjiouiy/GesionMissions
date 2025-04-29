import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from uuid import UUID, uuid4
from datetime import date, datetime
import io
from app.api.rapport_controller import router

# Créer une application de test
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Données de test
fake_rapport_id = uuid4()
fake_ordre_mission_id = uuid4()
fake_user_id = uuid4()
fake_mission_id = uuid4()


# Classe mock pour simuler un ordre de mission
class MockOrdreMission:
    def __init__(self):
        self.id = fake_ordre_mission_id
        self.dateDebut = date(2025, 5, 1)
        self.dateFin = date(2025, 5, 10)
        self.user_id = fake_user_id
        self.mission_id = fake_mission_id
        self.createdAt = datetime(2025, 4, 29, 10, 30, 28, 833312)
        self.updatedAt = datetime(2025, 4, 29, 10, 30, 28, 833323)


# Classe mock pour simuler un rapport
class MockRapport:
    def __init__(self):
        self.id = fake_rapport_id
        self.contenu = "Rapport de la mission à Marrakech"
        self.ordre_mission_id = fake_ordre_mission_id
        self.ordre_mission = MockOrdreMission()
        self.fichier = b"Contenu du fichier PDF"
        self.createdAt = datetime(2025, 4, 29, 10, 30, 28, 833312)
        self.updatedAt = datetime(2025, 4, 29, 10, 30, 28, 833323)


# Données JSON de rapport pour les tests
fake_rapport_json = {
    "id": str(fake_rapport_id),
    "contenu": "Rapport de la mission à Marrakech",
    "ordre_mission_id": str(fake_ordre_mission_id),
    "createdAt": "2025-04-29T10:30:28.833312",
    "updatedAt": "2025-04-29T10:30:28.833323"
}


# Test pour récupérer tous les rapports
def test_get_rapports(monkeypatch):
    # Mock rapport à retourner par le repository
    mock_rapport = MockRapport()

    # Mocker la fonction du repository
    async def mock_get_rapports(db):
        return [mock_rapport]

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.rapport_mission_repo.get_rapports", mock_get_rapports)

    # Faire l'appel API
    response = client.get("/rapport/")

    # Vérifier les résultats
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(fake_rapport_id)
    assert data[0]["titre"] == "Rapport de la mission à Marrakech"
    assert data[0]["ordre_mission"]["id"] == str(fake_ordre_mission_id)
    assert data[0]["rapport"] == f"/rapport/{fake_rapport_id}/download"


# Test pour créer un rapport
def test_create_rapport(monkeypatch):
    # Données pour créer un nouveau rapport
    rapport_content = "Nouveau rapport de mission"

    # Mocker la fonction du repository
    async def mock_create_rapport(db, rapport_data, file_data):
        # Simuler l'enrichissement des données par la base de données
        return {
            "id": str(uuid4()),
            "contenu": rapport_data.contenu,
            "ordre_mission_id": str(rapport_data.ordre_mission_id),
            "createdAt": "2025-04-30T10:30:28.833312",
            "updatedAt": "2025-04-30T10:30:28.833312"
        }

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.rapport_mission_repo.create_rapport", mock_create_rapport)

    # Fichier de test
    test_file = io.BytesIO(b"Contenu du fichier PDF")

    # Faire l'appel API
    response = client.post(
        "/rapport/add",
        files={"file": ("rapport.pdf", test_file, "application/pdf")},
        data={
            "ordre_mission_id": str(fake_ordre_mission_id),
            "content": rapport_content
        }
    )

    # Vérifier les résultats
    assert response.status_code == 200
    result = response.json()
    assert "id" in result
    assert result["contenu"] == rapport_content
    assert result["ordre_mission_id"] == str(fake_ordre_mission_id)
    assert "createdAt" in result
    assert "updatedAt" in result


# Test pour mettre à jour un rapport
def test_update_rapport(monkeypatch):
    # Données de mise à jour
    update_data = {
        "contenu": "Rapport mis à jour",
        "ordre_mission_id": str(fake_ordre_mission_id)
    }

    # Mocker la fonction du repository
    async def mock_update_rapport(db, rapport_id, rapport_update):
        # Vérifier que l'ID correspond bien à notre rapport fictif
        if str(rapport_id) == str(fake_rapport_id):
            # Retourner les données mises à jour
            return {
                **fake_rapport_json,
                "contenu": rapport_update.contenu,
                "updatedAt": "2025-04-30T11:45:28.833323"
            }
        return None

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.rapport_mission_repo.update_rapport_mission", mock_update_rapport)

    # Faire l'appel API
    response = client.put(f"/rapport/update-{fake_rapport_id}", json=update_data)

    # Vérifier les résultats
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == str(fake_rapport_id)
    assert result["contenu"] == update_data["contenu"]
    assert result["ordre_mission_id"] == str(fake_ordre_mission_id)


# Test pour mettre à jour un rapport qui n'existe pas
def test_update_rapport_not_found(monkeypatch):
    # Données de mise à jour
    update_data = {
        "contenu": "Rapport mis à jour",
        "ordre_mission_id": str(fake_ordre_mission_id)
    }

    # Mocker la fonction du repository pour retourner None (rapport non trouvé)
    async def mock_update_rapport_not_found(db, rapport_id, rapport_update):
        return None

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.rapport_mission_repo.update_rapport_mission", mock_update_rapport_not_found)

    # Faire l'appel API
    response = client.put(f"/rapport/update-{fake_rapport_id}", json=update_data)

    # Vérifier que l'API renvoie bien une erreur 404
    assert response.status_code == 404
    assert response.json()["detail"] == "Rapport de mission non trouvé"


# Test pour supprimer un rapport
def test_delete_rapport(monkeypatch):
    # Mocker la fonction du repository
    async def mock_delete_rapport(db, rapport_id):
        # Simuler la suppression réussie
        if str(rapport_id) == str(fake_rapport_id):
            return fake_rapport_json
        return None

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.rapport_mission_repo.delete_rapport", mock_delete_rapport)

    # Faire l'appel API
    response = client.delete(f"/rapport/delete/{fake_rapport_id}")

    # Vérifier les résultats
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == str(fake_rapport_id)
    assert result["contenu"] == fake_rapport_json["contenu"]


# Test pour supprimer un rapport qui n'existe pas
def test_delete_rapport_not_found(monkeypatch):
    # Mocker la fonction du repository pour retourner None
    async def mock_delete_rapport_not_found(db, rapport_id):
        return None

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.rapport_mission_repo.delete_rapport", mock_delete_rapport_not_found)

    # Faire l'appel API
    response = client.delete(f"/rapport/delete/{fake_rapport_id}")

    # Vérifier que l'API renvoie bien une erreur 404
    assert response.status_code == 404
    assert response.json()["detail"] == "Rapport de mission non trouvé"