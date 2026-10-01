from fastapi.testclient import TestClient

from demo.api import app

client = TestClient(app)


def test_demo_api():
    response = client.post("/api/cache-demo", json={"mode": "semantic"})
    assert response.status_code == 200
    assert response.json()["stats"]["semantic_hits"] >= 1
