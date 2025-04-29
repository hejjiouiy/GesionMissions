import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from uuid import UUID, uuid4
from app.api.remboursement_controller import router
from app.models.enums.Enums import EtatMission

# Créer une application de test
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Données de test
fake_remboursement_id = uuid4()
fake_ordre_mission_id = uuid4()


fake_remboursement = {
    "id": str(fake_remboursement_id),
    "dateDemande": "2025-04-29",
    "financement_id": str(fake_ordre_mission_id),
    "etat": EtatMission.OUVERTE,
    "valide": False,
    "createdAt": "2025-04-23T16:53:36.287057",
    "updatedAt": "2025-04-23T16:53:36.287068"
}


# Test pour récupérer tous les remboursements
def test_get_remboursements(monkeypatch):
    # Mocker la fonction du repository
    async def mock_get_remboursements(db):
        return [fake_remboursement]

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.remboursement_repo.get_remboursements", mock_get_remboursements)

    # Faire l'appel API
    response = client.get("/remboursement/")

    # Vérifier les résultats
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == fake_remboursement["id"]
    assert data[0]["etat"] == fake_remboursement["etat"]
    assert data[0]["dateDemande"] == fake_remboursement["dateDemande"]


# Test pour créer un remboursement
def test_create_remboursement(monkeypatch):
    # Données du nouveau remboursement
    new_remboursement_data = {
        "dateDemande": "2025-04-29",
        "financement_id": str(fake_ordre_mission_id),
        "etat": EtatMission.OUVERTE,
        "valide": False,
    }

    # Mocker la fonction du repository
    async def mock_create_remboursement(db, remboursement_data):
        # Simuler l'enrichissement des données par la base de données
        return {
            "id": str(uuid4()),
            **new_remboursement_data,
            "createdAt": "2025-04-23T16:53:36.287057",
            "updatedAt": "2025-04-23T16:53:36.287068"
        }

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.remboursement_repo.create_remboursement", mock_create_remboursement)

    # Faire l'appel API
    response = client.post("/remboursement/add", json=new_remboursement_data)

    # Vérifier les résultats
    assert response.status_code == 200
    result = response.json()
    assert "id" in result
    assert result["etat"] == new_remboursement_data["etat"]
    assert result["financement_id"] == new_remboursement_data["financement_id"]
    assert result["dateDemande"] == new_remboursement_data["dateDemande"]
    assert "createdAt" in result
    assert "updatedAt" in result


# Test pour mettre à jour un remboursement
def test_update_remboursement(monkeypatch):
    # Données de mise à jour
    update_data = {
         "dateDemande": "2025-04-29",
        "financement_id": str(fake_ordre_mission_id),
        "etat": EtatMission.OUVERTE,
        "valide": False,
    }

    # Mocker la fonction du repository
    async def mock_update_remboursement(db, remboursement_id, remboursement_update):
        # Vérifier que l'ID correspond à notre remboursement fictif
        if str(remboursement_id) == fake_remboursement["id"]:
            # Retourner les données mises à jour
            return {
                **fake_remboursement,
                **update_data,
                 "createdAt": "2025-04-23T16:53:36.287057",
                "updatedAt": "2025-04-23T16:53:36.287068"
            }
        return None

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.remboursement_repo.update_remboursement", mock_update_remboursement)

    # Faire l'appel API
    response = client.put(f"/remboursement/update-{fake_remboursement_id}", json=update_data)

    # Vérifier les résultats
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == fake_remboursement["id"]
    assert result["financement_id"] == update_data["financement_id"]
    assert result["etat"] == update_data["etat"]
    assert result["dateDemande"] == update_data["dateDemande"]


# Test pour mettre à jour un remboursement qui n'existe pas
def test_update_remboursement_not_found(monkeypatch):
    # Données de mise à jour
    update_data = {
        "dateDemande": "2025-04-29",
        "financement_id": str(fake_ordre_mission_id),
        "etat": EtatMission.OUVERTE,
        "valide": False,
    }

    # Mocker la fonction du repository pour retourner None (remboursement non trouvé)
    async def mock_update_remboursement_not_found(db, remboursement_id, remboursement_update):
        return None

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.remboursement_repo.update_remboursement", mock_update_remboursement_not_found)

    # Faire l'appel API
    response = client.put(f"/remboursement/update-{fake_remboursement_id}", json=update_data)

    # Vérifier que l'API renvoie bien une erreur 404
    assert response.status_code == 404
    assert response.json()["detail"] == "demande de Remboursement non trouvé"


# Test pour supprimer un remboursement
def test_delete_remboursement(monkeypatch):
    # Mocker la fonction du repository
    async def mock_delete_remboursement(db, remboursement_id):
        # Simuler la suppression réussie
        if str(remboursement_id) == fake_remboursement["id"]:
            return fake_remboursement
        return None

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.remboursement_repo.delete_remboursement", mock_delete_remboursement)

    # Faire l'appel API
    response = client.delete(f"/remboursement/delete/{fake_remboursement_id}")

    # Vérifier les résultats
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == fake_remboursement["id"]
    assert result["etat"] == fake_remboursement["etat"]


# Test pour supprimer un remboursement qui n'existe pas
def test_delete_remboursement_not_found(monkeypatch):
    # Mocker la fonction du repository pour retourner None
    async def mock_delete_remboursement_not_found(db, remboursement_id):
        return None

    # Appliquer le mock
    monkeypatch.setattr("app.repositories.remboursement_repo.delete_remboursement", mock_delete_remboursement_not_found)

    # Faire l'appel API
    response = client.delete(f"/remboursement/delete/{fake_remboursement_id}")

    # Vérifier que l'API renvoie bien une erreur 404
    assert response.status_code == 404
    assert response.json()["detail"] == "demande de Remboursement non trouvé"