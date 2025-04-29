import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.api.mission_controller import router  # Adapt path if needed

# Create test app and client
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Fake mission result
fake_mission = {
    "id": "4ed2447c-1f4d-49a1-9d4e-f332a277a28a",
    "type": "Nationale",
    "destination": "Tanger",
    "pays": "Maroc",
    "budgetPrevu": 7000,
    "details": "Congres",
    "ville": "Benguerrir",
    "createdAt": "2025-04-29T10:30:28.833312",
    "updatedAt": "2025-04-29T10:30:28.833323"
}

def test_get_missions(monkeypatch):
    async def mock_get_missions(db):
        return [fake_mission]

    monkeypatch.setattr("app.repositories.mission_repo.get_missions", mock_get_missions)

    headers = {
        "x-user-id": "ed734308-bf91-4f19-9f98-65da1cc964f6",
        "x-user-email": "test@example.com",
        "x-user-roles": "CG",
        "x-user-name": "John Doe"
    }

    response = client.get("mission/home", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["id"] == "ed734308-bf91-4f19-9f98-65da1cc964f6"
    assert len(data["missions"]) == 1

def test_create_mission(monkeypatch):
    async def mock_create_mission(db, mission):
        return fake_mission

    monkeypatch.setattr("app.repositories.mission_repo.create_mission", mock_create_mission)

    response = client.post("mission/createMission", json={
        "type": "Nationale",
        "destination": "Tanger",
        "pays": "Maroc",
        "budgetPrevu": 7000,
        "details": "Congres",
        "ville": "Benguerrir",
    })
    assert response.status_code == 200
    assert response.json()["type"] == "Nationale"

def test_update_mission(monkeypatch):
    async def mock_update_mission(db, mission_id, mission_update):
        return fake_mission

    monkeypatch.setattr("app.repositories.mission_repo.update_mission", mock_update_mission)

    response = client.put(f"mission/update-{fake_mission['id']}", json={
        "type": "Nationale",
        "destination": "Tanger",
        "pays": "Maroc",
        "budgetPrevu": 7000,
        "details": "Congres",
        "ville": "Benguerrir",
    })
    assert response.status_code == 200
    assert response.json()["type"] == "Nationale"

def test_delete_mission(monkeypatch):
    async def mock_delete_mission(db, mission_id):
        return fake_mission

    monkeypatch.setattr("app.repositories.mission_repo.delete_mission", mock_delete_mission)

    response = client.delete(f"mission/delete/{fake_mission['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == fake_mission["id"]
