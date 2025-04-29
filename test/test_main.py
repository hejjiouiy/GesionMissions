from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_missions():
    response = client.post('/home')
    assert response.status_code == 200
