import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from uuid import UUID
from app.api.ligne_budgetaire_controller import router
from app.models.enums.Enums import TypeFinancementEnum

# Create test app and client
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Fake ligne budgétaire data
fake_ligne_budgetaire = {
    "codeLigne": "string",
  "nom": "string",
  "exerciceBudgetaire": 0,
  "id": "ef399262-d1d6-4622-a375-b350825adec6"
}

def test_get_lignes_budgetaire(monkeypatch):
    async def mock_get_lignes_budgetaire(db):
        return [fake_ligne_budgetaire]

    monkeypatch.setattr("app.repositories.ligne_budgetaire_repo.get_lignes_budgetaire", mock_get_lignes_budgetaire)

    response = client.get("/ligne-budgetaire/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == fake_ligne_budgetaire["id"]

def test_create_ligne_budgetaire(monkeypatch):
    async def mock_create_ligne_budgetaire(db, ligne_budgetaire):
        return fake_ligne_budgetaire

    monkeypatch.setattr("app.repositories.ligne_budgetaire_repo.create_ligne_budgetaire", mock_create_ligne_budgetaire)

    response = client.post("/ligne-budgetaire/add", json={
        "codeLigne": "string",
  "nom": "string",
  "exerciceBudgetaire": 0,
  "id": "ef399262-d1d6-4622-a375-b350825adec6"
    })
    assert response.status_code == 200
    assert response.json()["nom"] == "string"

def test_update_ligne_budgetaire(monkeypatch):
    async def mock_update_ligne_budgetaire(db, ligne_budgetaire_id, ligne_budgetaire_update):
        return fake_ligne_budgetaire

    monkeypatch.setattr("app.repositories.ligne_budgetaire_repo.update_ligne_budgetaire", mock_update_ligne_budgetaire)

    response = client.put(f"/ligne-budgetaire/update-{fake_ligne_budgetaire['id']}", json={
        "codeLigne": "string",
  "nom": "string",
  "exerciceBudgetaire": 0,
  "id": "ef399262-d1d6-4622-a375-b350825adec6"
    })
    assert response.status_code == 200
    assert response.json()["id"] == fake_ligne_budgetaire["id"]
    assert response.json()["nom"] == "string"

def test_update_ligne_budgetaire_not_found(monkeypatch):
    async def mock_update_ligne_budgetaire_not_found(db, ligne_budgetaire_id, ligne_budgetaire_update):
        return None

    monkeypatch.setattr("app.repositories.ligne_budgetaire_repo.update_ligne_budgetaire", mock_update_ligne_budgetaire_not_found)

    response = client.put(f"/ligne-budgetaire/update-{fake_ligne_budgetaire['id']}", json={
        "codeLigne": "string",
  "nom": "string",
  "exerciceBudgetaire": 0,
  "id": "ef399262-d1d6-4622-a375-b350825adec6"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "LigneBudgetaire non trouvé"

def test_delete_ligne_budgetaire(monkeypatch):
    async def mock_delete_ligne_budgetaire(db, ligne_budgetaire_id):
        return fake_ligne_budgetaire

    monkeypatch.setattr("app.repositories.ligne_budgetaire_repo.delete_ligne_budgetaire", mock_delete_ligne_budgetaire)

    response = client.delete(f"/ligne-budgetaire/delete/{fake_ligne_budgetaire['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == fake_ligne_budgetaire["id"]

def test_delete_ligne_budgetaire_not_found(monkeypatch):
    async def mock_delete_ligne_budgetaire_not_found(db, ligne_budgetaire_id):
        return None

    monkeypatch.setattr("app.repositories.ligne_budgetaire_repo.delete_ligne_budgetaire", mock_delete_ligne_budgetaire_not_found)

    response = client.delete(f"/ligne-budgetaire/delete/{fake_ligne_budgetaire['id']}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ligne Budgetaire non trouvé"