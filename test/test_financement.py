import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from uuid import UUID, uuid4
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.enums.Enums import TypeFinancementEnum

# Créer une application de test
app = FastAPI()

# Importer et inclure les routes de financement
from app.api.financement_controller import router

app.include_router(router)

# Créer un client de test
client = TestClient(app)

# Données factices pour les tests
fake_financement_id = uuid4()
fake_financement = {
    "type": TypeFinancementEnum.PERSONNEL,
    "details": "string",
    "devise": "MAD",
    "updatedAt": "2025-04-23T16:53:36.253754",
    "id": str(fake_financement_id),
    "valide": False,
    "createdAt": "2025-04-23T16:53:36.253744",
    "ordre_mission_id": "c7056413-6cf1-4bd6-ac71-45001fef5d81"
}


# Test pour récupérer tous les financements
def test_get_financements(monkeypatch):
    # Mocker la fonction get_financements du repository
    async def mock_get_financements(db):
        return [fake_financement]

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.financement_repo.get_financements", mock_get_financements)

    # Faire l'appel API
    response = client.get("/financement/")

    # Vérifier les résultats
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == fake_financement["id"]
    assert data[0]["details"] == fake_financement["details"]
    assert data[0]["type"] == fake_financement["type"]


# Test pour créer un financement
def test_create_financement(monkeypatch):
    # Données du nouveau financement à créer
    new_financement_data = {
        "type": TypeFinancementEnum.PERSONNEL,
    "details": "string",
    "devise": "MAD",
    "valide": False,
    "ordre_mission_id": "c7056413-6cf1-4bd6-ac71-45001fef5d81"
    }

    # Mocker la fonction create_financement du repository pour qu'elle retourne
    # une version enrichie des données envoyées (simulant l'ajout d'un ID, etc.)
    async def mock_create_financement(db, financement_data):
        # Simuler l'enrichissement des données par la base de données
        return {
            "id": str(uuid4()),
            **new_financement_data,
            "createdAt": "2025-04-29T10:30:28.833312",
            "updatedAt": "2025-04-29T10:30:28.833323"
        }

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.financement_repo.create_financement", mock_create_financement)

    # Faire l'appel API
    response = client.post("/financement/add", json=new_financement_data)

    # Vérifier les résultats
    assert response.status_code == 200
    result = response.json()
    assert "id" in result  # Vérifier qu'un ID a été généré
    assert result["type"] == new_financement_data["type"]
    assert result["details"] == new_financement_data["details"]
    assert "createdAt" in result
    assert "updatedAt" in result


# Test pour mettre à jour un financement
def test_update_financement(monkeypatch):
    # Données de mise à jour (ajustez selon votre modèle)
    update_data = {
        "type": "PERSONNEL",
        "details": "string",
        "devise": "MAD",
        "valide": False,
        "ordre_mission_id": "c7056413-6cf1-4bd6-ac71-45001fef5d81"
    }

    # Mock du repo
    async def mock_update_financement(db, financement_id, financement_update):
        return {**fake_financement, **update_data}

    monkeypatch.setattr("app.repositories.financement_repo.update_financement", mock_update_financement)

    # CORRECTION : Assurez-vous que l'URL est correcte
    # Vérifiez que le format correspond exactement à votre route
    response = client.put(f"/financement/update-{fake_financement_id}", json=update_data)

    # Debug
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

    assert response.status_code == 200


# Test pour mettre à jour un financement qui n'existe pas
def test_update_financement_not_found(monkeypatch):
    # Données de mise à jour
    update_data = {
        "type": TypeFinancementEnum.PERSONNEL,
    "details": "string",
    "devise": "MAD",
    "valide": False,
    "ordre_mission_id": "c7056413-6cf1-4bd6-ac71-45001fef5d81"
    }

    # Mocker la fonction update_financement pour qu'elle retourne None (financement non trouvé)
    async def mock_update_financement_not_found(db, financement_id, financement_update):
        return None

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.financement_repo.update_financement", mock_update_financement_not_found)

    # Faire l'appel API avec un ID existant mais qui retourne None (simulant "non trouvé")
    response = client.put(f"/financement/update-{fake_financement_id}", json=update_data)

    # Vérifier que l'API renvoie bien une erreur 404
    assert response.status_code == 404
    assert response.json()["detail"] == "Financement non trouvé"


# Test pour supprimer un financement
def test_delete_financement(monkeypatch):
    async def mock_delete_financement(db, financement_id):
        return fake_financement

    monkeypatch.setattr("app.repositories.financement_repo.delete_financement", mock_delete_financement)

    # CORRECTION : Assurez-vous que l'URL est correcte
    response = client.delete(f"/financement/delete/{fake_financement_id}")

    # Debug
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")

    assert response.status_code == 200

# Test pour supprimer un financement qui n'existe pas
def test_delete_financement_not_found(monkeypatch):
    # Mocker la fonction delete_financement pour qu'elle retourne None (financement non trouvé)
    async def mock_delete_financement_not_found(db, financement_id):
        return None

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.financement_repo.delete_financement", mock_delete_financement_not_found)

    # Faire l'appel API
    response = client.delete(f"/financement/delete/{fake_financement_id}")

    # Vérifier que l'API renvoie bien une erreur 404
    assert response.status_code == 404
    assert response.json()["detail"] == "demande de Financement non trouvé"